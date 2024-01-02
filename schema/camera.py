from datetime import datetime

from models.camera import AddCameraModel, FilterCameraModel
from models.common import CommonQueryParm
from schema.common import batch_query

from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime
from schema.database import engine

Base = declarative_base()
Session = sessionmaker(bind=engine)


class Camera(Base):
    __tablename__ = "camera"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, index=True, name="name", comment="摄像头名称")
    sn = Column(String(64), nullable=False, name="sn", comment="摄像头序列号")
    # state = Enum(
    #     "online", "offline", "unknown", name="state", comment="摄像头状态", default="unknown"
    # )
    state = Column(String(32), nullable=False, name="state", comment="摄像头状态")
    address: str | None = Column(
        String(128), nullable=True, name="address", comment="摄像头地址"
    )
    location: str | None = Column(
        String(128), nullable=True, name="location", comment="摄像头位置"
    )
    step: str | None = Column(String(256), nullable=True, name="step", comment="所属环节")
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )


def query_cameras(params: CommonQueryParm) -> dict:
    """
    分页查询查询所有摄像头
    :param params: 查询参数
    """
    query, total = batch_query(Camera, params)
    cameras = query.all()
    return {
        "total": total,
        "data": cameras,
        "page": params.page,
        "page_size": params.page_size,
        "order_field": params.order_field,
        "order": params.order,
    }


def filter_cameras(params: FilterCameraModel) -> dict:
    """
    筛选摄像头
    :param params: 查询参数
    """
    with Session() as session:
        query = session.query(Camera)
        if params.fuzzy:
            query = (
                query.filter(Camera.name.like(f"%{params.name}%"))
                if params.name
                else query
            )
            query = (
                query.filter(Camera.address.like(f"%{params.address}%"))
                if params.address
                else query
            )
            query = (
                query.filter(Camera.step.like(f"%{params.step}%"))
                if params.step
                else query
            )
        else:
            query = query.filter(Camera.name == params.name) if params.name else query
            query = (
                query.filter(Camera.address == params.address)
                if params.address
                else query
            )
            query = query.filter(Camera.step == params.step) if params.step else query

        query, total = batch_query(Camera, params, query)
        cameras = query.all()
        return {
            "total": total,
            "data": cameras,
            "page": params.page,
            "page_size": params.page_size,
            "order_field": params.order_field,
            "order": params.order,
        }


def add_camera(params: AddCameraModel) -> None:
    """
    添加摄像头
    :param params: 查询参数
    """
    camera = Camera(
        name=params.name,
        sn=params.sn,
        state=params.state,
        address=params.address,
        location=params.location,
        step=params.step,
    )
    with Session() as session:
        session.add(camera)
        session.commit()


def delete_camera(camera_id: int) -> int:
    """
    删除摄像头
    :param camera_id: 摄像头id
    """
    with Session() as session:
        deleted_row = session.query(Camera).filter_by(id=camera_id).delete()
        session.commit()
        return deleted_row


def get_camera_by_id(camera_id: int) -> Camera | None:
    """
    根据id查询摄像头
    :param camera_id: 摄像头id
    """
    with Session() as session:
        camera = session.query(Camera).filter_by(id=camera_id).first()
        return camera


def update_camera(camera_id: int, params: AddCameraModel) -> int:
    """
    更新摄像头
    :param camera_id: 摄像头id
    :param params: 摄像头信息
    """
    with Session() as session:
        row_updated = (
            session.query(Camera)
            .filter_by(id=camera_id)
            .update(params.model_dump(exclude_unset=True))
        )
        session.commit()
        return row_updated
