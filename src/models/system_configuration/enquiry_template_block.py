from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base

from .associations import (
    enquiry_template_block_association_table,
    enquiry_template_block_query_association_table,
)

if TYPE_CHECKING:
    from enquiry_template import EnquiryTemplate

    from models.access_control.user import User
    from models.page_configuration.query import Query


class EnquiryTemplateBlock(Base):
    __tablename__ = "enquiry_template_block"
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
        back_populates="enquiry_template_blocks", lazy="selectin"
    )

    templates: Mapped[List["EnquiryTemplate"]] = relationship(
        secondary=enquiry_template_block_association_table,
        back_populates="blocks",
        lazy="selectin",
    )

    queries: Mapped[List["Query"]] = relationship(
        secondary=enquiry_template_block_query_association_table,
        back_populates="enquiry_template_blocks",
        lazy="selectin",
    )
