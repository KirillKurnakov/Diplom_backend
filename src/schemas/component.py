from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from schemas.component_template import ComponentTemplateSchema
from schemas.query import QuerySchema


class ComponentBase(BaseModel):
    title: str = Field(...)
    description: str = Field(...)
    styles: Optional[str] = Field(default=None)
    visible_empty_data: Optional[bool] = Field(default=None)
    data: Optional[str] = Field(default=None)
    use_filter: Optional[bool] = Field(default=None)
    options: Optional[str] = Field(default=None)
    loader: Optional[bool] = Field(default=None)


# Дополнительные поля
class ExtraMetaFields_1(BaseModel):
    user_id: Optional[int] = Field(...)
    error_id: Optional[int] = Field(default=1)


# Дополнительные поля
class ExtraMetaFields_2(BaseModel):
    with_api_data: Optional[bool] = Field(default=None, alias="withApiData")
    order: Optional[int] = Field(default=None)
    parent_component_id: Optional[int] = Field(default=None)


class ComponentIndependentSchema(ComponentBase, ExtraMetaFields_1):
    id: int = Field(...)
    component: Optional[str] = Field(...)
    # Переопределение типа из мейн класса
    options: Optional[dict] = Field(default=None)
    page_id: Optional[int] = Field(...)
    withApiData: Optional[bool] = Field(default=None)
    component_template: Optional["ComponentTemplateSchema"] = Field(default=None)
    uid: str = Field(...)


class ComponentAdminSchema(ComponentBase, ExtraMetaFields_1):
    id: int = Field(...)
    component: Optional[str] = Field(...)
    # Переопределение типа из мейн класса
    options: Optional[dict] = Field(default=None)
    page_id: Optional[int] = Field(...)
    withApiData: Optional[bool] = Field(default=None)
    component_template_id: Optional[int] = Field(default=None)
    uid: str = Field(...)
    parent_component_id: Optional[int] = Field(...)
    order: Optional[int] = Field(...)
    created_at: Optional[datetime] = Field(...)
    updated_at: Optional[datetime] = Field(...)
    version: Optional[int] = Field(...)


class ComponentPageSchema(ComponentBase, ExtraMetaFields_1):
    id: int = Field(...)
    component: Optional[str] = Field(...)
    page_id: Optional[int] = Field(...)
    component_template_id: Optional[int] = Field(...)
    parent_component_id: Optional[int] = Field(...)
    withApiData: Optional[bool] = Field(default=None)
    order: Optional[int] = Field(...)
    created_at: Optional[datetime] = Field(...)
    updated_at: Optional[datetime] = Field(...)
    version: Optional[int] = Field(...)
    component_template: Optional["ComponentTemplateSchema"] = Field(default=None)
    uid: str = Field(...)
    children: Optional[List["ComponentPageSchema"]] = Field(...)
    query: list = Field(default=[])
    formatters: list = Field(default=[])
    filters: list = Field(default=[])
    # Переопределение типа из мейн класса
    options: Optional[dict] = Field(default=None)


class ComponentAnswerSchema(ComponentBase):
    component: str = Field(...)
    withApiData: bool = Field(...)
    error_id: int = Field(...)
    uid: str = Field(...)
    # Переопределение типа из мейн класса
    options: Optional[dict] = Field(default=None)


class ComponentWithChildren(ComponentAnswerSchema):
    children: Optional[List["ComponentWithChildren"]] = Field(...)


# Схема компонента, которая может прийти с фронта
class ComponentFrontSchema(ComponentBase):
    component: str = Field(...)  # Обязательно

    # Поля по желанию
    withApiData: Optional[bool] = Field(default=None)
    component_template_id: Optional[int] = Field(default=None)

    # Переопределение типа из мейн класса
    options: Optional[dict] = Field(default=None)

    # Паттерн для проверки передаваемого uid на момент 04.10.2024
    uid: Optional[str] = Field(pattern=r"^[A-Z][a-zA-Z0-9]*_[0-9]+$", default=None)

    # список выпердышей таких же, как родитель
    children: Optional[List["ComponentFrontSchema"]] = Field(default=None)


# Схема для записи компонента в БД
class ComponentCreateSchema(ComponentBase, ExtraMetaFields_1, ExtraMetaFields_2):
    # Обязательные поля
    page_id: int = Field(...)
    component_template_id: int = Field(...)


class ComponentCreateResponseSchema(ComponentBase, ExtraMetaFields_1):
    id: int = Field(...)
    with_api_data: Optional[bool] = Field(default=None)
    order: Optional[int] = Field(default=None)
    parent_component_id: Optional[int] = Field(default=None)


# Cхема для обновления комопнета в БД
class ComponentUpdateSchema(ComponentBase, ExtraMetaFields_1, ExtraMetaFields_2):
    pass


# Схема для модели компонента, возвращающего данные
class ComponentDataSchema(BaseModel):
    id: int = Field(...)
    component_type: str = Field(default=None)
    query: QuerySchema = Field(...)
    formatters: list = Field(...)
    filters: list = Field(...)
