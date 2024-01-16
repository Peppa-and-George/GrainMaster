from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship, create_session, declarative_base
from datetime import datetime
from schema.privilege import Privilege

Base = declarative_base()


class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True, autoincrement=True)
    privilege_id = Column(Integer, ForeignKey("privilege.id"))

    account = Column(String(32), nullable=False, comment="账号", name='account')
    name = Column(String(32), nullable=False, comment="账号名", name='name')
    status = Column(Boolean, nullable=False, default=False, comment="激活状态", name='status')
    category = Column(String(32), nullable=False, comment="客户类型", name="category")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")
    delete_time = Column(DateTime, onupdate=datetime.now, comment="删除时间", name="delete_time")
    is_deleted = Column(Boolean, default=False, comment="是否删除", name="is_deleted")

    orders = relationship("Order", backref="client")

class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, autoincrement=True)
    c_id = Column(ForeignKey("client.id", ondelete="CASCADE"), comment="客户")

    name = Column(Text, nullable=False, comment="收货人", name="address")
    phone_num = Column(Integer, nullable=False, comment="手机号", name="phone_num")
    address = Column(Text, nullable=False, comment="地址", name="address")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")
