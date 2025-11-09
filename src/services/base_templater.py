import re
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import cast

from schemas.templater import TemplaterRequest, TemplaterRequestDump
from utils.logger import GLOBAL_LOGGER
from utils.unitofwork import IUnitOfWork
from utils.utils import ExternalQueryExecutor


class BaseTemplater(ABC):
    """Абстрактный базовый класс для всех шаблонизаторов."""

    def __init__(
        self,
        uow: IUnitOfWork,
        enquiry_id: int,
        templater_params: TemplaterRequest,
        template_type: str,
    ):
        self.uow = uow
        self.enquiry_id = enquiry_id
        self.templater_params: TemplaterRequestDump = cast(
            TemplaterRequestDump, templater_params.model_dump()
        )
        self.fields = self.templater_params["fields"]
        self.template_type = template_type

        self.raw_query_responses: dict[
            int, list[dict[str, str | int | Decimal | None]]
        ] = {}
        self.query_responses: dict[
            int, list[dict[str, str | int | Decimal]]
        ] = {}
        self.template_file_path = ""
        self.query_executor = ExternalQueryExecutor()

        # ЕДИНЫЙ КОМБИНИРОВАННЫЙ ПАТТЕРН ДЛЯ ВСЕХ
        self.combined_pattern = re.compile(
            r"\{\{"
            r"(?:"
            r"(?P<query_id>\d+):(?P<row_index>\d+);(?P<column_name>\w+)"
            # {{query_id:index;column}}
            r"|"
            r"(?P<field_name>\w+)"  # {{field}}
            # Сюда можно будет добавлять новые типы плейсхолдеров через "|"
            r")"
            r"\}\}"
        )

    async def _fetch_and_prepare_data(self, is_pdf: bool = False) -> None:
        """Общий метод для получения и подготовки данных.

        Args:
            is_pdf (bool, optional): Проверка на генерацию отчета в `.pdf`.
              Defaults to False.

        Returns:
            None: Функция работает с `self`.

        """
        self.template_file_path = await self.query_executor.get_data(
            self.enquiry_id,
            self.uow,
            self.templater_params,
            self.template_type,
            self.raw_query_responses,
            self.template_file_path,
            is_pdf,
        )

        for resp_id, response in self.raw_query_responses.items():
            self.query_responses[resp_id] = []
            for row in response:
                dict_row = dict(row)
                for key, value in dict_row.items():
                    if value is None:
                        dict_row[key] = ""
                processed_row = cast(dict[str, str | int | Decimal], dict_row)
                self.query_responses[resp_id].append(processed_row)
        GLOBAL_LOGGER.info(
            f"Finished queries for {self.template_type}, responses prepared."
        )

    async def _placeholder_replacer(self, match: re.Match) -> str:
        """ЕДИНЫЙ обработчик для всех типов плейсхолдеров.

        Args:
            match (re.Match): Найденные плейсхолдеры.

        Returns:
            str: Функция возвращает значение из словаря с данными.

        """
        if match.group("query_id"):
            query_id = int(match.group("query_id"))
            row_index = int(match.group("row_index"))
            column_name = match.group("column_name")
            if (
                query_id in self.query_responses
                and len(self.query_responses[query_id]) > row_index
            ):
                return str(
                    self.query_responses[query_id][row_index].get(
                        column_name, ""
                    )
                )
            return ""

        elif match.group("field_name"):
            field_name = match.group("field_name")
            if self.fields.get(field_name, ""):
                await self.query_executor.add_input_field_value(
                    self.enquiry_id,
                    self.uow,
                    {field_name: self.templater_params["fields"][field_name]},
                    self.templater_params["user_id"],
                )
                return str(self.fields.get(field_name, ""))
            else:
                return ""

        return match.group(0)

    # Эти методы должны будут реализовать дочерние классы
    @abstractmethod
    def _load_template(self): ...

    @abstractmethod
    async def _replace_single_placeholders(self): ...

    @abstractmethod
    def _process_dynamic_tables(self): ...

    @abstractmethod
    def _add_footer_info(self): ...

    @abstractmethod
    def _save_and_cleanup(self) -> str: ...

    # Главный оркестрирующий метод
    async def generate_report_from_template(self, is_pdf: bool = False) -> str:
        """Инициилизирует генерацию справки по шаблону.

        Основная функция модуля. Генерирует справку с помощью функций в модуле,
        предварительно обработав данные полученные из баз данных.


        Args:
            is_pdf (bool, optional): Определяет возможный формат.
                Defaults to False.

        Returns:
            str: Функция возращает путь к сгенерованной справке.

        """
        async with self.uow:
            await self._fetch_and_prepare_data(is_pdf)
            self._load_template()

            await self._replace_single_placeholders()
            self._process_dynamic_tables()

            self._add_footer_info()

            return self._save_and_cleanup()
