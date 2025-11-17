from fastapi import APIRouter
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String
import hashlib
from fastapi.responses import JSONResponse
import logging

# Определение модели
Base = declarative_base()

router = APIRouter(
    prefix="/enquiry/api/v1",
    tags=["Enquiries"],
)


class User(Base):
    __table_args__ = {'schema': 'diplom'}
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    lastname = Column(String)
    email = Column(String)
    login = Column(String)
    passw = Column(String)


@router.post("/registration")
def create_user(name_f, lastname_f, email_f, login_f, pass_f):
    session = get_session()
    pass_f_hash = hash_func(bytes(pass_f, 'utf-8'))
    user = User(name=name_f, lastname=lastname_f, email=email_f, login=login_f, passw=pass_f_hash)
    session.add(user)
    session.commit()
    return JSONResponse(
        content={"message": "User created"},
        status_code=201
    )

@router.post("/deleteuser")
def delete_user(id_back):
    session = get_session()
    #pass_f_hash = hash_func(bytes(pass_f, 'utf-8'))
    #user = User(name=name_f, lastname=lastname_f, email=email_f, login=login_f, passw=pass_f_hash)
    user = session.query(User).filter_by(id=id_back).first()
    if user is None:
        return JSONResponse(
            content={"message":"User not found"},
            status_code=404
        )
    else:
        session.delete(user)
        session.commit()
        return JSONResponse(
            content={"message": "User deleted"},
            status_code=200
        )


@router.get("/users",
            description="Получение списка всех пользователей",
            summary="Показать список всех пользователей")
def get_users():
    session = get_session()
    users = session.query(User).all()
    result = [u.__dict__ for u in users]
    for r in result:
        r.pop('_sa_instance_state', None)
    return result


@router.get("/users/{user_id}",
            description="Получение информации о пользователе по id",
            summary="Получить информацию о пользователе")
def get_user(user_id: int):
    session = get_session()
    # users = session.query(User).all()
    user = session.query(User).filter_by(id=user_id).first()
    if user is None:
        return JSONResponse(
            content={"message": "User not found"},
            status_code=404
        )
    else:
        data = user.__dict__.copy()
        data.pop('_sa_instance_state', None)
        data.pop('login', None)
        data.pop('passw', None)
        return data


def get_users_one(login_for):
    session = get_session()
    # session.get()
    # print("Схемы:", session.get(User,1))
    # Способ 1: query().all()
    # users = session.query(User).all()
    user = session.query(User).filter_by(login=login_for).first()
    if user is None:
        return JSONResponse(
            content={"message": "User not found"},
            status_code=404
        )
    else:
        return user.passw
    # print("Пользак", user.login)
    # return user.passw
    # for user in users:
    #   print(f"ID: {user.id}, Name: {user.name}")


@router.get("/authorization")
def check_user_pass(login_f, pass_f):
    passw_bd = get_users_one(login_f)
    password_f = hash_func(bytes(pass_f, 'utf-8'))
    # print("Хэш пароль с фронта", password_f)
    if passw_bd == password_f:
        return JSONResponse(
            content={"message": "Authorization OK"},
            status_code=200
        )
    else:
        return JSONResponse(
            content={"message": "Authorization Not OK"},
            status_code=403
        )


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
