from abc import ABC, abstractmethod

from db.db import get_main_session_maker
from repositories.db import DBRepository
from repositories.enquiry import (
    EnquiryRepository,
    EnquiryTemplateBlockRepository,
    EnquiryTemplateRepository,
)
from repositories.input_field import InputFieldValueRepository
from repositories.page import PageRepository
from repositories.query import QueryRepository
from repositories.user import UserRepository


class IUnitOfWork(ABC):
    users: UserRepository
    pages: PageRepository
    queries: QueryRepository
    dbs: DBRepository
    enquiries: EnquiryRepository
    enquiry_templates: EnquiryTemplateRepository
    enquiry_template_blocks: EnquiryTemplateBlockRepository
    input_field_values: InputFieldValueRepository

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, *args): ...

    @abstractmethod
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, *args): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork:
    def __init__(self):
        session_factory = get_main_session_maker()
        self._session = session_factory()

    async def __aenter__(self):
        self.users = UserRepository(self._session)
        self.pages = PageRepository(self._session)
        self.queries = QueryRepository(self._session)
        self.dbs = DBRepository(self._session)
        self.enquiries = EnquiryRepository(self._session)
        self.enquiry_templates = EnquiryTemplateRepository(self._session)
        self.enquiry_template_blocks = EnquiryTemplateBlockRepository(
            self._session
        )
        self.input_field_values = InputFieldValueRepository(self._session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
