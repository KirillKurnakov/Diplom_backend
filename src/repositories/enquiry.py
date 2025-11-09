from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models import (
    Enquiry,
    EnquiryInputField,
    EnquiryTemplate,
    EnquiryTemplateBlock,
    InputField,
    InputFieldValue,
)
from utils.repository import AsyncSQLAlchemyRepository


class EnquiryRepository(AsyncSQLAlchemyRepository):
    model = Enquiry

    async def get_data_by_id(self, enquiry_id: int) -> Enquiry | None:
        stmt = (
            select(self.model)
            .where(self.model.id == enquiry_id)
            .options(
                selectinload(self.model.templates)
                .selectinload(EnquiryTemplate.blocks)
                .selectinload(EnquiryTemplateBlock.queries),
                selectinload(self.model.input_fields)
                .selectinload(EnquiryInputField.input_field)
                .selectinload(InputField.enquiry_associations),
                selectinload(self.model.input_fields)
                .selectinload(EnquiryInputField.values)
                .selectinload(InputFieldValue.user),
            )
        )
        result = await self._session.execute(stmt)
        result = result.scalars().all()
        return result


class EnquiryTemplateRepository(AsyncSQLAlchemyRepository):
    model = EnquiryTemplate


class EnquiryTemplateBlockRepository(AsyncSQLAlchemyRepository):
    model = EnquiryTemplateBlock
