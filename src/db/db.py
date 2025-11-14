from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

# Определение модели
Base = declarative_base()

class test(Base):
    __tablename__ = 'newtable'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    # email = Column(String)

def get_session():
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')

    # Создание фабрики сессий
    # Указываем тип сессии и движок
    Session = sessionmaker(bind=engine)

    # Создание экземпляра сессии
    session = Session()

    return session

def get_schemas_sqlalchemy(connection_string):
    """
    Получает список схем из БД через SQLAlchemy.
    Пример строки подключения:
      PostgreSQL: postgresql://user:password@localhost:5432/dbname
      MySQL: mysql+pymysql://user:password@localhost:3306/dbname
      SQLite: sqlite:///path/to/file.db
    """
    try:
        engine = create_engine(connection_string)
        inspector = inspect(engine)
        return inspector.get_schema_names()
    except Exception as e:
        print(f"Ошибка при подключении: {e}")
        return []


# Пример использования
if __name__ == "__main__":
    #schemas = get_schemas_sqlalchemy("postgresql://postgres:postgres@localhost:5432/postgres")
    session=get_session()
    # session.get()
    #print("Схемы:", session.get(User,1))
    # Способ 1: query().all()
    users = session.query(test).all()
    print("Все пользователи (способ 1):")
    for user in users:
        print(f"ID: {user.id}, Name: {user.name}")
