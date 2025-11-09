from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base
from models.system_configuration.associations import (
    enquiry_template_block_query_association_table,
)
from schemas.query import QuerySchema

if TYPE_CHECKING:
    from ..system_configuration.db import Db
    from ..system_configuration.enquiry_template_block import (
        EnquiryTemplateBlock,
    )


class Query(Base):
    __tablename__ = "query"
    __table_args__ = {"schema": "page_configuration"}

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    sql_query: Mapped[str] = mapped_column(nullable=False)
    database_id: Mapped[int] = mapped_column(
        ForeignKey("system_configuration.db.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("access_control.user.id"), nullable=False
    )
    code: Mapped[str]

    database: Mapped["Db"] = relationship(
        back_populates="queries", foreign_keys=[database_id], lazy="selectin"
    )

    enquiry_template_blocks: Mapped[List["EnquiryTemplateBlock"]] = (
        relationship(
            secondary=enquiry_template_block_query_association_table,
            back_populates="queries",
            lazy="selectin",
        )
    )

    def to_read_model(self) -> QuerySchema:
        return QuerySchema(
            id=self.id,
            title=self.title,
            description=self.description,
            sql_query=self.sql_query,
            database_id=self.database_id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            version=self.version,
            user_id=self.user_id,
            code=self.code,
            database=self.database.to_read_model(),
        )
