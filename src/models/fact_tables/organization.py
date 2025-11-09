from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from db.db import Base


class Organization(Base):
    __tablename__ = "organization"
    __table_args__ = {"schema": "fact_tables"}

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    short_name: Mapped[str] = mapped_column(String, nullable=False)
    inn: Mapped[str] = mapped_column(String, nullable=False)
    okpo: Mapped[str] = mapped_column(String, nullable=False)
    okved: Mapped[str] = mapped_column(String, nullable=False)
    oksm_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fns_code_id: Mapped[int] = mapped_column(Integer, nullable=False)
