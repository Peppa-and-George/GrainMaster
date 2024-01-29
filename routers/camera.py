from datetime import datetime
from typing import Literal, Union

from fastapi import APIRouter, status, Body
from fastapi.responses import JSONResponse

from models.base import CameraSchema
from schema.common import page_with_order, transform_schema
from schema.tables import Camera
from schema.database import SessionLocal

from utils.camera_fetch import (
    get_all_camera_m3u8url,
    is_expired_date,
    date_string_to_datetime,
)

camera_router = APIRouter()


@camera_router.get("/get_camera", summary="批量获取摄像头信息")
async def get_camera(
    order_field: str = "id",
    order: Literal["asc", "desc"] = "asc",
    page: int = 1,
    page_size: int = 10,
):
    """
    # 批量获取摄像头信息
    - **order_field**: 排序字段
    - **order**: 排序方式
    - **page**: 页码
    - **page_size**: 每页数量
    """
    update_token()
    with SessionLocal() as session:
        query = session.query(Camera)
        response = page_with_order(
            schema=CameraSchema,
            query=query,
            page=page,
            page_size=page_size,
            order_field=order_field,
            order=order,
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


@camera_router.post("/add_camera", summary="添加摄像头")
async def add_camera(
    name: str,
    sn: str,
    device_status: str,
    expire_time: str,
    stream_url: str,
    location: str,
    address: str,
):
    """
    # 添加摄像头
    - **name**: 摄像头名称
    - **sn**: 摄像头序列号
    - **device_status**: 摄像头状态
    - **expire_time**: 摄像头过期时间
    - **stream_url**: 摄像头流地址
    - **location**: 摄像头位置
    - **address**: 摄像头地址
    """
    with SessionLocal() as session:
        cam = Camera(
            name=name,
            sn=sn,
            status=device_status,
            expire_time=datetime.strptime(expire_time, "%Y-%m-%d %H:%M:%S"),
            stream_url=stream_url,
            location=location,
            address=address,
        )
        session.add(cam)
        session.commit()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "添加成功"})


@camera_router.get("/filter_camera", summary="根据条件筛选摄像头")
async def filter_camera(
    name: str = None,
    alise_name: str = None,
    sn: str = None,
    device_status: str = None,
    location: str = None,
    address: str = None,
    fuzzy: bool = False,
    order_field: str = "id",
    order: Literal["asc", "desc"] = "asc",
    page: int = 1,
    page_size: int = 10,
):
    """
    # 根据条件筛选摄像头
    - **name**: 摄像头名称, 可选
    - **alise_name**: 摄像头别名, 可选
    - **sn**: 摄像头序列号, 可选
    - **device_status**: 摄像头状态, 可选
    - **location**: 摄像头位置, 可选
    - **address**: 摄像头地址, 可选
    - **fuzzy**: 是否模糊查询
    - **order_field**: 排序字段
    - **order**: 排序方式
    - **page**: 页码
    - **page_size**: 每页数量
    """
    with SessionLocal() as session:
        query = session.query(Camera)
        if name:
            if fuzzy:
                query = query.filter(Camera.name.like(f"%{name}%"))
            else:
                query = query.filter(Camera.name == name)
        if alise_name:
            if fuzzy:
                query = query.filter(Camera.alise_name.like(f"%{alise_name}%"))
            else:
                query = query.filter(Camera.alise_name == alise_name)
        if sn:
            if fuzzy:
                query = query.filter(Camera.sn.like(f"%{sn}%"))
            else:
                query = query.filter(Camera.sn == sn)
        if device_status:
            query = query.filter(Camera.status == device_status)
        if location:
            query = query.filter(Camera.location == location)
        if address:
            query = query.filter(Camera.address == address)
        response = page_with_order(
            schema=CameraSchema,
            query=query,
            page=page,
            page_size=page_size,
            order_field=order_field,
            order=order,
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content=response)


def update_token():
    with SessionLocal() as session:
        camera_first = session.query(Camera).first()
        if camera_first:  # 摄像头表有数据
            camera_second = session.query(Camera).filter(Camera.status == 1).first()
            # 随便查一个在线的摄像头看url是否过期
            if is_expired_date(camera_second.expire_time):
                camera_list = get_all_camera_m3u8url()
                for camera in camera_list:
                    cam = (
                        session.query(Camera)
                        .filter(Camera.sn == camera["deviceSerial"])
                        .first()
                    )
                    cam.expired = date_string_to_datetime(camera["expire_time"])
                    cam.status = camera["status"]
                    cam.stream_url = camera["url"]
                session.commit()
        else:
            # 没有摄像头数据
            camera_list = get_all_camera_m3u8url()
            for camera in camera_list:
                if camera["status"] == 1:  # 在线设备才有过期时间和url
                    cam = Camera(
                        alise_name=camera["deviceName"],
                        sn=camera["deviceSerial"],
                        status=camera["status"],
                        expire_time=date_string_to_datetime(camera["expire_time"]),
                        stream_url=camera["url"],
                    )
                    session.add(cam)
                elif camera["status"] == 0:  # 离线设备没有
                    cam = Camera(
                        alise_name=camera["deviceName"],
                        sn=camera["deviceSerial"],
                        status=camera["status"],
                    )
                    session.add(cam)
            session.commit()


@camera_router.put("/update_camera", summary="更新摄像头信息")
async def update_camera(
    camera_id: int = Body(..., description="摄像头id"),
    name: Union[str] = Body(None, description="摄像头名称"),
    alise_name: Union[str] = Body(None, description="摄像头别名"),
    sn: Union[str] = Body(None, description="摄像头序列号"),
    device_status: Union[str] = Body(None, description="摄像头状态"),
    expire_time: Union[str] = Body(None, description="摄像头过期时间"),
    stream_url: Union[str] = Body(None, description="摄像头流地址"),
    location: Union[str] = Body(None, description="摄像头位置"),
    address: Union[str] = Body(None, description="摄像头地址"),
):
    """
    # 更新摄像头信息
    - **camera_id**: 摄像头id
    - **name**: 摄像头名称, 可选
    - **alise_name**: 摄像头别名, 可选
    - **sn**: 摄像头序列号, 可选
    - **device_status**: 摄像头状态, 可选
    - **expire_time**: 摄像头过期时间, 可选
    - **stream_url**: 摄像头流地址, 可选
    - **location**: 摄像头位置, 可选
    - **address**: 摄像头地址, 可选
    """
    with SessionLocal() as session:
        cam = session.query(Camera).filter(Camera.id == camera_id).first()
        if cam:
            if name:
                cam.name = name
            if alise_name:
                cam.alise_name = alise_name
            if sn:
                cam.sn = sn
            if device_status:
                cam.status = device_status
            if expire_time:
                cam.expire_time = datetime.strptime(expire_time, "%Y-%m-%d %H:%M:%S")
            if stream_url:
                cam.stream_url = stream_url
            if location:
                cam.location = location
            if address:
                cam.address = address
            session.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"message": "更新成功"}
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content={"message": "更新失败"}
            )


@camera_router.delete("/delete_camera", summary="删除摄像头")
async def delete_camera(
    camera_id: int = Body(..., description="摄像头id"),
):
    with SessionLocal() as session:
        cam = session.query(Camera).filter(Camera.id == camera_id).first()
        if cam:
            session.delete(cam)
            session.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"message": "删除成功"}
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST, content={"message": "删除失败"}
            )
