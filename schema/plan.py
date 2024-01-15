from datetime import datetime
from typing import Type

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from schema.database import engine
from schema.location import Location
from schema.user import User
from schema.common import batch_query

Base = declarative_base()
Session = sessionmaker(bind=engine)


class Plan(Base):
    __tablename__ = 'plan'
    id = Column(Integer, primary_key=True, autoincrement=True)
    lid = Column(Integer, ForeignKey("location.id", ondelete="CASCADE"), comment="基地", name="location")

    create_people = Column(String(50), comment="创建人", name="create_people")
    year = Column(Integer, nullable=False, comment="年份", name="year")
    batch = Column(Integer, nullable=True, comment="批次", name="batch")
    total_material = Column(Integer, comment="总加工原料(KG)", name="total_material")
    total_product = Column(Integer, comment="成品总量(L)", name="total_product")
    surplus_product = Column(Integer, comment="剩余发货量(L)", name="surplus_product")
    notices = Column(Text, comment="备注", name="notices")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")


class PlantSegment(Base):
    __tablename__ = 'segment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey('plan.id'))

    name = Column(String(50), nullable=False, comment="种植环节", name="name")

    operate = relationship("PlantOperate", backref="segment")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")


class PlantOperate(Base):
    __tablename__ = 'operate'
    id = Column(Integer, primary_key=True, autoincrement=True)
    segment_id = Column(Integer, ForeignKey('segment.id'))

    name = Column(String(50), nullable=False)

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")


class Transport(Base):
    __tablename__ = "transport"  # noqa 原料运输
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey('plan.id'))

    operate_date = Column(DateTime, default=datetime.now, comment="计划操作日期", name="operate_date")
    loading_worker = Column(String(50), comment="装车人员", name="loading_worker")
    driver = Column(String(50), comment="运输人员", name="driver")
    unload_worker = Column(String(50), comment="卸货人员", name="unload_worker")
    unload_place = Column(String(50), comment="卸货地点", name="unload_place")
    air_worker = Column(String(50), comment="晾晒人员", name="air_worker")
    clean_worker = Column(String(50), comment="清选人员", name="clean_worker")
    after_clean_driver = Column(String(50), comment="清选后运输人员", name="after_clean_driver")
    after_unload_worker = Column(String(50), comment="清选后卸货人员", name="after_unload_worker")
    after_unload_place = Column(String(50), comment="清选后卸货地点", name="after_unload_place")
    notices = Column(Text, comment="备注", name="notices")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")


class Warehouse(Base):
    __tablename__ = "warehouse"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey('plan.id'))

    operate_date = Column(DateTime, default=datetime.now, comment="计划操作日期", name="operate_date")
    feeding_place = Column(String(50), comment="投料口转运", name="feeding_place")
    feeding_warehouse = Column(String(50), comment="投料仓转运地点", name="feeding_warehouse")
    feeding = Column(String(50), comment="投料", name="feeding")
    press = Column(String(50), comment="压榨", name="press")
    refine = Column(String(50), comment="精炼", name="refine")
    sorting = Column(String(50), comment="分装", name="sorting")
    warehousing = Column(String(50), comment="入库", name="Warehousing")
    product_warehousing = Column(String(50), comment="成品入库地点", name="product_warehousing")
    notices = Column(Text, comment="备注", name="notices")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")


class Logistics(Base):
    __tablename__ = "logistics"  # noqa 物流运输
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey('plan.id'))

    operate_date = Column(DateTime, default=datetime.now, comment="计划操作日期", name="operate_date")
    operate_people = Column(String(50), comment="操作人员", name="operate_people")
    order_num = Column(String(250), comment="发货订单", name="order_num")
    notices = Column(Text, comment="备注", name="notices")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")



