from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base
from schemas.component import ComponentWithChildren
from schemas.page import PageSchema


class Page(Base):
    __tablename__ = "page"
    __table_args__ = {"schema": "page_configuration"}

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("page_configuration.page.id"), nullable=True
    )

    parent: Mapped[Optional["Page"]] = relationship(
        remote_side=[id], lazy="selectin"
    )

    code: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("access_control.user.id"), nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("access_control.user.id")
    )

    @hybrid_property
    def breadcrumbs(self) -> list[dict]:
        breadcrumbs = [{"name": self.title, "path": self.code}]
        if self.parent:
            breadcrumbs = [*self.parent.breadcrumbs, *breadcrumbs]
        return breadcrumbs

    @hybrid_property
    def config(self) -> list[dict]:
        config = [
            ComponentWithChildren(
                **component.to_read_model().model_dump(by_alias=True)
            )
            for component in self.components
            if component.parent_component_id is None
        ]
        return config

    def to_read_model(self):
        return PageSchema(
            id=self.id,
            parent_id=self.parent_id,
            code=self.code,
            title=self.title,
            description=self.description,
            created_at=self.created_at,
            updated_at=self.updated_at,
            version=self.version,
            user_id=self.user_id,
            created_by=self.created_by,
            breadcrumbs=self.breadcrumbs,
            config=self.config,
        )
