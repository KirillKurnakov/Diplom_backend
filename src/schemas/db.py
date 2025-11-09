from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, AliasChoices


class DbSchema(BaseModel):
    id: Optional[int] = Field(...)
    dbms: Optional[str] = Field(
        ...,
        validation_alias=AliasChoices("drivername", "dbms"),
        serialization_alias="drivername",
    )
    host: Optional[str] = Field(...)
    port: Optional[str] = Field(...)
    name: Optional[str] = Field(
        ...,
        validation_alias=AliasChoices("database", "name"),
        serialization_alias="database",
    )
    username: Optional[str] = Field(...)
    password: Optional[str] = Field(...)
    description: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    version: Optional[int] = Field(default=None)
    user_id: Optional[int] = Field(default=None)
