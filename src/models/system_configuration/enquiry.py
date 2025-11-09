from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base
from models.system_configuration.associations import (
    enquiry_enquiry_template_table,
)

if TYPE_CHECKING:
    from access_control.user import User
    from enquiry_temp.input_field import EnquiryInputField
    from enquiry_template import EnquiryTemplate


class Enquiry(Base):
    __tablename__ = "enquiry"
    __table_args__ = {"schema": "system_configuration"}

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=text("now()")
    )
    version: Mapped[int] = mapped_column(
        nullable=False, server_default=text("1")
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("access_control.user.id"), nullable=False
    )

    user: Mapped["User"] = relationship(
        back_populates="enquiries", lazy="selectin"
    )

    templates: Mapped[List["EnquiryTemplate"]] = relationship(
        secondary=enquiry_enquiry_template_table,
        back_populates="enquiries",
        lazy="selectin",
    )

    input_fields: Mapped[List["EnquiryInputField"]] = relationship(
        back_populates="enquiry", cascade="all, delete-orphan", lazy="selectin"
    )
