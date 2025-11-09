from utils.repository import AsyncSQLAlchemyRepository
from models.page_configuration import page


class PageRepository(AsyncSQLAlchemyRepository):
    model = page
