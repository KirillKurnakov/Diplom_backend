from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base
from schemas.db import DbSchema

if TYPE_CHECKING:
    from ..page_configuration.query import Query


class Db(Base):
    __tablename__ = "db"
    __table_args__ = {"schema": "system_configuration"}

    id: Mapped[int] = mapped_column(primary_key=True)
    dbms: Mapped[str] = mapped_column(nullable=False)
    host: Mapped[str] = mapped_column(nullable=False)
    port: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("access_control.user.id"), nullable=False
    )

    queries: Mapped[List["Query"]] = relationship(
        back_populates="database", lazy="selectin"
    )

    def to_read_model(self) -> DbSchema:
        return DbSchema(
            id=self.id,
            dbms=self.dbms,
            host=self.host,
            port=self.port,
            name=self.name,
            username=self.username,
            password=self.password,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            version=self.version,
            user_id=self.user_id,
        )
