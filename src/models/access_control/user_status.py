from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.db import Base


class UserStatus(Base):
    __tablename__ = "user_status"
    __table_args__ = {"schema": "access_control"}

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
