from utils.repository import AsyncSQLAlchemyRepository
from models.page_configuration.query import Query


class QueryRepository(AsyncSQLAlchemyRepository):
    model = Query
