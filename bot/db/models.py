
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Auth(Base):
    __tablename__ = 'auth'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger)
    email = Column(String)
    access_token = Column(String)
    refresh_token = Column(String)
    auth_date = Column(DateTime, default=datetime.utcnow)
