import time
from datetime import datetime
from typing import Any, Dict, List

from more_itertools import always_iterable
from sqlalchemy import MetaData, Table, and_, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from db.db import get_session_maker
from exceptions import DataNotFoundError
from models import Db, InputFieldValue, Query
from schemas.templater import TemplaterRequestDump
from utils.logger import GLOBAL_LOGGER
from utils.unitofwork import IUnitOfWork


class ExternalQueryExecutor:
    """Класс для обработки запросов и получения данных из баз данных."""

    def __init__(self):
        """Инициализирует обработчик запросов."""
        self._session_factories_cache: Dict[int, async_sessionmaker] = {}

    async def _get_or_create_session_factory(
        self, uow: IUnitOfWork, db_id: int
    ) -> async_sessionmaker:
        """Получает фабрику сессий из кэша.

        Функция получает фабрику сессий для `db_id` из кэша. Если ее нет,
        создает и кэширует.

        Args:
            uow (IUnitOfWork): Unit of Work для доступа к базам данных.
            db_id (int): ID базы данных для которой нужно проверить наличие
            сессии.

        Returns:
            async_sessionmaker: Функция возвращает объект `async_sessionmaker`.

        Raises:
            ValueError: Выбрасывает исключение, если данных для подключения к
            базе данных с `db_id` не найдено.
        """
        if db_id not in self._session_factories_cache:
            GLOBAL_LOGGER.debug(
                f"Фабрика сессий для db_id={db_id} не найдена в кэше.\
            Создаем новую..."
            )
            db_connection_details = await self._get_db_details(uow, db_id)
            if not db_connection_details:
                raise ValueError(
                    f"Не найдены данные подключения к database_id: {db_id}"
                )

            self._session_factories_cache[db_id] = (
                self._create_external_session_factory(db_connection_details)
            )

        return self._session_factories_cache[db_id]

    async def _execute(
        self, uow: IUnitOfWork, query: Query, filter_params: Dict
    ) -> List[Dict]:
        """Подключается к внешней БД и выполняет запрос.

        Функция подключается к базе данных и выполняет несколько запросов
        для получения необходимых данных.

        Args:
            uow (IUnitOfWork): Unit of Work для доступа к базам данных.
            query (Query): Объект `query` являющийся отражением таблицы
            полученный посредством `sqlalchemy`.
            filter_params (Dict): Параметры для фильтрации данных в запросах.

        Returns:
            List[Dict]: Функция возвращает результат выполненного запроса.

        Raises:
            DataNotFoundError: Подсказывает для какого запроса и с какими
            параметрами не найдены данные.
        """
        external_session_factory = await self._get_or_create_session_factory(
            uow, query.database_id
        )

        async with external_session_factory() as session:
            view = await self._get_view_table(session, query)
            stmt = select(view)
            stmt = await self._apply_filters(
                stmt, view, {"inn": filter_params["inn"][0]}
            )

            result = await session.execute(stmt)
            view_results = result.mappings().all()
            if not view_results:
                raise DataNotFoundError(
                    f"Данные для query_id: {query.id} с параметрами\
                          {filter_params} не найдены - {view_results=}"
                )
            else:
                GLOBAL_LOGGER.debug(
                    f"Все удачно для {query.id} с параметрами\
                          {filter_params} - {view_results=}"
                )
            return view_results

    async def _get_db_details(self, uow: IUnitOfWork, db_id: int) -> Db | None:
        """Получает объект `Db` из основной базы.

        Args:
            uow (IUnitOfWork): Unit of Work для доступа к базам данных.
            db_id (int): ID базы данных для которой нужно получить объект `Db`.

        Returns:
            Db | None: Функция возвращает искомый объект или ничего, в
            зависимости от результата выполнения запроса.

        """
        return await uow.dbs.find_one(id=db_id)

    def _create_external_session_factory(self, db: Db) -> async_sessionmaker:
        """Создает новую фабрику сессий.

        Args:
            db (Db): Объект `Db` с информацией о подключении к базе данных.

        Returns:
            async_sessionmaker: Функция возвращает сессию `async_sessionmaker`.

        """
        conn_params = {
            "drivername": db.dbms,
            "host": db.host,
            "port": db.port,
            "database": db.name,
            "username": db.username,
            "password": db.password,
        }
        return get_session_maker(conn_params)

    async def _get_view_table(
        self, session: async_sessionmaker, query: Query
    ) -> Table:
        """Получает представление базы данных.

        Args:
            session (async_sessionmaker): Объект асинхронной сессии.
            query (Query): Объект запроса.

        Returns:
            Table: Функция возвращает объект `Table`, предстваляющий отражение
            представления из базы данных.

        """
        view_name = f"query_{query.id}" if query.code is None else query.code
        return await session.run_sync(
            lambda sync_session: Table(
                view_name,
                MetaData(),
                schema="cbias_spravki",
                autoload_with=sync_session.get_bind(),
            )
        )

    async def _apply_filters(
        self, stmt: select, view: Table, params: Dict
    ) -> select:
        """Применяет фильтры к запросу.

        Args:
            stmt (select): Изначальный запрос.
            view (Table): Таблица - представление.
            params (Dict): Параметры фильтрации.

        Returns:
            select: Функция возвращает запрос с добавленными фильтрами.

        """
        filters = []
        for key, value in params.items():
            if hasattr(view.c, key):
                column = getattr(view.c, key)
                converted_values = self._convert_value(value, column.type)
                filters.append(column.in_(converted_values))

        return stmt.where(and_(*filters)) if filters else stmt

    def _convert_value(self, value: Any, column_type: Any) -> List[Any]:
        """Конвертирует значения фильтрации.

        Args:
            value (Any): Фильтр.
            column_type (Any): Тип значения колонки.

        Returns:
            List[Any]: Фунция возвращает сконвертированный объект.

        """
        iterable_value = always_iterable(value, base_type=(str, list))
        return list(map(column_type.python_type, iterable_value))

    async def get_data(
        self,
        enquiry_id: int,
        uow: IUnitOfWork,
        templater_params: TemplaterRequestDump,
        template_type: str,
        target_dict: dict,
        template_file_path: str,
        is_pdf: bool = False,
    ) -> str:
        """Получает данные по запросам.

        Функция получает данные согласно запросам для объекта `enquiry`.

        Args:
            enquiry_id (int): ID справки `enquiry`.
            uow (IUnitOfWork): Unit of Work для доступа к базам данных.
            templater_params (TemplaterRequestDump): Параметры фильтрации
            запросов.
            template_type (str): Тип шаблона для справки.
            target_dict (dict): Словарь для модификации.
            template_file_path (str): Путь до директории с шаблоном справки.
            is_pdf (bool, optional): Флаг, определяющий тип генеруемой справки.
            Defaults to False.

        Returns:
            str: Функция возвращает путь до шаблона справки.

        """
        enquiry = await uow.enquiries.get_data_by_id(enquiry_id)
        for template in enquiry[0].templates:
            if template.template_file_path.split(".")[1] == template_type:
                if (is_pdf and "pdf" not in template.template_file_path) or (
                    not is_pdf and "pdf" in template.template_file_path
                ):
                    continue
                template_file_path = template.template_file_path
                for block in template.blocks:
                    for query in block.queries:
                        try:
                            view_data = await self._execute(
                                uow, query, templater_params["filter_params"]
                            )
                            target_dict[query.id] = view_data
                        except DataNotFoundError as e:
                            GLOBAL_LOGGER.debug(f"{e}, время: {time.ctime()}")
        return template_file_path

    async def get_template_info(
        self, enquiry_id: int, uow: IUnitOfWork
    ) -> List:
        """Получает доступные форматы шаблонов.

        Args:
            enquiry_id (int): ID справки для получения шаблонов.
            uow (IUnitOfWork): Unit of Work для доступа к базам данных.

        Returns:
            List: Функция возвращает список доступных форматов шаблонов.

        """
        templates_types = list()
        fields = list()
        enquiry = await uow.enquiries.get_data_by_id(enquiry_id)
        if not enquiry:
            return []
        for template in enquiry[0].templates:
            if (
                template.template_file_path.split(".")[1]
                not in templates_types
            ):
                templates_types.append(
                    template.template_file_path.split(".")[1]
                )
        for input_field_index in enquiry[0].input_fields:
            fields.append(
                {
                    "title": input_field_index.input_field.title,
                    "field_key": input_field_index.input_field.field_key,
                    "field_type": input_field_index.input_field.field_type,
                    "values": [
                        {
                            "id": field.id,
                            "value": field.input_field_value,
                            "user_fio": f"{field.user.data[0].last_name} "
                            f"{field.user.data[0].name} "
                            f"{field.user.data[0].middle_name}",
                            "created_at": field.created_at.strftime(
                                "%d.%m.%Y"
                            ),
                        }
                        for field in input_field_index.relevant_values
                        if not field.is_deleted
                    ],
                }
            )
        return {"formats": templates_types, "fields": fields}

    async def delete_input_field_value_soft(
        self, enquiry_id: int, uow: IUnitOfWork, input_field_value_id: int
    ) -> bool:
        """Выполняет "мягкое" удаление значения поля.

        Находит значение по его ID, проверяет, что оно принадлежит
        указанной справке (enquiry_id), и устанавливает флаг is_deleted=True.

        Args:
            enquiry_id (int): ID справки для проверки принадлежности.
            uow (IUnitOfWork): Unit of Work для доступа к данным.
            input_field_value_id (int): ID удаляемого значения.

        Returns:
            bool: True, если удаление прошло успешно, False в противном случае.
        """
        value_to_delete = await uow.input_field_values.find_one(
            id=input_field_value_id
        )
        if not value_to_delete:
            GLOBAL_LOGGER.warning(
                f"Значение с ID {input_field_value_id} не найдено."
            )
            return False
        if value_to_delete.enquiry_input_field.enquiry_id != enquiry_id:
            GLOBAL_LOGGER.error(
                f"Попытка удалить значение {input_field_value_id}, "
                f"которое не принадлежит справке {enquiry_id}."
            )
            return False
        if value_to_delete.is_deleted:
            return True
        value_to_delete.is_deleted = True
        await uow.commit()
        GLOBAL_LOGGER.debug(
            f"Значение {input_field_value_id} было мягко удалено."
        )
        return True

    async def add_input_field_value(
        self,
        enquiry_id: int,
        uow: IUnitOfWork,
        fields: Dict[str, str],
        user_id: int | None,
    ) -> None:
        """Добавление значения поля в БД.

        Args:
            enquiry_id (int): ID справки для которой добавляется поле.
            uow (IUnitOfWork): UOW для подключения к БД.
            fields (Dict[str, str]): Словарь полей:
                ключ - `input_field.field_key`,
                значение - `input_field_value.input_field_value`.
            user_id (int): ID пользователя, создающего запись.

        Returns:
            None: Функция работает с БД.

        """
        ((field_key, field_value),) = fields.items()
        enquiry = await uow.enquiries.get_data_by_id(enquiry_id)
        for input_field_index in enquiry[0].input_fields:
            if field_key != input_field_index.input_field.field_key:
                GLOBAL_LOGGER.debug(
                    f"Поля {field_key} нет в справке с id={enquiry_id}"
                )
                continue
            field_value_exists = any(
                record.input_field_value == field_value
                for record in input_field_index.values
            )
            if not field_value_exists:
                field_data = {
                    "enquiry_input_field_id": input_field_index.id,
                    "input_field_value": field_value,
                    "user_id": user_id,
                    "created_at": datetime.now(),
                }
                new_input_field_value = InputFieldValue(**field_data)
                uow._session.add(new_input_field_value)
        GLOBAL_LOGGER.debug(
            f"Попытка загрузить значение {field_value} для "
            f"поля {field_key} в БД"
        )
        await uow.commit()
        GLOBAL_LOGGER.debug(
            f"Значение {field_value} для поля {field_key} ЗАГРУЖЕНО в БД"
        )
