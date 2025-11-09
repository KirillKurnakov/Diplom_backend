from decimal import Decimal

import pytest
from loguru import logger

from services.templaterDocx import DocxTemplate


class DummyUOW:
    pass


class DummyTemplaterRequest:
    def model_dump(self):
        return {"filter_params": {"inn": ["123"]}}


@pytest.fixture(autouse=True)
def setup_logger_for_pytest(caplog):
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level="DEBUG",
        filter=lambda record: True,
    )
    yield
    logger.remove(handler_id)


@pytest.fixture
def docx_templater() -> DocxTemplate:
    """Создает экземпляр нашего класса с пустыми зависимостями."""
    return DocxTemplate(
        uow=DummyUOW(), enquiry_id=1, templater_params=DummyTemplaterRequest()
    )


def test_insert_string_value(docx_templater, mocker):
    """Тестирует, что обычная строка правильно вставляется в параграф."""
    # 1. Подготовка (Arrange)
    # Создаем мок (подделку) для объекта CharacterFormat. Нам не важно, что внутри.
    mock_char_format = mocker.Mock()

    # Создаем мок для TextRange, который должен возвращать наш мок формата.
    mock_text_range = mocker.Mock()
    # Настраиваем мок: говорим, что при вызове метода ApplyCharacterFormat
    # он должен вернуть наш мок формата (это нужно для цепочки вызовов).
    mock_text_range.ApplyCharacterFormat.return_value = mock_char_format

    # Создаем мок для Paragraph. Это наш главный "шпион".
    mock_paragraph = mocker.Mock()
    # Настраиваем его: при вызове метода AppendText он должен вернуть мок TextRange.
    mock_paragraph.AppendText.return_value = mock_text_range

    test_value = "Простой текст"

    # 2. Действие (Act)
    # Вызываем тестируемый метод с нашими моками
    docx_templater._insert_value_with_formatting(
        paragraph=mock_paragraph, value=test_value, formatting=mock_char_format
    )

    # 3. Проверка (Assert)
    # Проверяем, что метод AppendText у нашего "шпиона" был вызван ровно 1 раз.
    mock_paragraph.AppendText.assert_called_once()
    # Проверяем, что метод AppendText был вызван именно с текстом "Простой текст".
    mock_paragraph.AppendText.assert_called_with("Простой текст")
    # Проверяем, что у результата (mock_text_range) был вызван метод ApplyCharacterFormat
    # и что ему был передан наш объект форматирования.
    mock_text_range.ApplyCharacterFormat.assert_called_once_with(
        mock_char_format
    )


def test_insert_decimal_value(docx_templater, mocker):
    """Тестирует, что число Decimal правильно форматируется и вставляется."""
    # 1. Arrange
    mock_char_format = mocker.Mock()
    mock_text_range = mocker.Mock()
    mock_text_range.ApplyCharacterFormat.return_value = mock_char_format
    mock_paragraph = mocker.Mock()
    mock_paragraph.AppendText.return_value = mock_text_range

    # Тестовое значение Decimal
    test_value = Decimal("12345.67")
    expected_string = "12 345,7"  # Ожидаемый результат форматирования

    # 2. Act
    docx_templater._insert_value_with_formatting(
        paragraph=mock_paragraph, value=test_value, formatting=mock_char_format
    )

    # 3. Assert
    # Проверяем, что метод был вызван с правильно отформатированной строкой
    mock_paragraph.AppendText.assert_called_once_with(expected_string)
    mock_text_range.ApplyCharacterFormat.assert_called_once_with(
        mock_char_format
    )


def test_insert_negative_decimal_value(docx_templater, mocker):
    """Тестирует, что отрицательное число Decimal правильно форматируется."""
    # 1. Arrange
    mock_char_format = mocker.Mock()
    mock_text_range = mocker.Mock()
    mock_text_range.ApplyCharacterFormat.return_value = mock_char_format
    mock_paragraph = mocker.Mock()
    mock_paragraph.AppendText.return_value = mock_text_range

    test_value = Decimal("-987.65")
    expected_string = "-987,6"  # Твоя логика округляет -0.65 до -0.6

    # 2. Act
    docx_templater._insert_value_with_formatting(
        paragraph=mock_paragraph, value=test_value, formatting=mock_char_format
    )

    # 3. Assert
    mock_paragraph.AppendText.assert_called_once_with(expected_string)
    mock_text_range.ApplyCharacterFormat.assert_called_once_with(
        mock_char_format
    )
