import os
import shutil
import subprocess

from schemas.templater import TemplaterRequest
from services.templaterDocx import DocxTemplate
from services.templaterXlsx import TemplaterXlsx
from utils.logger import GLOBAL_LOGGER
from utils.unitofwork import IUnitOfWork
from utils.utils import ExternalQueryExecutor


class PdfCreation:
    """Класс для автоматической генерации справки по формату ".pdf" ."""

    def __init__(
        self,
        uow: IUnitOfWork,
        enquiry_id: int,
        templater_params: TemplaterRequest,
    ):
        """Инициилизирует генератор справки.

        Args:
            uow (IUnitOfWork): Unit of Work для доступа к базам данных.
            enquiry_id (int): ID запроса для получения шаблонов.
            templater_params (TemplaterRequest): Параметры для фильтрации
                данных во внешних запросах.

        """
        self.uow = uow
        self.enquiry_id = enquiry_id
        self.templater_params = templater_params
        self.docx_templater = DocxTemplate(uow, enquiry_id, templater_params)
        self.xlsx_templater = TemplaterXlsx(uow, enquiry_id, templater_params)
        self.query_executor = ExternalQueryExecutor()

    async def pdf_creation(self) -> str:
        """Конвертирует файл в PDF с помощью Воли Небес.

        Основная функция генерации справки в формате `.pdf`,
        инициирует генерацию `.docx` справки по специальному шаблону, после
        конвертирует ее в `.pdf`

        Args:
            No arguments.

        Returns:
            str: Путь к сгенерированной справке.
        """
        # async with self.uow:
        #     theTypes = await self.query_executor.getTemplateTypes
        # (self.enquiry_id, self.uow)
        # if len(theTypes) == 1 and theTypes[0] == 'xlsx':
        #     path_to_file = await self.xlsx_templater.
        # generate_report_from_template()
        # elif len(theTypes) == 1 and theTypes[0] == 'docx':
        #     await self.docx_templater.setup()
        #     path_to_file = await self.docx_templater.
        # generate_report_from_template()
        # else:
        path_to_file = await self.docx_templater.generate_report_from_template(
            is_pdf=True
        )
        # path_to_file1 = (
        #     await self.xlsx_templater.generate_report_from_template()
        # )
        os.makedirs("pdfOlder", exist_ok=True)
        full_path = os.path.join(os.getcwd(), path_to_file)
        destination_path = os.path.join("pdfOlder", path_to_file)
        shutil.move(full_path, destination_path)
        pdf_output_path = os.path.splitext(destination_path)[0] + ".pdf"
        pdf_output_dir = os.path.dirname(destination_path)

        command = "soffice" if os.name != "nt" else "soffice.exe"
        args = [
            command,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            pdf_output_dir,
            destination_path,
        ]

        conversion = subprocess.run(
            args, check=True, timeout=120, capture_output=True, text=True
        )
        GLOBAL_LOGGER.debug("STDOUT:", conversion.stdout)
        if conversion.stderr:
            GLOBAL_LOGGER.error("STDERR:", conversion.stderr)

        GLOBAL_LOGGER.debug(f"Файл успешно сконвертирован: {pdf_output_path}")
        return pdf_output_path
