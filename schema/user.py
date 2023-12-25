from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean

from schema.database import Base


class User(Base):
    __tablename__ = "users"  # noqa

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False, comment="用户名", name="name")
    phone_number = Column(Integer, nullable=False, comment="手机号", name="phone_number")
    hashed_passwd = Column(String, nullable=False, comment="密码", name="hashed_passwd")

    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now)
