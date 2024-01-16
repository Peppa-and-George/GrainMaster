from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Boolean, desc, asc, FLOAT, ForeignKey, Text

from sqlalchemy.orm import declarative_base

from models.product import QueryProductsModel, QueryProductByNameModel
from schema.common import batch_query
from schema.database import engine
from schema.plan import Plan
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker(bind=engine)


class Quality(Base):
    __tablename__ = "quality"  # noqa
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    p_id = Column(Integer, ForeignKey("plan.id"))
    name = Column(String(50), nullable=False, comment="报告名称", name="name")
    people = Column(String(50), nullable=False, comment="上传人", name="people")
    status = Column(String(50), default="未上传", comment="上传状态", name="status")
    report = Column(Text, comment="文件路径", name="report")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间", name="create_time")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间", name="update_time")
