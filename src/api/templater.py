import os
import shutil
import time

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from starlette.background import BackgroundTask

from api.dependencies import UOWDep
from schemas.templater import TemplaterRequest
from services.templaterDocx import DocxTemplate
from services.templaterPdf import PdfCreation
from services.templaterXlsx import TemplaterXlsx
from utils.logger import GLOBAL_LOGGER
from utils.utils import ExternalQueryExecutor

router = APIRouter(
    prefix="/enquiry/api/v1",
    tags=["Enquiries"],
)


@router.post("/{enquiry_id}/xlsx/", response_model=None)
async def generate_excel_file(
    uow: UOWDep,
    templater_params: TemplaterRequest,
    enquiry_id: int = Path(
        ..., description="ID справки для формирования шаблона"
    ),
) -> FileResponse:
    """Генерирует справку формата `.xlsx` .

    Args:
        uow (UOWDep): Unit of Work для доступа к базам данных..
        enquiry_id (int): ID справки для формирования шаблона.
        templater_params (TemplaterRequest): Параметры для фильтрации
            данных во внешних запросах.

    Returns:
        FileResponse: HTTP-ответ, содержащий сгенерированный файл справки.

    """
    start_time = time.perf_counter()
    templater_xlsx = TemplaterXlsx(uow, enquiry_id, templater_params)
    GLOBAL_LOGGER.debug(f"начало выполнения скрипта - {time.ctime()}\n")
    file_path = await templater_xlsx.generate_report_from_template()
    task = BackgroundTask(os.unlink, file_path)
    GLOBAL_LOGGER.debug(
        "enquiry created in %2.f seconds" % (time.perf_counter() - start_time)
    )
    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=zealot.xlsx"},
        background=task,
    )


#
# Как передавать перечень справок в компонент, на основании чего?
# Передавать на фронт возможные форматы шаблона
# Эндпоинт на pdf
# Проверка авторизации на стороне Yii2
# Подключить логгер
# Где хранить шаблоны
# --------------------
# Форматтеры, принимающие в себя параметры
#


@router.post("/{enquiry_id}/docx/", response_model=None)
async def generate_word_file(
    uow: UOWDep,
    templater_params: TemplaterRequest,
    enquiry_id: int = Path(
        ..., description="ID справки для формирования шаблона"
    ),
) -> FileResponse:
    """Генерирует справку формата `.docx` .

    Args:
        uow (UOWDep): Unit of Work для доступа к базам данных..
        enquiry_id (int): ID справки для формирования шаблона.
        templater_params (TemplaterRequest): Параметры для фильтрации
            данных во внешних запросах.

    Returns:
        FileResponse: HTTP-ответ, содержащий сгенерированный файл справки.

    """
    start_time = time.perf_counter()

    templater_docx = DocxTemplate(uow, enquiry_id, templater_params)

    GLOBAL_LOGGER.debug(f"начало выполнения скрипта - {time.ctime()}\n")

    file_path = await templater_docx.generate_report_from_template()
    task = BackgroundTask(os.unlink, file_path)

    GLOBAL_LOGGER.debug(
        "enquiry created in %2.f seconds" % (time.perf_counter() - start_time)
    )

    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=zealot.docx"},
        background=task,
    )


@router.post("/{enquiry_id}/pdf/", response_model=None)
async def generate_pdf_file(
    uow: UOWDep,
    templater_params: TemplaterRequest,
    enquiry_id: int = Path(
        ..., description="ID справки для формирования шаблона"
    ),
) -> FileResponse:
    """Генерирует справку формата `.pdf` .

    Args:
        uow (UOWDep): Unit of Work для доступа к базам данных..
        enquiry_id (int): ID справки для формирования шаблона.
        templater_params (TemplaterRequest): Параметры для фильтрации
            данных во внешних запросах.

    Returns:
        FileResponse: HTTP-ответ, содержащий сгенерированный файл справки.

    """
    start_time = time.perf_counter()
    templater_pdf = PdfCreation(uow, enquiry_id, templater_params)
    GLOBAL_LOGGER.debug(f"начало выполнения скрипта - {time.ctime()}\n")
    file_path = await templater_pdf.pdf_creation()
    task = BackgroundTask(shutil.rmtree, os.path.dirname(file_path))
    GLOBAL_LOGGER.debug(
        "enquiry created in %2.f seconds" % (time.perf_counter() - start_time)
    )
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=zealot.pdf"},
        background=task,
    )


@router.get("/{enquiry_id}/")
async def get_templates_info(
    uow: UOWDep,
    enquiry_id: int = Path(
        ..., description="ID справки для сбора информации о шаблонах"
    ),
) -> JSONResponse:
    """Получает доступные форматы шаблонов.

    Args:
        uow (UOWDep): Unit of Work для доступа к базам данных.
        enquiry_id (int): ID справки для сбора информации о шаблонах.

    Returns:
        JSONResponse: Функция возвращает список форматов шаблонов
        в необходимом формате.

    Raises:
        HTTPException: HTTP-ответ, содержащий список доступных форматов
        шаблонов (например, ["xlsx", "docx", "pdf"]).
    """
    query_executor = ExternalQueryExecutor()
    async with uow:
        GLOBAL_LOGGER.debug("Пошел запрос за информацией о шаблонах")
        enquiry_info = await query_executor.get_template_info(enquiry_id, uow)
        if not enquiry_info:
            raise HTTPException(status_code=404, detail="Enquiry not found")
        else:
            enquiry_info["formats"].append("pdf")
    encoded_data = jsonable_encoder(enquiry_info)
    return JSONResponse(content=encoded_data)


@router.delete("/input_field_value")
async def input_field_value_soft_delete(
    uow: UOWDep,
    input_field_value_id: int = Query(..., description="ID удаляемого поля"),
    enquiry_id: int = Query(..., description="ID справки с полем"),
) -> JSONResponse:
    """Мягко удаляет значение поля в справке.

    Args:
        uow (UOWDep): Unit of Work для доступа к базам данных.
        input_field_value_id (int): "ID удаляемого поля".
        enquiry_id (int): "ID справки с полем".

    Returns:
        JSONResponse: Ответ со статусом.

    """
    query_executor = ExternalQueryExecutor()
    async with uow:
        GLOBAL_LOGGER.debug(
            f"Пошел запрос на удаление значения поля {input_field_value_id} "
            f"для справки {enquiry_id}"
        )
        was_deleted = await query_executor.delete_input_field_value_soft(
            enquiry_id, uow, input_field_value_id
        )
        if not was_deleted:
            raise HTTPException(
                status_code=404,
                detail="Значение не найдено или не принадлежит указанной"
                " справке.",
            )

    return JSONResponse(
        status_code=200, content={"message": "Значение было успешно удалено"}
    )
