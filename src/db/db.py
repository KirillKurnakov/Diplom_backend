from typing import Optional

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from loaded_env import get_variables
from utils.logger import GLOBAL_LOGGER

ENGINE_ARGS = dict(pool_size=50, pool_pre_ping=True, pool_recycle=3600)


_main_async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None


def get_main_session_maker() -> async_sessionmaker[AsyncSession] | None:
    """Получение фабрики сессий(лениво).

    Args:
        None

    Returns:
        async_session_maker (async_sessionmaker[AsyncSession]): Фабрика сессий
          для подключения к СУБД
    """
    global _main_async_session_maker

    if _main_async_session_maker is None:
        GLOBAL_LOGGER.debug(
            "Первый вызов get_async_session_maker, создаем engine"
            " и session maker..."
        )
        async_conn_params = {
            "drivername": get_variables().DB_DRIVER_NAME,
            "host": get_variables().DB_HOST,
            "port": get_variables().DB_PORT,
            "database": get_variables().DB_NAME,
            "username": get_variables().DB_USER,
            "password": get_variables().DB_PASS,
        }

        async_url = URL.create(**async_conn_params)
        async_engine = create_async_engine(async_url, **ENGINE_ARGS)
        _main_async_session_maker = async_sessionmaker(
            async_engine, expire_on_commit=False
        )
        GLOBAL_LOGGER.debug("Подключение к основной БД установлено")

    return _main_async_session_maker


def get_session_maker(
    conn_params: dict[str, str],
) -> async_sessionmaker[AsyncSession] | None:
    """Получение фабрики сессий.

    Args:
        ENGINE_ARGS (_type_): _description_
        conn_params (dict[str, str]): Параметры подключения к СУБД

    Returns:
        async_session_maker (async_sessionmaker[AsyncSession]): Фабрика сессий
          для подключения к СУБД
    """
    try:
        GLOBAL_LOGGER.debug("Получение сессии для стороннего подключения")
        async_url = URL.create(**conn_params)
        async_engine = create_async_engine(async_url, **ENGINE_ARGS)
        async_session_maker = async_sessionmaker(
            async_engine, expire_on_commit=False, autoflush=True
        )
    except Exception as e:
        GLOBAL_LOGGER.error(
            f"При подключении к базе данных {conn_params.get('host')}:{conn_params.get('port')} произошла ошибка!{e=}"
        )
        return
    else:
        GLOBAL_LOGGER.debug(
            f"Подключение к базе данных {conn_params.get('host')}:{conn_params.get('port')} установлено!"
        )

    return async_session_maker


class Base(DeclarativeBase):
    pass
