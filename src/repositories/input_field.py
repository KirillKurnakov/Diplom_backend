from models.enquiry_temp.input_field import (
    EnquiryInputField,
    InputField,
    InputFieldValue,
)
from utils.repository import AsyncSQLAlchemyRepository


class InputFieldValueRepository(AsyncSQLAlchemyRepository):
    model = InputFieldValue


class InputFieldRepository(AsyncSQLAlchemyRepository):
    model = InputField


class EnquiryInputFieldRepository(AsyncSQLAlchemyRepository):
    model = EnquiryInputField
