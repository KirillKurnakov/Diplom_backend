from sqlalchemy import String, DATETIME

from fastapi import APIRouter
from sqlalchemy import text, create_engine, Column, Integer, Float, Table
from sqlalchemy.orm import sessionmaker, declarative_base

from src.authorize import authorizeModule

# Base = declarative_base()

router = APIRouter(
    prefix="/enquiry/api/v1",
    tags=["Enquiries"],
)


class Pfhd(authorizeModule.Base):
    # engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    # __table__ = Table('pfhd_spravki', Base.metadata, autoload_with=engine, schema='diplom')
    __table_args__ = {'schema': 'diplom'}
    __tablename__ = 'pfhd_spravki'

    inn = Column(String)
    id = Column(String, primary_key=True)
    strcode = Column(String)
    sumcurfinyear = Column(Float)
    sumfirstyearplper = Column(Float)
    sumsecondyearplper = Column(Float)
    finyear = Column(String)


class fkform(authorizeModule.Base):
    # engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    # __table__ = Table('pfhd_spravki', Base.metadata, autoload_with=engine, schema='diplom')
    __table_args__ = {'schema': 'cbias_spravki'}
    __tablename__ = 'fk_form'

    total = Column(Float)
    blocksubbo_inn = Column(String, primary_key=True)
    strcode = Column(String)
    codeanalytic = Column(String)
    period = Column(String)
    periodicity = Column(String)

class fkformchart(authorizeModule.Base):
    # engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    # __table__ = Table('pfhd_spravki', Base.metadata, autoload_with=engine, schema='diplom')
    __table_args__ = {'schema': 'cbias_spravki'}
    __tablename__ = 'fk_formchart'

    total = Column(Float)
    id = Column(Float, primary_key=True)
    strcode = Column(String)
    period = Column(String)

class protocols(authorizeModule.Base):
    # engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    # __table__ = Table('pfhd_spravki', Base.metadata, autoload_with=engine, schema='diplom')
    __table_args__ = {'schema': 'cbias_spravki'}
    __tablename__ = 'protocols'

    protocols_id = Column(String)
    report_date = Column(DATETIME)
    year_finance = Column(String)
    kbk = Column(String)
    subsidyictype = Column(String)
    inn = Column(String, primary_key=True)
    finance = Column(Float)
    taxes = Column(Float)
    finance_without_tax = Column(Float)


class protocolschart(authorizeModule.Base):
    # engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    # __table__ = Table('pfhd_spravki', Base.metadata, autoload_with=engine, schema='diplom')
    __table_args__ = {'schema': 'cbias_spravki'}
    __tablename__ = 'protocolschart'

    subsidyictype = Column(String, primary_key=True)
    finance = Column(Float)


def get_session():
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    # Создание фабрики сессий
    # Указываем тип сессии и движок
    Session = sessionmaker(bind=engine)

    # Создание экземпляра сессии
    session = Session()

    return session


@router.get("/getpfhd",
            description="Получение данных по ПФХД",
            summary="Получение данных по ПФХД")
def get_pfhd():
    limit_str = 10000
    session = get_session()
    pfhds = session.query(Pfhd).limit(limit_str).all()
    # pfhds = session.query(Pfhd).all()

    result = [u.__dict__ for u in pfhds]
    for r in result:
        r.pop('_sa_instance_state', None)

    return result


@router.get("/getfkform",
            description="Получение данных по 737 форме",
            summary="Получение данных по 737 форме")
def get_fkform():
    limit_str = 10000
    session = get_session()
    pfhds = session.query(fkform).limit(limit_str).all()
    # pfhds = session.query(Pfhd).all()

    result = [u.__dict__ for u in pfhds]
    for r in result:
        r.pop('_sa_instance_state', None)

    return result


@router.get("/getprotocols",
            description="Получение данных по Протоколам БК",
            summary="Получение данных по Протоколам БК")
def get_protocols():
    limit_str = 10000
    session = get_session()
    pfhds = session.query(protocols).limit(limit_str).all()
    # pfhds = session.query(Pfhd).all()

    result = [u.__dict__ for u in pfhds]
    for r in result:
        r.pop('_sa_instance_state', None)
        r.pop('protocols_id', None)

    return result


@router.get("/api/pfhd-chart")
def get_pfhd_chart():
    session = get_session()

    rows = session.query(Pfhd).all()

    # агрегируем по году
    data_by_year = {}

    for row in rows:
        year = str(row.finyear)
        value = float(row.sumcurfinyear or 0)

        if year not in data_by_year:
            data_by_year[year] = 0

        data_by_year[year] += round(round(value, 2) / 1000000, 2)

    # сортировка по году
    years = sorted(data_by_year.keys())

    values = [data_by_year[y] for y in years]

    return {
        "title": "ПФХД Данные по годам",
        "xtitle": "Годы",
        "ytitle": "Сумма текущий год",
        "categories": years,
        "series": [
            {
                "name": "sumcurfinyear",
                "data": values
            }
        ]
    }


@router.get("/api/protocols-chart")
def get_protocols_chart():
    session = get_session()

    rows = session.query(protocolschart).all()

    # # агрегируем по году
    data_by_year = {}
    #
    for row in rows:
        year = str(row.subsidyictype)
        value = float(row.finance or 0)

        if year not in data_by_year:
            data_by_year[year] = 0

        data_by_year[year] += round(value, 2)

    # # сортировка по году
    years = list(data_by_year.keys())
    #
    values = [data_by_year[y] for y in years]

    return {
        "title": "Протоколы БК данные по субсидиям",
        "xtitle": "Субсидии",
        "ytitle": "Сумма по субсидиям",
        "categories": years,
        "series": [
            {
                "name": "млн рублей",
                "data": values
            }
        ]
    }

@router.get("/api/fkform-chart")
def get_protocols_chart():
    session = get_session()  # Получаем сессию БД

    rows = session.query(fkformchart).all()

    # 1. Сбор уникальных категорий (strcode)
    categories = sorted(set(row.strcode for row in rows))

    # 2. Словарь: year -> { category: value } без defaultdict
    year_map = {}  # обычный словарь
    for row in rows:
        year = str(row.period)
        category = row.strcode
        value = float(row.total or 0)

        if year not in year_map:
            year_map[year] = {}  # создаём подсловарь для категорий

        if category not in year_map[year]:
            year_map[year][category] = 0.0  # инициализируем значение

        year_map[year][category] += value

    # 3. Формирование series
    series = []
    for year in sorted(year_map.keys()):
        data_for_year = [round(year_map[year].get(cat, 0), 2) for cat in categories]
        series.append({
            "name": f"{year}",
            "data": data_for_year
        })

    return {
        "chart": {"type": "bar"},
        "title": {"text": "Данные по субсидиям"},
        "xAxis": {
            "categories": categories,
            "title": {"text": None},
            "gridLineWidth": 1,
            "lineWidth": 0
        },
        "yAxis": {
            "min": 0,
            "title": {"text": "Сумма по субсидиям", "align": "high"},
            "labels": {"overflow": "justify"},
            "gridLineWidth": 0
        },
        "tooltip": {"valueSuffix": " млн рублей"},
        "plotOptions": {
            "bar": {
                "borderRadius": "50%",
                "dataLabels": {"enabled": True},
                "groupPadding": 0.1
            }
        },
        "legend": {
            "layout": "vertical",
            "align": "right",
            "verticalAlign": "top",
            "x": -40,
            "y": 80,
            "floating": True,
            "borderWidth": 1,
            "backgroundColor": "var(--highcharts-background-color, #ffffff)",
            "shadow": True
        },
        "credits": {"enabled": False},
        "series": series
    }
