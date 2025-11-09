from sqlalchemy.ext.asyncio import AsyncSession

from models import Enquiry, EnquiryTemplate, Organization, User, UserStatus

# Фабрики лучше делать асинхронными, чтобы они могли работать с сессией БД


async def create_organization(
    db_session: AsyncSession, **kwargs
) -> Organization:
    """Фабрика для создания Organization с дефолтными значениями."""
    defaults = {
        "name": "Тестовая Организация по Умолчанию",
        "short_name": "ТОУ",
        "inn": "1111111111",
        "okpo": "22222222",
        "okved": "22222222",
        "oksm_id": 123,
        "fns_code_id": 40590,
    }
    defaults.update(kwargs)

    organization = Organization(**defaults)
    db_session.add(organization)
    await db_session.flush()
    return organization


async def create_user(db_session: AsyncSession, **kwargs) -> User:
    """Фабрика для создания User."""
    if "org_id" not in kwargs:
        org = await create_organization(db_session)
        kwargs["org_id"] = org.id

    if "status_id" not in kwargs:
        status = await db_session.get(UserStatus, 1)
        if not status:
            status = UserStatus(id=1, name="active", description="Active user")
            db_session.add(status)
            await db_session.flush()
        kwargs["status_id"] = status.id

    defaults = {
        "uid": "test-user-uid",
        "username": "testuser",
        "password_hash": "some_strong_hash",
        # "status_id": "обновится",
        "auth_token": "some_auth_token",
        "password_reset_token": "some_reset_token",
        "verification_token": "some_verification_token",
        # "org_id": "тут тоже обновится",
        "position": "Главный Тестировщик",
    }
    defaults.update(kwargs)

    user = User(**defaults)
    db_session.add(user)
    await db_session.flush()
    return user


async def create_enquiry(db_session: AsyncSession, **kwargs) -> Enquiry:
    """Фабрика для создания Enquiry."""
    if "user_id" not in kwargs:
        user = await create_user(db_session)
        kwargs["user_id"] = user.id
    if "templates" not in kwargs:
        test_template = await create_template(db_session)
        kwargs["templates"] = [test_template]
    defaults = {
        "title": "Тестовая справка по умолчанию",
        "description": "Описание по умолчанию",
    }
    defaults.update(kwargs)

    enquiry = Enquiry(**defaults)
    db_session.add(enquiry)
    await db_session.flush()
    return enquiry


async def create_template(
    db_session: AsyncSession, **kwargs
) -> EnquiryTemplate:
    """Фабрика для создания EnquiryTemplate."""
    if "user_id" not in kwargs:
        user = await create_user(db_session)
        kwargs["user_id"] = user.id

    defaults = {
        "title": "Тестовый шаблон XLSX",
        "description": "Описание шаблона",
        "template_file_path": "/default/path/template.xlsx",
    }
    defaults.update(kwargs)

    template = EnquiryTemplate(**defaults)
    db_session.add(template)
    await db_session.flush()
    return template
