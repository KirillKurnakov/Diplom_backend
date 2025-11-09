import os
import re
import shutil
import zipfile
from datetime import datetime
from decimal import Decimal
from typing import Match, Union

import spire.doc
from spire.doc import (
    Document,
    FileFormat,
    HorizontalAlignment,
    Paragraph,
    TextRange,
)
from spire.doc.common import Regex

from schemas.templater import TemplaterRequest
from utils.logger import GLOBAL_LOGGER
from utils.unitofwork import IUnitOfWork
from utils.utils import ExternalQueryExecutor

from .base_templater import BaseTemplater


class DocxTemplate(BaseTemplater):
    """Класс для автоматической генерации справки по формату ".docx" ."""

    def __init__(
        self,
        uow: IUnitOfWork,
        enquiry_id: int,
        templater_params: TemplaterRequest,
    ):
        """Инициализирует генератор справки.

        Args:
            uow (IUnitOfWork): Unit of Work для доступа к базам данных.
            enquiry_id (int): ID справки для получения шаблонов.
            templater_params (TemplaterRequest): Параметры для фильтрации
                данных во внешних запросах.

        """
        super().__init__(
            uow, enquiry_id, templater_params, template_type="docx"
        )
        self._SAMPLE_RESPONSES = {
            "5": [
                {"inn": 777777, "chinases": "МБОУ СОШ 13579"},
                {"inn": 777777, "chinases": "МБОУ СОШ 13579"},
                {"inn": 777777, "chinases": "МБОУ СОШ 13579"},
            ],
            "8": [{"inn": 777777}],
            "7": [{"inn": 777777}],
            "6": [
                {
                    "n": 1,
                    "pokaz": "Работы",
                    "n2": 3,
                    "pokaz34": "Ыбок",
                    "y_2023": 55.66,
                    "y_2024": 66.77,
                    "y_2025": 100.25,
                },
                {
                    "n": 2,
                    "pokaz": "Услуги",
                    "n2": 4,
                    "pokaz34": "ЫЫЫБ",
                    "y_2023": 55.66,
                    "y_2024": 66.77,
                    "y_2025": 100.25,
                },
                {
                    "n": 3,
                    "pokaz": "Работы",
                    "n2": 77,
                    "pokaz34": "РЫБЫ",
                    "y_2023": 55.662,
                    "y_2024": 66.737,
                    "y_2025": 100.425,
                },
                {
                    "n": 4,
                    "pokaz": "РаботыS",
                    "n2": 52,
                    "pokaz34": "workЫ",
                    "y_2023": 55.663,
                    "y_2024": 66.727,
                    "y_2025": 100.255,
                },
            ],
            "9": [
                {
                    "n": 5,
                    "pokaz": "PIPIPUPU",
                    "y_2023": 255.66,
                    "y_2024": 366.77,
                    "y_2025": 4100.25,
                },
                {
                    "n": 7,
                    "pokaz": "PIPIPUPU",
                    "y_2023": 255.66,
                    "y_2024": 366.77,
                    "y_2025": 4100.25,
                },
                {
                    "n": 6,
                    "pokaz": "PIPIPUPU",
                    "y_2023": 255.662,
                    "y_2024": 366.737,
                    "y_2025": 4100.425,
                },
            ],
        }

    def _load_template(self):
        """Загружает шаблон Word документа."""
        self.document = Document()
        self.document.LoadFromFile(self.template_file_path)

    def _save_and_cleanup(self) -> str:
        """Сохраняет итоговый документ, удаляя вотермарки."""
        self.document.SaveToFile("tmp.docx", FileFormat.Docx2016)
        self.document.Close()
        self.removing_watermarks("tmp.docx", "final.docx")
        os.unlink("tmp.docx")
        return "final.docx"

    def _add_footer_info(self) -> None:
        """Добавляет нижний колонтитул с датой и временем генерации.

        Функция добавляет информацию о времени формирования справки
        в нижний колонтитул каждой секции документа.

        Args:
            document (Document): Документ, в который нужно добавить колонтитул.

        Returns:
            None: Функция модифицирует объект `document` напрямую.
        """
        current_time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        # Создание параграфа с данными(мета)
        credentials_in_footer = Paragraph(self.document)
        footer_text = f"Справка сформирована\n{current_time}"
        text_range = credentials_in_footer.AppendText(footer_text)
        text_range.CharacterFormat.FontSize = 9
        text_range.CharacterFormat.FontName = "Times New Roman"
        credentials_in_footer.Format.AfterSpacing = 0
        credentials_in_footer.Format.HorizontalAlignment = (
            HorizontalAlignment.Right
        )

        for i in range(self.document.Sections.Count):
            section = self.document.Sections.get_Item(i)

            footer = section.HeadersFooters.OddFooter

            # Добавляем новый параграф в начало колонтитула
            footer.Paragraphs.Insert(0, credentials_in_footer)

    def _insert_value_with_formatting(
        self,
        paragraph: Paragraph,
        value: Union[Decimal, str, int, None],
        formatting: spire.doc.CharacterFormat,
    ) -> None:
        """Вставляет в параграф данные с форматированием.

        Функция производит проверку типа входящего значения, применяет
        к нему форматирование и вставляет в параграф.

        Args:
            paragraph (Paragraph): Параграф ожидающий информацию.
            value (Union[Decimal, str]): Значение(число или строка) для
            вставки.
            formatting (spire.doc.CharacterFormat): Объект `CharacterFormat`,
            содержащий информацию о форматировании.

        Returns:
            None: Объект `paragraph` редактируется напрямую.

        """
        if isinstance(value, Decimal):
            integer_part = int(value)
            decimal_part = round((value - integer_part) * 10)
            if "-" in str(decimal_part):
                decimal_part = decimal_part * -1
            formatted_integer = f"{integer_part:,}".replace(",", " ")
            text_to_insert = f"{formatted_integer},{decimal_part}"
        else:
            text_to_insert = str(value)
        paragraph.AppendText(text_to_insert).ApplyCharacterFormat(formatting)

    def process_formatters(self, document: Document) -> None:
        """Обрабатывает форматоры в документе.

        Функция обрабатывает плейсхолдеры составленные для форматоров.

        Args:
            document (Document): Обрабатывающийся документ.

        Returns:
            None: Функция модифицирует объект `document` напрямую.

        """
        pattern_string = r"\{\{([a-zA-Z_][\w;]*);(\d+;[a-zA-Z_]\w*)\}\}"
        spire_regex = Regex(pattern_string)
        pattern_compiled = re.compile(pattern_string)

        selections = document.FindAllPattern(spire_regex)

        if not selections:
            GLOBAL_LOGGER.debug(
                "Плейсхолдеров-форматтеров в docx шаблоне не найдено."
            )
            return

        for selection in list(selections):
            placeholder_range = selection.GetAsOneRange()
            placeholder_text = placeholder_range.Text

            match = pattern_compiled.search(placeholder_text)
            if not match:
                continue

            operations_str, data_source_str = match.groups()

            formatter_operations = operations_str.split(";")
            query_id_str, column_name = data_source_str.split(";")
            query_id = int(query_id_str)

            current_result = 0.0
            value_to_insert: Union[Decimal, str]

            if (
                query_id not in self.query_responses
                or not self.query_responses[query_id]
            ):
                GLOBAL_LOGGER.debug(
                    f"Предупреждение: нет данных для query_id {query_id}\
                          в плейсхолдере {placeholder_text}"
                )
                value_to_insert = "0"
            else:
                for operation in reversed(formatter_operations):
                    operation = operation.strip().upper()

                    if operation == "SUM":
                        GLOBAL_LOGGER.debug("Ima kinda useless...")

                    elif operation == "ROUND":
                        if current_result != 0.0:
                            current_result = round(current_result)
                        else:
                            for dataset in self.query_responses[query_id]:
                                for key in dataset.keys():
                                    current_value = dataset[key]
                                    if key == column_name and isinstance(
                                        current_value, int
                                    ):
                                        current_result = round(current_value)

                value_to_insert = Decimal(str(current_result))

            paragraph = placeholder_range.OwnerParagraph
            pseudo_formatting = paragraph.ChildObjects.get_Item(
                0
            ).CharacterFormat
            paragraph.ChildObjects.Remove(placeholder_range)
            self._insert_value_with_formatting(
                paragraph, value_to_insert, pseudo_formatting
            )

    async def swapping_placeholder_to_value(
        self, match: Match[str], paragraph: Paragraph, paragraph_text: str
    ) -> None:
        """Заменяет плейсхолдер значением.

        Args:
            match (re.match): _description_.
            paragraph (Paragraph): _description_.
            paragraph_text (str): _description_.

        Returns:
            None: _description_.

        """
        # Получаем значение из наших данных
        value_to_insert = await self._placeholder_replacer(match)
        # Получение форматирования ячейки и замена текста внутри
        formatting = paragraph.ChildObjects.get_Item(0).CharacterFormat
        updated_value = paragraph_text.replace(match.group(0), value_to_insert)
        paragraph.ChildObjects.Clear()
        text_range = paragraph.AppendText(updated_value)
        text_range.ApplyCharacterFormat(formatting)

    async def _replace_single_placeholders(self) -> None:
        """Заменяет одиночные плейсхолдеры в параграфах документа.

        Функция итерируется по параграфам найденным с помощью `spire_regex`
        и заменяет найденные плейсхолдеры, формата
        `{{query_id:response_index;column_name}}`. Найденные плейсхолдеры
        заменяются на соответствующие данные из `self.query_responses`

        Args:
            document (Document): Обрабатывающийся документ.

        Returns:
            None: Функция обрабатывает объект `document` напрямую.

        """
        # Паттерн для поиска одиночных плейсхолдеров: {{id:index;column}}
        # Spire.Doc позволяет искать по всему документу
        # с помощью регулярных выражений

        for section_index in range(self.document.Sections.Count):
            section = self.document.Sections.get_Item(section_index)

            for paragraph_index in range(section.Body.ChildObjects.Count):
                paragraph = section.Body.ChildObjects.get_Item(paragraph_index)
                if not isinstance(paragraph, Paragraph):
                    continue

                paragraph_text = paragraph.Text

                if "{{" not in paragraph_text:
                    continue

                match = self.combined_pattern.search(paragraph_text)
                if match:
                    await self.swapping_placeholder_to_value(
                        match, paragraph, paragraph_text
                    )

            for table_index in range(section.Tables.Count):
                table = section.Tables.get_Item(table_index)

                for row_index in range(table.Rows.Count - 1, -1, -1):
                    row = table.Rows.get_Item(row_index)

                    for cell_index in range(row.Cells.Count):
                        cell = row.Cells.get_Item(cell_index)

                        if cell.Paragraphs.Count > 0:
                            for paragraph_index in range(
                                cell.Paragraphs.Count
                            ):
                                paragraph = cell.Paragraphs.get_Item(
                                    paragraph_index
                                )
                                paragraph_text = paragraph.Text

                                match = self.combined_pattern.search(
                                    paragraph_text
                                )
                                if match:
                                    await self.swapping_placeholder_to_value(
                                        match, paragraph, paragraph_text
                                    )

    def _process_dynamic_tables(self) -> None:
        """Обрабатывает (динамические) блоки документа.

        Функция итерируется по секциям, затем по таблицам и , в заключение,
        по рядам, ищет плейсхолдеры, формата
        `{{query_id:response_index;column_name}}`. Найденные плейсхолдеры
        заменяются на соответствующие данные из `self.query_responses` либо
        строка с отсутствующими данными удаляется.

        Args:
            document (Document): Обрабатываемый документ.

        Returns:
            None: Функция модифицирует объект `document` напрямую.

        """
        for section_index in range(self.document.Sections.Count):
            section = self.document.Sections.get_Item(section_index)

            for table_index in range(section.Tables.Count):
                table = section.Tables.get_Item(table_index)

                for row_index in range(table.Rows.Count - 1, -1, -1):
                    row = table.Rows.get_Item(row_index)

                    row_text_parts = []
                    for cell_index in range(row.Cells.Count):
                        cell = row.Cells.get_Item(cell_index)

                        if cell.Paragraphs.Count > 0:
                            paragraph = cell.Paragraphs.get_Item(0)
                            row_text_parts.append(paragraph.Text)

                    row_text = "".join(row_text_parts)

                    if re.search(r"\{\{\d+;.+?\}\}", row_text):
                        GLOBAL_LOGGER.debug(
                            f"В docx шаблоне найдена строка-шаблон в таблице\
                                {table_index} на строке {row_index}..."
                        )

                        placeholders_in_row = {}
                        query_id_for_this_row = None

                        for cell_index in range(row.Cells.Count):
                            cell = row.Cells.get_Item(cell_index)
                            if cell.Paragraphs.Count > 0:
                                cell_text = cell.Paragraphs.get_Item(0).Text
                                match = re.search(
                                    r"\{\{(\d+);(.+?)\}\}", cell_text
                                )
                                if match:
                                    query_id_str, column_name = match.groups()
                                    query_id_for_this_row = int(query_id_str)
                                    placeholders_in_row[cell_index] = (
                                        query_id_for_this_row,
                                        column_name,
                                    )

                        if (
                            not query_id_for_this_row
                            or query_id_for_this_row
                            not in self.query_responses
                        ):
                            table.Rows.RemoveAt(row_index)
                            GLOBAL_LOGGER.debug(
                                f"  -> Данных нет, строка-шаблон {row_index}\
                                    удалена."
                            )
                            continue

                        data_to_insert = self.query_responses[
                            query_id_for_this_row
                        ]

                        if len(data_to_insert) == 1:
                            last_data_row = data_to_insert[-1]
                            for cell_index, (
                                query_id,
                                column_name,
                            ) in placeholders_in_row.items():
                                cell = row.Cells.get_Item(cell_index)
                                paragraph = cell.Paragraphs.get_Item(0)
                                if (
                                    paragraph.ChildObjects.Count > 0
                                    and isinstance(
                                        paragraph.ChildObjects.get_Item(0),
                                        TextRange,
                                    )
                                ):
                                    first_text_range = (
                                        paragraph.ChildObjects.get_Item(0)
                                    )
                                    template_formatting = (
                                        first_text_range.CharacterFormat
                                    )
                                paragraph.ChildObjects.Clear()
                                text_to_append = last_data_row.get(
                                    column_name, ""
                                )
                                self._insert_value_with_formatting(
                                    paragraph,
                                    text_to_append,
                                    template_formatting,
                                )
                        else:
                            for i in range(len(data_to_insert) - 1, -1, -1):
                                data_row = data_to_insert[i]
                                new_row = row.Clone()

                                for cell_index, (
                                    query_id,
                                    column_name,
                                ) in placeholders_in_row.items():
                                    cell = new_row.Cells.get_Item(cell_index)
                                    paragraph = cell.Paragraphs.get_Item(0)
                                    if (
                                        paragraph.ChildObjects.Count > 0
                                        and isinstance(
                                            paragraph.ChildObjects.get_Item(0),
                                            TextRange,
                                        )
                                    ):
                                        first_text_range = (
                                            paragraph.ChildObjects.get_Item(0)
                                        )
                                        template_formatting = (
                                            first_text_range.CharacterFormat
                                        )
                                    paragraph.ChildObjects.Clear()
                                    text_to_append = data_row.get(
                                        column_name, ""
                                    )
                                    self._insert_value_with_formatting(
                                        paragraph,
                                        text_to_append,
                                        template_formatting,
                                    )

                                table.Rows.Insert(row_index, new_row)
                            template_row_new_index = row_index + len(
                                data_to_insert
                            )
                            table.Rows.RemoveAt(template_row_new_index)

    def removing_watermarks(
        self, file_to_cleanse: str, cleaned_file_path: str
    ) -> None:
        """Удаляет водяной знак, оставленную триальной версией библиотеки.

        Ищет и удаляет параграф с водяным знаком `spire.doc` из документа
        `file_to_cleanse`, после сохраняет полученный документ как
        `cleaned_file_path` и удаляет директорию с промежуточными файлами,
        созданными в предыдущих функциях.

        Args:
            file_to_cleanse (str): Обрабатываемый файл.
            cleaned_file_path (str): Очищенный от вотермарки файл.

        Returns:
            None: Создает новый файл по пути `cleaned_file_path`
        без водяного знака.

        """
        GLOBAL_LOGGER.debug(
            f"Применяем метод 'грубой силы' (XML)\
                  к файлу {file_to_cleanse}..."
        )

        watermark_text = (
            '<w:p><w:r><w:rPr><w:color w:val="FF0000" /><w:sz w:'
            'val="24" /></w:rPr><w:t xml:space="preserve">Evaluation Warning: '
            "The document was created with Spire.Doc"
            " for Python.</w:t></w:r></w:p>"
        )

        temp_dir = "temp_docx_unpacked"

        with zipfile.ZipFile(file_to_cleanse, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        xml_changed = False
        for dirpath, _, filenames in os.walk(temp_dir):
            for filename in filenames:
                if filename.endswith(".xml"):
                    xml_path = os.path.join(dirpath, filename)

                    with open(xml_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if watermark_text in content:
                        GLOBAL_LOGGER.debug(
                            f"Найден водяной знак в файле: {filename}"
                        )
                        new_content = content.replace(
                            watermark_text,
                            "",
                        )

                        with open(xml_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        xml_changed = True

        if not xml_changed:
            GLOBAL_LOGGER.debug(
                "Водяной знак не найден на уровне XML. Возможно,"
                " он является изображением."
            )
            shutil.copy(file_to_cleanse, cleaned_file_path)
            shutil.rmtree(temp_dir)
            return

        with zipfile.ZipFile(
            cleaned_file_path, "w", zipfile.ZIP_DEFLATED
        ) as zip_out:
            for dirpath, _, filenames in os.walk(temp_dir):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zip_out.write(file_path, arcname)

        shutil.rmtree(temp_dir)
        GLOBAL_LOGGER.debug(f"Очищенный файл сохранен как {cleaned_file_path}")
