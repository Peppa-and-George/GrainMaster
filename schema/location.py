from datetime import datetime
from typing import Type

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from schema.database import engine
from schema.common import batch_query
from models.location import (
    BatchQueryLocationsModel,
    LocationNecessaryFields,
    FilterLocationModel,
)

Base = declarative_base()
Session = sessionmaker(bind=engine)


class Location(Base):
    __tablename__ = "location"  # noqa

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), index=True, nullable=False, comment="位置名称", name="name")
    type = Column(String(128), nullable=False, comment="位置类型", name="type")
    detail = Column(String(128), nullable=False, comment="位置详情", name="detail")
    longitude = Column(Float, nullable=False, comment="经度", name="longitude")
    latitude = Column(Float, nullable=False, comment="纬度", name="latitude")
    area = Column(Float, nullable=True, comment="面积", name="area")
    customized = Column(String(16), nullable=True, comment="是否定制", name="customized")
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )


def query_locations(params: BatchQueryLocationsModel) -> dict:
    query, total = batch_query(Location, params)
    return {
        "total": total,
        "data": query.all(),
        "page": params.page,
        "page_size": params.page_size,
        "order_field": params.order_field,
        "order": params.order,
    }


def add_location(location: LocationNecessaryFields) -> None:
    with Session() as session:
        location = Location(**location.model_dump())
        session.add(location)
        session.commit()


def delete_location(location_id: int) -> int:
    with Session() as session:
        deleted_row = location = (
            session.query(Location).filter_by(id=location_id).delete()
        )
        session.commit()
        return deleted_row


def get_location_by_id(location_id: int) -> Type[Location] | None:
    with Session() as session:
        location = session.query(Location).filter_by(id=location_id).first()
        return location


def filter_location(params: FilterLocationModel) -> dict:
    with Session() as session:
        query = session.query(Location)
        if params.fuzzy:
            query = (
                query.filter(Location.name.like(f"%{params.name}%"))
                if params.name
                else query
            )
            query = (
                query.filter(Location.type.like(f"%{params.type}%"))
                if params.type
                else query
            )
            query = (
                query.filter(Location.customized.like(f"%{params.customized}%"))
                if params.customized
                else query
            )
        else:
            query = query.filter(Location.name == params.name) if params.name else query
            query = query.filter(Location.type == params.type) if params.type else query
            query = (
                query.filter(Location.customized == params.customized)
                if params.customized
                else query
            )
        query, total = batch_query(
            Location,
            BatchQueryLocationsModel(
                page=params.page,
                page_size=params.page_size,
                order_field=params.order_field,
                order=params.order,
            ),
            query,
        )
        return {
            "total": total,
            "data": query.all(),
            "page": params.page,
            "page_size": params.page_size,
            "order_field": params.order_field,
            "order": params.order,
        }


def update_location(location_id: int, location: LocationNecessaryFields) -> int:
    with Session() as session:
        updated_rows = (
            session.query(Location)
            .filter_by(id=location_id)
            .update(location.model_dump(exclude_unset=True))
        )
        session.commit()
        return updated_rows
