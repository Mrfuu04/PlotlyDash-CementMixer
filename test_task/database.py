import pandas as pd
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    Integer,
    String,
    Time,
    create_engine,
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
)

from test_task.settings import (
    DB_PATH,
)

Base = declarative_base()


class DB:
    """Класс для работы с БД."""

    def __init__(self):
        engine = create_engine(f"sqlite:///{DB_PATH}")

        Session = sessionmaker(bind=engine)
        self.session = Session()

    class Sources(Base):
        """Таблица sources."""

        __tablename__ = 'sources'

        endpoint_id = Column(Integer, primary_key=True, unique=False)
        client_name = Column(String)
        endpoint_name = Column(String)
        shift_day = Column(Date)
        calendar_day = Column(Date)
        state = Column(String)
        status = Column(String)
        reason = Column(String)
        state_begin = Column(DateTime)
        state_end = Column(DateTime)
        duration_hour = Column(Float)
        duration_min = Column(Float)
        color = Column(String)
        period_name = Column(String)
        shift_name = Column(String)
        operator = Column(String)
        operator_auth_start = Column(DateTime)
        operator_auth_end = Column(DateTime)
        shift_begin = Column(Time)
        shift_end = Column(Time)


class DataCollector:
    """Используется для сбора данных из БД."""

    def __init__(self):
        self.db = DB()

    def get_first_client_name(self):
        """Используется в качестве тестового примера для выборки первого
        (и единственного уникального) значения client_name из таблицы sourses.

        Returns:
            str: Имя первого клиента в таблице sourses"""

        client_name = self.db.session.query(
            self.db.Sources,
        ).first().client_name

        return client_name

    def get_data(self):
        """Возвращает все данные из таблицы sources отфильтрованные по client_name.

        Returns:
            list: Список кортежей с полученными данными."""

        data = self.db.session.query(
            self.db.Sources.__table__.columns,
        ).all()

        return data

    def get_dataframe(self):
        """Возвращает готовый датафрейм с данными из таблицы sources,
        отсортированными по client_name.

        Returns:
            DataFrame: Готовый датафрейм для работы.
        """

        data = self.get_data()

        return pd.DataFrame(data)
