from typing import Any, Dict, List, NotRequired, Optional, TypedDict, Union

from pydantic import BaseModel, Field, field_validator


class TemplaterRequestDump(TypedDict):
    user_id: NotRequired[int | None]
    filter_params: NotRequired[dict[str, list[str] | list[int]] | None]
    fields: dict[str, str]


class TemplaterRequest(BaseModel):
    user_id: Optional[int] = Field(default=None, description="ID пользователя")
    filter_params: Optional[Dict[str, Union[List[str], List[int]]]] = Field(
        default=None, description="Параметры фильтрации"
    )
    fields: Dict[str, str] = Field(
        default=None, description="Модификация полей"
    )

    @field_validator("fields", mode="before")
    @classmethod
    def make_fields_dict(cls, value: Any) -> Dict[str, str] | Dict:
        return value if isinstance(value, dict) else {}
