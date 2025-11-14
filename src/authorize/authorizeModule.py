from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
import hashlib

# Определение модели
Base = declarative_base()

class User(Base):
    __tablename__ = 'newtable'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    # email = Column(String)

def hash_func(password):
    # создаем объект хэширования
    hash_object = hashlib.sha256()

    # обновление объета хэширования данными
    hash_object.update(password)

    # получение хэша в 16-ном виде
    hex_dig = hash_object.hexdigest()
    return hex_dig

def get_session():
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    # Создание фабрики сессий
    # Указываем тип сессии и движок
    Session = sessionmaker(bind=engine)

    # Создание экземпляра сессии
    session = Session()

    return session

