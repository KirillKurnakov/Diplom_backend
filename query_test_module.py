from sqlalchemy import (
    Column,
    Date,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
)

"""
вставлять в utils на 42 строку под инициилизированной сессией
"""
if query.database_id == 5 or query.database_id == "5":
    metadata = MetaData()
    uslugirabota = uslugirabota = Table(
        "uslugirabota",
        metadata,
        # Явно описываем ТОЛЬКО те колонки, которые нам нужны
        Column("report_date", Date),
        Column("year", String),
        Column("inn", String),
        Column("work_group", String),
        Column("number", Integer),  # или какой там тип
        Column("volume_hours", Numeric),
        Column("fogz", Numeric),
        schema="cbias_spravki",
    )
    u = uslugirabota.alias("u")
    subquery_2023 = (
        select(func.max(uslugirabota.c.report_date))
        .where(uslugirabota.c.year == "2023")
        .scalar_subquery()
    )
    subquery_2024 = (
        select(func.max(uslugirabota.c.report_date))
        .where(uslugirabota.c.year == "2024")
        .scalar_subquery()
    )
    subquery_2025 = (
        select(func.max(uslugirabota.c.report_date))
        .where(uslugirabota.c.year == "2025")
        .scalar_subquery()
    )

    # Колонки
    columns_to_select = [
        func.row_number().over(order_by=u.c.number).label("row_num"),
        u.c.inn,
        u.c.work_group,
        func.sum(
            case(
                (
                    and_(
                        u.c.year == "2023", u.c.report_date.in_(subquery_2023)
                    ),
                    cast(u.c.volume_hours, Numeric),
                ),
                else_=0,
            )
        ).label("2023_k"),
        func.sum(
            case(
                (
                    and_(
                        u.c.year == "2024", u.c.report_date.in_(subquery_2024)
                    ),
                    cast(u.c.volume_hours, Numeric),
                ),
                else_=0,
            )
        ).label("2024_k"),
        func.sum(
            case(
                (
                    and_(
                        u.c.year == "2025", u.c.report_date.in_(subquery_2025)
                    ),
                    cast(u.c.volume_hours, Numeric),
                ),
                else_=0,
            )
        ).label("2025_k"),
        func.sum(
            case(
                (
                    and_(
                        u.c.year == "2023", u.c.report_date.in_(subquery_2023)
                    ),
                    cast(u.c.fogz, Numeric),
                ),
                else_=0,
            )
        ).label("2023_fo"),
        func.sum(
            case(
                (
                    and_(
                        u.c.year == "2024", u.c.report_date.in_(subquery_2024)
                    ),
                    cast(u.c.fogz, Numeric),
                ),
                else_=0,
            )
        ).label("2024_fo"),
        func.sum(
            case(
                (
                    and_(
                        u.c.year == "2025", u.c.report_date.in_(subquery_2025)
                    ),
                    cast(u.c.fogz, Numeric),
                ),
                else_=0,
            )
        ).label("2025_fo"),
    ]

    # Условие WHERE
    where_condition = and_(
        # u.c.inn == '7801021076',
        u.c.work_group.notin_(
            [
                "Музейные работы",
                "Библиотечные работы",
                "Паспортные работы",
                "Обеспечение проведения научных исследований",
                "Архивные работы",
                "Дополнительные общеразвивающие программы",
                "Дополнительные программы профпереподготовки",
                "Дошкольное образование",
                "Общее образование",
                "Содержание детей",
                "Архивные услуги",
                "Библиотечные услуги",
                "Медицинские услуги",
                "Музейные услуги",
                "Услуга по организации и проведению мероприятий",
            ]
        )
    )

    # Собираем все вместе
    stmt = (
        select(*columns_to_select)
        .select_from(u)
        .where(where_condition)
        .group_by(u.c.inn, u.c.work_group, u.c.number)
    )
    result = await session.execute(stmt)
    theResult = result.mappings().all()
    1
