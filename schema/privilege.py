from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship, create_session, declarative_base
from datetime import datetime
from schema.client import Client

Base = declarative_base()


class Privilege(Base):
    __tablename__ = "privilege"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False, comment="权益名称", name='name')
    description = Column(String(250), comment="权益描述", name='description')
    expired_date = Column(String(250), comment="过期时间", name='expired_date')

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")

    client = relationship("Client", backref="privilege")


class PrivilegeInfo(Base):
    __tablename__ = "privilege_info"
    id = Column(Integer, primary_key=True, autoincrement=True)
    p_id = Column(ForeignKey("privilege.id", ondelete="CASCADE"))

    name = Column(String(50), nullable=False, comment="权益项", name="address")
    description = Column(Text, nullable=False, comment="权益项描述", name="phone_num")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")

    privilege_table = relationship("privilege_table", backref="privilege_info")

class PrivilegeTable(Base):
    __tablename__ = "privilege_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pi_id = Column(ForeignKey("privilege_info.id"))

    num = Column(Integer, nullable=False, comment="剩余数量", name="number")