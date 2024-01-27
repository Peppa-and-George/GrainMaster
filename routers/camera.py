from datetime import datetime
from typing import Literal
import uuid

from fastapi import APIRouter, Query, HTTPException, status, Body
from fastapi.responses import JSONResponse

from schema.common import page_with_order, transform_schema
from schema.tables import Camera
from schema.database import SessionLocal
from models.base import ClientSchema, AddressSchema

from utils.camera_fetch import get_all_camera_m3u8url, is_expired_date, date_string_to_datetime

camera_router = APIRouter()
session = SessionLocal()

@camera_router.get("/get_camera", summary="批量获取摄像头信息")
async def get_camera(
        order_field: str = "id",
        order: Literal["asc", "desc"] = "asc",
        page: int = 1,
        page_size: int = 10,
):
    update_camera()
    query = session.query(Camera)
    response = page_with_order(
        schema="", # todo 缺一个schema
        query=query,
        page=page,
        page_size=page_size,
        order_field=order_field,
        order=order,
    )

    return JSONResponse(status_code=status.HTTP_200_OK, content=response)



def update_camera():
    camera_first = session.query(Camera).first()
    if camera_first:    # 摄像头表有数据
        camera_second = session.query(Camera).filter(Camera.status==1).first()
        # 随便查一个在线的摄像头看url是否过期
        if is_expired_date(camera_second.expire_time):
            camera_list = get_all_camera_m3u8url()
            for camera in camera_list:
                cam = session.query(Camera).filter("sn"==camera["deviceSerial"]).first()
                cam.expired = date_string_to_datetime(camera["expire_time"])
                cam.status = camera["status"]
                cam.stream_url = camera["url"]
            session.commit()
    else:
        # 没有摄像头数据
        camera_list = get_all_camera_m3u8url()
        for camera in camera_list:
            if camera["status"] == 1:   # 在线设备才有过期时间和url
                cam = Camera(
                    d_name=camera["deviceName"],
                    sn=camera["deviceSerial"],
                    status=camera["status"],
                    expire_time=date_string_to_datetime(camera["expire_time"]),
                    stream_url=camera["url"]
                )
                session.add(cam)
            elif camera["status"] == 0:     # 离线设备没有
                cam = Camera(
                    d_name=camera["deviceName"],
                    sn=camera["deviceSerial"],
                    status=camera["status"],
                )
                session.add(cam)
        session.commit()



update_camera()
