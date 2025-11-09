from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from schemas.db import DbSchema


class QuerySchema(BaseModel):
    id: int
    title: Optional[str] = Field(...)
    description: Optional[str] = Field(...)
    sql_query: Optional[str] = Field(...)
    database_id: Optional[int] = Field(...)
    created_at: Optional[datetime] = Field(...)
    updated_at: Optional[datetime] = Field(...)
    version: Optional[int] = Field(...)
    user_id: Optional[int] = Field(...)
    code: Optional[str] = Field(...)
    database: Optional["DbSchema"] = Field(...)
