import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем модели, которые нужны для создания тестовых данных
from tests.model_factories import create_enquiry
from utils.unitofwork import IUnitOfWork


@pytest.mark.asyncio
async def test_get_templates_types_success(
    client: AsyncClient, db_session: AsyncSession, get_test_uow: IUnitOfWork
):
    """Тест успешного получения типов шаблонов для существующей справки."""
    # 1. Arrange (Подготовка): Создаем данные в тестовой БД
    test_enquiry = await create_enquiry(db_session)
    await db_session.commit()

    async with get_test_uow:
        valid_enquiry_list = await get_test_uow.enquiries.get_data_by_id(
            test_enquiry.id
        )
    valid_enquiry = valid_enquiry_list[0]
    # 2. Act (Действие): Отправляем запрос
    response = await client.get(f"/enquiry/api/v1/{valid_enquiry.id}/")
    created_template_filepath = valid_enquiry.templates[0].template_file_path
    expected_formats = [created_template_filepath.split(".")[-1], "pdf"]
    # 3. Assert (Проверка): Проверяем результат
    assert response.status_code == 200
    response_data = response.json()

    assert sorted(response_data["formats"]) == sorted(expected_formats)
    assert response_data["fields"] == []


@pytest.mark.asyncio
async def test_get_templates_types_not_found(
    client: AsyncClient, get_test_uow
):
    """Тест получения ошибки 404 для несуществующей справки."""
    # 1. Arrange: Ничего не создаем в БД, она пуста для этого теста

    # 2. Act: Отправляем запрос к несуществующему ресурсу
    response = await client.get("/enquiry/api/v1/999/")

    # 3. Assert: Проверяем ошибку
    assert response.status_code == 404
    assert response.json() == {"detail": "Enquiry not found"}
