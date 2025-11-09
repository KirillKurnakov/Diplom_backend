import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_filename():
    """
    Функция для определения пути до файла с виртуальными пременными.
    В зависимости от файловой структуры стоит подкорретикровать.
    """

    # Получаем путь до файла из установленной глобальной переменной.
    runtime_env = os.getenv("ENV")
    dotenv_filename = f"src/.env.{runtime_env}" if runtime_env else "src/.env"
    return dotenv_filename


class Settings(BaseSettings):
    """
    Схема для установки переменных из .env
    """

    app_name: str
    app_description: str
    reload: bool = False

    # Конфиг подключения к системной базе данных
    DB_HOST: str
    DB_NAME: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_DRIVER_NAME: str
    LOG_MESSAGE_FORMAT: str
    LOG_DATETIME_FORMAT: str
    LOG_TO_CONSOLE: bool = True

    model_config = SettingsConfigDict(env_file=get_env_filename(), extra="ignore")


# Создание кешированной функции. Ее и надо импортировать в другие файлы
@lru_cache
def get_variables():
    return Settings()
