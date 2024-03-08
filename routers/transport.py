# 原料运输
import json
from datetime import datetime
from typing import Literal, Optional, Union

from fastapi import (
    APIRouter,
    Query,
    status,
    Body,
    Form,
    UploadFile,
    File,
    HTTPException,
)
from fastapi.responses import JSONResponse

from routers.message import add_message
from schema.tables import Transport, Plan, Location, Quality, TransportSegment, Order
from schema.common import page_with_order, transform_schema
from schema.database import SessionLocal
from models.base import TransportSchema, TransportSegmentSchema
from dependency.image import save_upload_image, delete_image
from dependency.videos import save_video, delete_video

transport_router = APIRouter()


def query_segment(
    transport_id: int, transport_segment_type: Literal["原料", "装车", "运输", "卸货"]
) -> TransportSegment:
    with SessionLocal() as db:
        transport_segment = db.query(TransportSegment).filter(
            TransportSegment.transport_id == transport_id,
            TransportSegment.type == transport_segment_type,
        )
        if transport_segment.count() > 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"原料运输计划对应的运输环节重复，计划ID: {transport_id}， 环节类型: {transport_segment_type}",
            )
        elif transport_segment.count() == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"原料运输计划对应的运输环节缺失，计划ID: {transport_id}， 环节类型: {transport_segment_type}",
            )
        return transport_segment.first()


def update_transport_status(transport_id: int):
    with SessionLocal() as db:
        transport = db.query(Transport).filter(Transport.id == transport_id).first()
        segment = query_segment(transport_id, "卸货")
        if segment.completed:
            transport.status = "运输完成"
            db.commit()
            return

        segment = query_segment(transport_id, "运输")
        if segment.completed:
            transport.status = "运输中"
            db.commit()
            return

        transport.status = "准备运输"


@transport_router.get("/get_transports", summary="获取原料运输信息")
async def get_transports_api(
    transport_id: Optional[int] = Query(None, description="运输计划ID"),
    plan_id: Optional[int] = Query(None, description="计划ID"),
    location: Union[str, int, None] = Query(None, description="位置信息"),
    location_type: Literal["id", "name"] = Query(id, description="位置类型"),
    year: Optional[int] = Query(None, description="年份"),
    batch: Optional[int] = Query(None, description="批次"),
    transport_status: Literal["准备运输", "运输中", "运输完成"] = Query(None, description="运输状态"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("asc", description="排序方式"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    """
    # 批量获取运输信息
    ## params
    - **location_name**: 位置名称, 可选
    - **year**: 年份, 可选
    - **batch**: 批次, 可选
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认10，范围1-100, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    """
    try:
        with SessionLocal() as db:
            query = db.query(Transport).join(Plan, Plan.id == Transport.plan_id)
            if year:
                query = query.filter(Plan.year == year)
            if batch is not None:
                query = query.filter(Plan.batch == batch)
            if location:
                if location_type == "id":
                    query = query.filter(Plan.location_id == location)
                else:
                    query = query.join(
                        Location, Location.id == Plan.location_id
                    ).filter(Location.name == location)
            if transport_status:
                query = query.filter(Transport.status == transport_status)
            if transport_id:
                query = query.filter(Transport.id == transport_id)
            if plan_id:
                query = query.filter(Transport.plan_id == plan_id)
            response = page_with_order(
                schema=TransportSchema,
                query=query,
                page=page,
                page_size=page_size,
                order_field=order_field,
                order=order,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response,
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.get("/get_transport_segment", summary="获取运输环节信息")
async def get_transport_segment_api(
    transport_id: Optional[int] = Query(None, description="运输ID"),
    segment_id: Optional[int] = Query(None, description="运输环节ID"),
    segment_type: Literal["原料", "装车", "运输", "卸货", "all"] = Query(
        "all", description="环节类型"
    ),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("asc", description="排序方式"),
):
    """
    # 获取运输环节信息
    ## params
    - **transport_id**: 运输ID, int
    - **segment_id**: 运输环节ID, int, 可选
    - **segment_type**: 环节类型, str, 可选, 默认为"all", 可选值: "原料", "装车", "运输", "卸货", "all"
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认10，范围1-100, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    """
    try:
        with SessionLocal() as db:
            query = db.query(TransportSegment).join(
                Transport, Transport.id == TransportSegment.transport_id
            )
            if segment_id:
                query = query.filter(TransportSegment.id == segment_id)
            if transport_id:
                query = query.filter(TransportSegment.transport_id == transport_id)
            if segment_type != "all":
                query = query.filter(TransportSegment.type == segment_type)
            response = page_with_order(
                schema=TransportSegmentSchema,
                query=query,
                page=page,
                page_size=page_size,
                order_field=order_field,
                order=order,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response,
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.post("/add_transport", summary="添加运输信息")
async def add_transport_api(
    plan_id: int = Body(..., description="计划ID", examples=[1]),
    operate_time: str = Body(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="操作时间",
        examples=["2021-01-01 00:00:00"],
    ),
    remark: Optional[str] = Body("", description="备注"),
    notify: bool = Body(False, description="是否通知客户"),
):
    """
    # 添加运输信息
    ## params
    - **plan_id**: 计划ID, int
    - **operate_date**: 操作时间, str, 格式为"2021-01-01 00:00:00"
    - **remark**: 备注, str, 可选
    - **notify**: 是否通知客户, bool, 可选
    """
    try:
        with SessionLocal() as db:
            plan = db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "计划不存在"},
                )
            transport = Transport(
                operate_time=datetime.strptime(operate_time, "%Y-%m-%d %H:%M:%S"),
                remark=remark,
                status="准备运输",
            )

            quality = Quality(type="原料运输", status="未上传", name="原料运输质检报告")
            quality.plan = plan
            transport.qualities.append(quality)
            transport.plan = plan

            for segment_name in ["原料", "装车", "运输", "卸货"]:
                transport_segment = TransportSegment(type=segment_name)
                transport.segments.append(transport_segment)

            db.add(transport)
            db.commit()

            if notify:
                orders = (
                    db.query(Order.client_id)
                    .filter(Order.plan_id == plan_id)
                    .group_by(Order.client_id)
                    .all()
                )
                for o in orders:
                    add_message(
                        title="原料运输计划添加成功",
                        content=f"您的原料运输计划已经添加成功, 操作时间：{operate_time}, 当前状态：准备运输, 备注：{remark}",
                        sender="系统",
                        receiver_id=o[0],
                        message_type="添加原料运输计划",
                        tag=2,
                        details=json.dumps(
                            transform_schema(TransportSchema, transport)
                        ),
                    )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加成功"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.put("/update_transport_segment", summary="更新运输环节信息")
async def update_transport_segment_api(
    transport_segment_id: int = Body(..., description="运输环节ID"),
    operator: Optional[str] = Body(None, description="操作人"),
    operate_time: Optional[str] = Body(
        None, description="操作时间", examples=["2021-01-01 00:00:00"]
    ),
    operate_place: Optional[str] = Body(None, description="操作地点"),
    remarks: Optional[str] = Body(None, description="备注"),
    complete: Optional[bool] = Body(None, description="是否完成"),
    notify: bool = Body(False, description="是否通知客户"),
):
    """
    # 更新运输环节信息
    ## params
    - **transport_id**: 运输ID, int, 必填
    - **operator**: 操作人, str, 可选
    - **operate_date**: 操作时间, str, 可选
    - **operate_place**: 操作地点, str, 可选
    - **remarks**: 备注, str, 可选
    - **complete**: 是否完成, bool, 可选
    - **notify**: 是否通知客户, bool, 可选
    """
    try:
        with SessionLocal() as db:
            transport_segment = (
                db.query(TransportSegment)
                .filter(TransportSegment.id == transport_segment_id)
                .first()
            )
            if not transport_segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "运输环节信息不存在"},
                )
            if operator:
                transport_segment.operator = operator
            if operate_time:
                transport_segment.operate_time = datetime.strptime(
                    operate_time, "%Y-%m-%d %H:%M:%S"
                )
            if operate_place:
                transport_segment.operate_place = operate_place
            if remarks:
                transport_segment.remarks = remarks
            if complete is not None:
                transport_segment.completed = complete
                update_transport_status(transport_segment.transport_id)
            db.commit()
            if notify:
                orders = (
                    db.query(Order.client_id)
                    .join(Transport, Order.plan_id == Transport.plan_id)
                    .join(
                        TransportSegment, TransportSegment.transport_id == Transport.id
                    )
                    .filter(TransportSegment.id == transport_segment_id)
                    .group_by(Order.client_id)
                    .all()
                )
                for o in orders:
                    add_message(
                        title=f"{transport_segment.type}环节更新",
                        content=f"您的原料运输计划的{transport_segment.type}环节已经更新, 操作时间：{operate_time}",
                        sender="系统",
                        receiver_id=o[0],
                        message_type=f"原料运输环节更新",
                        tag=2,
                        details=json.dumps(
                            transform_schema(TransportSegmentSchema, transport_segment)
                        ),
                    )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "修改成功"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.post("/upload_file", summary="上传运输环节文件")
async def upload_file_api(
    transport_segment_id: int = Form(..., description="运输环节ID"),
    file_type: Literal["image", "video"] = Form("image", description="文件类型"),
    file: UploadFile = File(..., description="文件"),
    notify: bool = Form(False, description="是否通知客户"),
):
    """
    # 上传运输环节文件
    ## params
    - **transport_segment_id**: 运输环节ID, int
    - **file_type**: 文件类型, 枚举类型, 可选值: "image", "video"
    - **file**: 文件, 文件类型
    """
    try:
        with SessionLocal() as db:
            transport_segment = (
                db.query(TransportSegment)
                .filter(TransportSegment.id == transport_segment_id)
                .first()
            )
            if not transport_segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "运输环节信息不存在"},
                )
            if file_type == "image":
                if transport_segment.image_filename:
                    delete_image(transport_segment.image_filename)
                transport_segment.image_filename = save_upload_image(file)
            else:
                if transport_segment.video_filename:
                    delete_video(transport_segment.video_filename)
                transport_segment.video_filename = save_video(file)
            transport_segment.completed = True
            db.commit()
            if notify:
                orders = (
                    db.query(Order.client_id)
                    .join(Transport, Order.plan_id == Transport.plan_id)
                    .join(
                        TransportSegment, TransportSegment.transport_id == Transport.id
                    )
                    .filter(TransportSegment.id == transport_segment_id)
                    .group_by(Order.client_id)
                    .all()
                )
                for o in orders:
                    add_message(
                        title=f"{transport_segment.type}环节文件上传",
                        content=f"您的原料运输计划的{transport_segment.type}环节文件已经上传",
                        sender="系统",
                        receiver_id=o[0],
                        message_type=f"原料运输环节文件上传",
                        tag=2,
                        details=json.dumps(
                            transform_schema(TransportSegmentSchema, transport_segment)
                        ),
                    )
            # 更新运输状态
            update_transport_status(transport_segment.transport_id)

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "上传成功"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.delete("/delete_file", summary="删除运输环节文件")
async def delete_file_api(
    transport_segment_id: int = Query(..., description="运输环节ID"),
    file_type: Literal["image", "video", "all"] = Query("all", description="文件类型"),
    notify: bool = Query(False, description="是否通知客户"),
):
    """
    # 删除运输环节文件
    ## params
    - **transport_segment_id**: 运输环节ID, int
    - **file_type**: 文件类型, 枚举类型, 可选值: "image", "video", "all", 默认为"all",代表同时删除图片和视频
    - **notify**: 是否通知客户, bool, 可选
    """
    try:
        with SessionLocal() as db:
            transport_segment = (
                db.query(TransportSegment)
                .filter(TransportSegment.id == transport_segment_id)
                .first()
            )
            if not transport_segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "运输环节信息不存在"},
                )
            if notify:
                orders = (
                    db.query(Order.client_id)
                    .join(Transport, Order.plan_id == Transport.plan_id)
                    .join(
                        TransportSegment, TransportSegment.transport_id == Transport.id
                    )
                    .filter(TransportSegment.id == transport_segment_id)
                    .group_by(Order.client_id)
                    .all()
                )
                for o in orders:
                    add_message(
                        title=f"{transport_segment.type}环节文件删除",
                        content=f"您的原料运输计划的{transport_segment.type}环节文件已经删除, 文件类型: {file_type}",
                        sender="系统",
                        receiver_id=o[0],
                        message_type=f"原料运输环节文件删除",
                        tag=2,
                        details=json.dumps(
                            transform_schema(TransportSegmentSchema, transport_segment)
                        ),
                    )
            if file_type == "image":
                if transport_segment.image_filename:
                    delete_image(transport_segment.image_filename)
                transport_segment.image_filename = None
            elif file_type == "video":
                if transport_segment.video_filename:
                    delete_video(transport_segment.video_filename)
                transport_segment.video_filename = None
            else:
                if transport_segment.image_filename:
                    delete_image(transport_segment.image_filename)
                if transport_segment.video_filename:
                    delete_video(transport_segment.video_filename)
                transport_segment.image_filename = None
                transport_segment.video_filename = None
            if (
                not transport_segment.image_filename
                and not transport_segment.video_filename
            ):
                transport_segment.completed = False
            db.commit()
            update_transport_status(transport_segment.transport_id)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.put("/update_transport_status", summary="修改运输状态")
async def update_transport_status_api(
    transport_id: int = Body(..., description="运输ID"),
    transport_status: Literal["准备运输", "运输中", "运输完成"] = Body(..., description="状态"),
    notify: bool = Body(False, description="是否通知客户"),
):
    """
    # 修改运输状态
    ## params
    - **transport_id**: 运输ID, int
    - **transport_status**: 状态, 枚举类型, 可选值: "准备运输", "运输中", "运输完成"
    - **notify**: 是否通知客户, bool, 可选
    """
    try:
        with SessionLocal() as db:
            transport = db.query(Transport).filter(Transport.id == transport_id).first()
            if not transport:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "运输信息不存在"},
                )
            transport.status = transport_status
            db.commit()
            if notify:
                orders = (
                    db.query(Order.client_id)
                    .join(Transport, Order.plan_id == Transport.plan_id)
                    .filter(Transport.id == transport_id)
                    .group_by(Order.client_id)
                    .all()
                )
                for o in orders:
                    add_message(
                        title="原料运输状态更新",
                        content=f"您的原料运输计划状态已经更新, 当前状态：{transport_status}",
                        sender="系统",
                        receiver_id=o[0],
                        message_type="原料运输状态更新",
                        tag=2,
                        details=json.dumps(
                            transform_schema(TransportSchema, transport)
                        ),
                    )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "修改成功"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.put("/update_transport", summary="更新运输信息")
async def update_transport_api(
    transport_id: int = Body(..., description="运输ID"),
    plan_id: Optional[int] = Body(None, description="计划ID"),
    operate_time: Optional[str] = Body(
        None, description="操作时间", examples=["2021-01-01 00:00:00"]
    ),
    remark: Optional[str] = Body(None, description="备注"),
    notify: bool = Body(False, description="是否通知客户"),
):
    """
    # 更新运输信息
    ## params
    - **transport_id**: 运输ID, int
    - **plan_id**: 计划ID, int, 可选
    - **operate_date**: 操作时间, str, 可选
    - **remark**: 备注, str, 可选
    - **notify**: 是否通知客户, bool, 可选
    """
    try:
        with SessionLocal() as db:
            transport = db.query(Transport).filter(Transport.id == transport_id).first()
            if not transport:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "运输信息不存在"},
                )
            if plan_id:
                plan = db.query(Plan).filter(Plan.id == plan_id).first()
                if not plan:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "关联的计划不存在"},
                    )
                transport.plan = plan
            if operate_time:
                transport.operate_time = datetime.strptime(
                    operate_time, "%Y-%m-%d %H:%M:%S"
                )
            if remark:
                transport.remark = remark
            db.commit()
            if notify:
                orders = (
                    db.query(Order.client_id)
                    .join(Transport, Order.plan_id == Transport.plan_id)
                    .filter(Transport.id == transport_id)
                    .group_by(Order.client_id)
                    .all()
                )
                for o in orders:
                    add_message(
                        title="原料运输信息变更",
                        content=f"您的原料运输计划信息已经变更, 操作时间：{operate_time}, 备注：{remark}",
                        sender="系统",
                        receiver_id=o[0],
                        message_type="原料运输信息变更",
                        tag=2,
                        details=json.dumps(
                            transform_schema(TransportSchema, transport)
                        ),
                    )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "修改成功"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.delete("/delete_transport", summary="删除运输信息")
async def delete_transport_api(
    transport_id: int = Query(..., description="运输ID"),
    notify: bool = Query(False, description="是否通知客户"),
):
    """
    # 删除运输信息
    ## params
    - **transport_id**: 运输ID
    - **notify**: 是否通知客户, bool, 可选
    """
    try:
        with SessionLocal() as db:
            transport = db.query(Transport).filter(Transport.id == transport_id).first()
            if not transport:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "运输信息不存在"},
                )
            if notify:
                orders = (
                    db.query(Order.client_id)
                    .join(Transport, Order.plan_id == Transport.plan_id)
                    .filter(Transport.id == transport_id)
                    .group_by(Order.client_id)
                    .all()
                )
                for o in orders:
                    add_message(
                        title="原料运输计划删除",
                        content=f"您的原料运输计划已经删除",
                        sender="系统",
                        receiver_id=o[0],
                        message_type="原料运输计划删除",
                        tag=2,
                        details=json.dumps(
                            transform_schema(TransportSchema, transport)
                        ),
                    )
            db.delete(transport)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )
