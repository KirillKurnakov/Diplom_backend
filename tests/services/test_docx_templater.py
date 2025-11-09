from datetime import datetime
from unittest.mock import MagicMock

import pytest

from schemas.templater import TemplaterRequest
from services.templaterDocx import DocxTemplate


@pytest.fixture
def docx_templater() -> DocxTemplate:
    """Создает экземпляр DocxTemplate с замоканными зависимостями."""
    mock_uow = MagicMock()
    mock_params = MagicMock(spec=TemplaterRequest)
    mock_params.model_dump.return_value = {
        "user_id": 1,
        "filter_params": {},
        "fields": {},
    }
    return DocxTemplate(
        uow=mock_uow, enquiry_id=1, templater_params=mock_params
    )


def test_add_footer_info(docx_templater, mocker):
    """Проверяет корректное добавление колонтитула в документ."""
    # Arrange
    mock_document = MagicMock()
    mock_section = MagicMock()
    mock_footer = MagicMock()
    mock_paragraph = MagicMock()
    mock_text_range = MagicMock()

    mock_document.Sections.Count = 1
    mock_document.Sections.get_Item.return_value = mock_section
    mock_section.HeadersFooters.OddFooter = mock_footer

    docx_templater.document = mock_document

    mock_paragraph_constructor = mocker.patch(
        "services.templaterDocx.Paragraph", return_value=mock_paragraph
    )
    mock_paragraph.AppendText.return_value = mock_text_range

    fixed_time = datetime(2025, 9, 24, 15, 0, 0)
    mock_datetime = MagicMock()
    mock_datetime.now.return_value = fixed_time
    mocker.patch("services.templaterDocx.datetime", mock_datetime)

    # Act
    docx_templater._add_footer_info()

    # Assert
    mock_paragraph_constructor.assert_called_once_with(mock_document)
    expected_footer_text = (
        f"Справка сформирована\n{fixed_time.strftime('%d.%m.%Y %H:%M:%S')}"
    )
    mock_paragraph.AppendText.assert_called_once_with(expected_footer_text)
    assert mock_text_range.CharacterFormat.FontSize == 9
    mock_footer.Paragraphs.Insert.assert_called_once_with(0, mock_paragraph)


@pytest.mark.asyncio
async def test_replace_single_placeholders_in_paragraph(
    docx_templater, mocker
):
    """Тестирует_replace_single_placeholders."""
    # 1. Arrange (Подготовка)

    # Создаем сложную иерархию моков для имитации структуры документа
    mock_document = MagicMock()
    mock_section = MagicMock()
    mock_paragraph = MagicMock()

    # Настраиваем иерархию: document -> section -> body -> paragraph
    mock_document.Sections.Count = 1
    mock_document.Sections.get_Item.return_value = mock_section

    # Body.ChildObjects будет списком, содержащим наш параграф
    mock_section.Body.ChildObjects.Count = 1
    mock_section.Body.ChildObjects.get_Item.return_value = mock_paragraph

    # Указываем, что наш объект является параграфом

    # Задаем текст параграфа, содержащий плейсхолдер
    mock_paragraph.Text = (
        "Привет, это тестовый параграф с плейсхолдером {{1:0;name}}."
    )

    mock_table = mocker.MagicMock()
    mock_table.Rows.Count = 1

    mock_row = mocker.MagicMock()
    mock_row.Rows.Count = 1

    mock_cell = mocker.MagicMock()
    mock_cell.Paragraphs.Count = 1

    mock_cell.Paragraphs.get_Item.return_value = mock_paragraph
    mock_row.Cells.get_Item.return_value = mock_cell
    mock_table.Rows.get_Item.return_value = mock_row
    mock_section.Tables.get_Item.return_value = mock_table
    mock_section.Tables.Count = 1

    # Устанавливаем мок-документ в наш тестируемый экземпляр
    docx_templater.document = mock_document

    # Нам не нужно тестировать внутренности swapping_placeholder_to_value,
    # мы просто хотим убедиться, что он был вызван.
    # Поэтому мы его мокаем. Используем AsyncMock, так как метод асинхронный.
    mock_swapping_method = mocker.patch.object(
        docx_templater,
        "swapping_placeholder_to_value",
        new_callable=mocker.AsyncMock,
    )

    # 2. Act (Действие)
    await docx_templater._replace_single_placeholders()

    # 3. Assert (Проверка)

    # Проверяем, что "шпион" swapping_placeholder_to_value был вызван один раз
    mock_swapping_method.assert_awaited_once()

    # Мы можем даже проверить, с какими аргументами он был вызван.
    # call_args[0] - это кортеж позиционных аргументов.
    # Первый аргумент - это объект match от регулярного выражения.
    call_args = mock_swapping_method.call_args[0]

    match_object = call_args[0]
    paragraph_object = call_args[1]
    text_object = call_args[2]

    assert (
        match_object.group(0) == "{{1:0;name}}"
    )  # Проверяем найденный плейсхолдер
    assert (
        paragraph_object is mock_paragraph
    )  # Проверяем, что передан правильный параграф
    assert (
        text_object == mock_paragraph.Text
    )  # Проверяем, что передан правильный текст
