from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ComponentTemplateSchema(BaseModel):
    id: int = Field(...)
    component_type_id: Optional[int] = Field(default=None)
    created_at: Optional[datetime] = Field(...)
    updated_at: Optional[datetime] = Field(...)
    version: Optional[int] = Field(...)
    user_id: Optional[int] = Field(...)
    title: Optional[str] = Field(...)
    styles: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    with_api_data: Optional[bool] = Field(default=None)
    loader: Optional[bool] = Field(default=None)
    visible_empty_data: Optional[bool] = Field(default=None)
    options: Optional[str] = Field(default=None)
    user_filter: Optional[bool] = Field(default=None)
    error_id: Optional[int] = Field(default=None)
    is_default: Optional[bool] = Field(default=None)
