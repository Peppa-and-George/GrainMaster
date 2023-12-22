from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Float

from schema.database import Base


class User(Base):
    __tablename__ = "users"  # noqa

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False, comment="用户名")
    phone_number = Column(Integer, nullable=False, comment="手机号")
    hashed_passwd = Column(String)

    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now)


class Product(Base):
    __tablename__ = "product" # noqa

    product_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False, comment="产品名称")
    introduction = Column(String, index=True, nullable=False, comment="产品介绍")
    price = Column(Integer, nullable=False, comment="价格")
    unit = Column(String, index=True, nullable=False, comment="规格(L)")

    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now)

