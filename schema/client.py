from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship, create_session, declarative_base

Base = declarative_base()


class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, autoincrement=True)
    account = Column(String(32), nullable=False)
    status = Column(Boolean, nullable=False, default=False)
    category = Column(String(32), nullable=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    is_deleted = Column(Boolean)
    orders = relationship("Order", back_populates="client")
