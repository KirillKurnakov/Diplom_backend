from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base
from models.system_configuration.associations import (
    user_user_data_association_table,
)

if TYPE_CHECKING:
    from models.system_configuration.enquiry import Enquiry

    from .user_data import UserData


class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "access_control"}

    id: Mapped[int] = mapped_column(primary_key=True)
    uid: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    status_id: Mapped[int] = mapped_column(
        ForeignKey("access_control.user_status.id"), nullable=False
    )
    last_visit: Mapped[datetime | None]
    auth_token: Mapped[str] = mapped_column(nullable=False)
    password_reset_token: Mapped[str] = mapped_column(nullable=False)
    verification_token: Mapped[str] = mapped_column(nullable=False)
    org_id: Mapped[int] = mapped_column(
        ForeignKey("fact_tables.organization.id")
    )
    position: Mapped[str] = mapped_column(nullable=False)

    enquiries: Mapped[List["Enquiry"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    enquiry_templates: Mapped[List["EnquiryTemplate"]] = relationship(
        back_populates="user", lazy="selectin"
    )
    enquiry_template_blocks: Mapped[List["EnquiryTemplateBlock"]] = (
        relationship(back_populates="user", lazy="selectin")
    )

    data: Mapped[List["UserData"]] = relationship(
        secondary=user_user_data_association_table,
        back_populates="users",
        lazy="selectin",
    )
