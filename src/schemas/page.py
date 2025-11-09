from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from transliterate import translit

from schemas.component import ComponentWithChildren, ComponentFrontSchema


# Схема для всех запросов с кодом
class PageByCodeDefaulltSchema(BaseModel):
    code: str = Field(...)


# Схема для использования условной атомарности
class PageBase(PageByCodeDefaulltSchema):
    title: str = Field(...)
    description: str = Field(...)


# Схема ответа с бека
class PageStructResponseSchema(PageBase, BaseModel):
    breadcrumbs: list[dict] = Field(...)
    # modal: Optional["ComponentDifficultSchema"] = Field(...)
    config: Optional[List["ComponentWithChildren"]] = Field(default=None)

    def dict(self):
        return super().model_dump_json(by_alias=True)


class PageSchema(PageStructResponseSchema):
    id: int = Field(...)
    parent_id: Optional[int] = Field(...)
    created_at: datetime = Field(...)
    updated_at: datetime = Field(...)
    version: int = Field(...)
    user_id: int = Field(...)
    created_by: int = Field(...)


# Схема страницы приходящей с фронта
class PageFrontStructSchema(PageBase):
    parent_id: Optional[str] = Field(
        alias="parent_code",
        default=None
    )
    config: Optional[List["ComponentFrontSchema"]] = Field(default=None)

    @field_validator('code', mode="before")
    def translit_code(cls, code) -> str:
        try:
            return translit(code, 'ru', reversed=True)
        except Exception:
            return code


# Схема для записи в БД
class PageCreateSchema(PageBase, BaseModel):
    parent_id: Optional[int] = Field(default=None)
    user_id: int = Field(default=None)
    created_by: int = Field(default=None)
