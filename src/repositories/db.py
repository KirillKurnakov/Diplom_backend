from utils.repository import AsyncSQLAlchemyRepository
from models.system_configuration.db import Db


class DBRepository(AsyncSQLAlchemyRepository):
    model = Db
