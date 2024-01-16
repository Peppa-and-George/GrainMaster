from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship, create_session, declarative_base
from datetime import datetime
from schema.product import Product
from schema.client import Client, Address
from schema.plan import Plan

Base = declarative_base()


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("product.id"))
    plan_id = Column(Integer, ForeignKey("plan.id"))
    client_id = Column(Integer, ForeignKey("client.id"))

    order_num = Column(String(100), unique=True, nullable=False, comment="订单编号", name="order_num")
    num = Column(Integer, nullable=False, comment="数量", name="order_num")
    status = Column(String(100), nullable=False, comment="状态", name="order_num")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")

    order_address = relationship("OrderAddress", backref="order")

class OrderAddress(Base):
    __tablename__ = "order_address"
    id = Column(Integer, primary_key=True, autoincrement=True)
    address_id = Column(Integer, ForeignKey("address.id"))
    order_id = Column(Integer, ForeignKey("order.id"))

    status = Column(String(100), nullable=False, comment="发货状态", name="status")
    express_num = Column(String(200), nullable=False, comment="物流单号", name="express_num")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")
