from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base
from models.system_configuration.associations import (
    user_user_data_association_table,
)

if TYPE_CHECKING:
    from .user import User


class UserData(Base):
    __tablename__ = "user_data"
    __table_args__ = {"schema": "access_control"}

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String)
    middle_name: Mapped[str | None] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    work_phone_number: Mapped[str] = mapped_column(String)
    personal_phone_number: Mapped[str | None] = mapped_column(String)
    changed_by: Mapped[int | None] = mapped_column(
        ForeignKey("access_control.user.id")
    )

    users: Mapped[List["User"]] = relationship(
        secondary=user_user_data_association_table,
        back_populates="data",
        lazy="selectin",
    )
