from tokenize import String

from fastapi import APIRouter
from sqlalchemy import text, create_engine, Column, Integer, Float, Table
from sqlalchemy.orm import sessionmaker, declarative_base
from authorize import authorizeModule

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
    id = Column(String)
    strcode = Column(String)
    sumcurfinyear = Column(Float)
    sumfirstyearplper = Column(Float)
    sumsecondyearplper = Column(Float)
    finyear = Column(String)


def get_session():
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    # Создание фабрики сессий
    # Указываем тип сессии и движок
    Session = sessionmaker(bind=engine)

    # Создание экземпляра сессии
    session = Session()

    return session


@router.get("/getpfhd")
def get_pfhd():
    db = get_session()
    try:
        result = db.execute(text("SELECT * FROM diplom.pfhd_spravki")).mappings().all()
        return [dict(row) for row in result]  # JSON
    finally:
        db.close()
    # session = get_session()
    # pfhds = session.query(Pfhd).all()
    # result = [u.__dict__ for u in pfhds]
    # for r in result:
    #     r.pop('_sa_instance_state', None)
    # return result
