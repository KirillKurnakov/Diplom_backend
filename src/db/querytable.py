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
    #engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    #__table__ = Table('pfhd_spravki', Base.metadata, autoload_with=engine, schema='diplom')
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
    #engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    #__table__ = Table('pfhd_spravki', Base.metadata, autoload_with=engine, schema='diplom')
    __table_args__ = {'schema': 'cbias_spravki'}
    __tablename__ = 'fk_form'

    total = Column(Float)
    blocksubbo_inn = Column(String, primary_key=True)
    strcode = Column(String)
    codeanalytic = Column(String)
    period = Column(String)
    periodicity = Column(String)

class protocols(authorizeModule.Base):
    #engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    #__table__ = Table('pfhd_spravki', Base.metadata, autoload_with=engine, schema='diplom')
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
    limit_str=10000
    session = get_session()
    pfhds = session.query(Pfhd).limit(limit_str).all()
    #pfhds = session.query(Pfhd).all()

    result = [u.__dict__ for u in pfhds]
    for r in result:
        r.pop('_sa_instance_state', None)

    return result

@router.get("/getfkform",
            description="Получение данных по 737 форме",
            summary="Получение данных по 737 форме")
def get_fkform():
    limit_str=10000
    session = get_session()
    pfhds = session.query(fkform).limit(limit_str).all()
    #pfhds = session.query(Pfhd).all()

    result = [u.__dict__ for u in pfhds]
    for r in result:
        r.pop('_sa_instance_state', None)

    return result

@router.get("/getprotocols",
            description="Получение данных по Протоколам БК",
            summary="Получение данных по Протоколам БК")
def get_protocols():
    limit_str=10000
    session = get_session()
    pfhds = session.query(protocols).limit(limit_str).all()
    #pfhds = session.query(Pfhd).all()

    result = [u.__dict__ for u in pfhds]
    for r in result:
        r.pop('_sa_instance_state', None)
        r.pop('protocols_id', None)

    return result

@router.get("/api/pfhd-chart")
def get_pfhd_chart():
    session = get_session()
    limit_str = 50000
    session = get_session()
    rows = session.query(Pfhd).limit(limit_str).all()

    #rows = session.query(Pfhd).all()

    # Сортируем по году
    rows_sorted = sorted(rows, key=lambda x: x.finyear)

    years = [r.finyear for r in rows_sorted]
    values = [r.sumcurfinyear for r in rows_sorted]

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


