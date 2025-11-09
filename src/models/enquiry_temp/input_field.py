from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db import Base

if TYPE_CHECKING:
    from models.access_control.user import User
    from models.system_configuration.enquiry import Enquiry


# --- Модель для `input_field` ---
class InputField(Base):
    __tablename__ = "input_field"
    __table_args__ = {"schema": "enquiry_temp"}

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    field_key: Mapped[str] = mapped_column(String)
    field_type: Mapped[str] = mapped_column(String)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("access_control.user.id")
    )

    # Связь "один-ко-многим" к таблице-ассоциации
    enquiry_associations: Mapped[List["EnquiryInputField"]] = relationship(
        back_populates="input_field", lazy="selectin"
    )


# --- Модель для `enquiry_input_field` ---
class EnquiryInputField(Base):
    __tablename__ = "enquiry_input_field"
    __table_args__ = (
        UniqueConstraint(
            "enquiry_id", "input_field_id", name="unique_enq_input_fields"
        ),
        {"schema": "enquiry_temp"},
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    enquiry_id: Mapped[int] = mapped_column(
        ForeignKey("system_configuration.enquiry.id", ondelete="CASCADE")
    )
    input_field_id: Mapped[int] = mapped_column(
        ForeignKey("enquiry_temp.input_field.id", ondelete="CASCADE")
    )
    enquiry_specific: Mapped[bool] = mapped_column(default=True)

    # Связи "многие-к-одному"
    enquiry: Mapped["Enquiry"] = relationship(back_populates="input_fields")
    input_field: Mapped["InputField"] = relationship(
        back_populates="enquiry_associations", lazy="selectin"
    )

    # Связь "один-ко-многим" к значениям
    values: Mapped[List["InputFieldValue"]] = relationship(
        back_populates="enquiry_input_field", lazy="selectin"
    )

    @hybrid_property
    def relevant_values(self) -> List["InputFieldValue"]:
        """Возвращает список релевантрых значений.

        - Если `enquiry_specific`=True, возвращает только значения,
            связанные с этой конкретной записью.
        - Если `enquiry_specific`=False, возвращает значения от ВСЕХ
            записей, которые ссылаются на тот же `InputField`.
        """
        if self.enquiry_specific:
            # Если поле специфично, возвращаем только "свои" значения
            return self.values
        else:
            # Если поле "общее", собираем значения со всех "соседей"
            all_values = []
            # self.input_field.enquiry_associations - это все записи
            # EnquiryInputField, которые ссылаются на тот же InputField.
            for association in self.input_field.enquiry_associations:
                all_values.extend(association.values)
            return all_values


# --- Модель для `input_field_value` ---
class InputFieldValue(Base):
    __tablename__ = "input_field_value"
    __table_args__ = {"schema": "enquiry_temp"}

    id: Mapped[int] = mapped_column(primary_key=True)
    enquiry_input_field_id: Mapped[int | None] = mapped_column(
        ForeignKey("enquiry_temp.enquiry_input_field.id", ondelete="SET NULL")
    )
    input_field_value: Mapped[str] = mapped_column(Text)
    is_deleted: Mapped[bool | None] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("access_control.user.id", ondelete="SET NULL")
    )

    # Связи "многие-к-одному"
    enquiry_input_field: Mapped["EnquiryInputField"] = relationship(
        back_populates="values", lazy="selectin"
    )
    user: Mapped["User | None"] = relationship(lazy="selectin")
