from utils.repository import AsyncSQLAlchemyRepository
from models.access_control import user


class UserRepository(AsyncSQLAlchemyRepository):
    model = user
