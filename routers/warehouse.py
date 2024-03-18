import json
from datetime import datetime
from typing import Literal, Optional, Union
from routers.message import add_message

from fastapi import (
    APIRouter,
    Query,
    status,
    Body,
    HTTPException,
    Form,
    UploadFile,
    File,
)
from fastapi.responses import JSONResponse

from schema.tables import (
    Plan,
    Location,
    Warehouse,
    Order,
    Product,
    Quality,
    ProcessingSegment,
)
from schema.common import page_with_order, transform_schema
from schema.database import SessionLocal
from models.base import WarehouseSchema, ProcessingSegmentSchema
from dependency.image import save_upload_image, delete_image
from dependency.videos import save_video, delete_video

warehouse_router = APIRouter()


def query_segment(
    warehouse_id: int, segment_type: Literal["投料", "压榨", "精炼", "分装", "入库"]
) -> ProcessingSegment:
    with SessionLocal() as db:
        segment = db.query(ProcessingSegment).filter(
            ProcessingSegment.warehouse_id == warehouse_id,
            ProcessingSegment.type == segment_type,
        )
        if segment.count() == 0:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail=f"加工环节{segment_type}不存在, 仓储加工计划ID: {warehouse_id}",
            )
        elif segment.count() > 1:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail=f"加工环节{segment_type}重复, 仓储加工计划ID: {warehouse_id}",
            )
        return segment.first()


def update_status(warehouse_id: int):
    with SessionLocal() as db:
        warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not warehouse:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "仓库不存在"},
            )
        segment = query_segment(warehouse_id, "入库")
        if segment.completed:
            warehouse.status = "加工完成"
            db.commit()
            return
        for item in ["投料", "压榨", "精炼", "分装"]:
            segment = query_segment(warehouse_id, item)
            if segment.completed:
                warehouse.status = "加工中"
                db.commit()
                return
        warehouse.status = "准备加工"


@warehouse_router.get("/get_total_amount_by_order", summary="获取订单数量")
async def get_total_amount(
    order: Union[int, str] = Query(..., description="订单ID或者订单编号"),
    order_field_type: Literal["id", "num"] = Query("id", description="订单字段类型"),
):
    """
    # 获取订单加工数量
    ## params
    - **order**: 订单ID或者订单编号, int | str, 必选
    - **order_field_type**: 订单字段类型, 可选, 默认id, 可选值：id | num
    # response
    - **total_amount**: 总数量
    """
    with SessionLocal() as db:
        if order_field_type == "id":
            order_obj = db.query(Order).filter(Order.id == order).first()
        else:
            order_obj = db.query(Order).filter(Order.order_number == order).first()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"total_amount": order_obj.total_amount},
        )


@warehouse_router.get("/get_amount_info_by_order", summary="通过订单获取仓储加工数量信息")
async def get_amount_info_by_order(
    order: Union[int, str] = Query(..., description="订单ID或者订单编号"),
    order_field_type: Literal["id", "num"] = Query("id", description="订单字段类型"),
):
    """
    # 通过订单获取仓储加工数量信息
    ## params
    - **order**: 订单ID或者订单编号, int | str, 必选
    - **order_field_type**: 订单字段类型, 可选, 默认id, 可选值：id | num
    # response
    - **total_amount**: 总数量
    - **processed_amount**: 已加工数量
    - **processing_amount**: 加工中数量
    - **available_amount**: 可加工数量
    """
    with SessionLocal() as db:
        if order_field_type == "id":
            order_obj = db.query(Order).filter(Order.id == order).first()
        else:
            order_obj = db.query(Order).filter(Order.order_number == order).first()

        if not order_obj:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "订单不存在"},
            )
        total_amount = order_obj.total_amount
        warehouse = (
            db.query(Warehouse)
            .filter(Warehouse.order_id == order_obj.id, Warehouse.status == "加工完成")
            .all()
        )
        processed_amount = sum([i.amount for i in warehouse])
        all_warehouse = (
            db.query(Warehouse).filter(Warehouse.order_id == order_obj.id).all()
        )
        processing_amount = sum([i.amount for i in all_warehouse]) - processed_amount
        available_amount = total_amount - processed_amount - processing_amount
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "total_amount": total_amount,
                "processed_amount": processed_amount,
                "processing_amount": processing_amount,
                "available_amount": available_amount,
            },
        )


@warehouse_router.get("/get_warehouse", summary="获取仓储加工计划信息")
async def get_warehouse(
    warehouse_id: int = Query(None, description="仓储加工计划ID"),
    plan_id: Optional[int] = Query(None, description="计划ID"),
    year: int = Query(None, description="年份"),
    batch: int = Query(None, description="批次"),
    location: Union[int, str, None] = Query(None, description="基地标识"),
    location_field_type: Literal["id", "name"] = Query("id", description="基地字段类型"),
    order: Union[int, str, None] = Query(None, description="订单ID或者订单编号"),
    order_field_type: Literal["id", "num"] = Query("id", description="订单字段类型"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order_type: Literal["asc", "desc"] = Query("asc", description="排序"),
    order_by: str = Query("id", description="排序字段"),
):
    """
    # 获取仓储加工信息
    ## params
    - **warehouse_id**: 仓储加工计划ID, int,  可选
    - **plan_id**: 计划ID, int, 可选
    - **year**: 年份, int, 可选
    - **batch**: 批次, int, 可选
    - **location**: 基地标识, int | str, 可选
    - **location_field_type**: 基地字段类型, 可选, 默认id, 可选值：id | name
    - **order**: 订单ID或者订单编号, int | str, 可选
    - **order_field_type**: 订单字段类型, 可选, 默认id, 可选值：id | num
    - **page**: 页码, int, 可选, 默认1
    - **page_size**: 每页数量, int, 可选, 默认10
    - **order_type**: 排序类型, 可选, 默认asc, 可选值：asc | desc
    - **order_by**: 排序字段, 可选, 默认id
    """
    try:
        with SessionLocal() as db:
            query = db.query(Warehouse)
            if warehouse_id:
                query = query.filter(Warehouse.id == warehouse_id)
            if plan_id:
                query = query.filter(Warehouse.plan_id == plan_id)
            if year or batch or location_field_type == "id":
                query = query.join(Plan)
            if year:
                query = query.filter(Plan.year == year)
            if batch:
                query = query.filter(Plan.batch == batch)
            if location:
                if location_field_type == "id":
                    query = query.filter(Plan.location_id == location)
                else:
                    query = query.join(
                        Location, Plan.location_id == Location.id
                    ).filter(Location.name == location)
            if order:
                if order_field_type == "id":
                    query = query.filter(Warehouse.order_id == order)
                else:
                    query = query.join(Order, Warehouse.order_id == Order.id).filter(
                        Order.order_number == order
                    )

            response = page_with_order(
                WarehouseSchema,
                query,
                page=page,
                page_size=page_size,
                order_field=order_by,
                order=order_type,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response,
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仓库信息失败, {e}",
        )


@warehouse_router.get("/get_processing_segment", summary="获取仓储加工环节信息")
async def get_processing_segment(
    processing_segment_id: int = Query(None, description="加工环节ID"),
    warehouse_id: Optional[int] = Query(None, description="仓库ID"),
    processing_type: Optional[Literal["投料", "压榨", "精炼", "分装", "入库"]] = Query(
        None, description="加工环节类型"
    ),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order_type: Literal["asc", "desc"] = Query("asc", description="排序"),
    order_by: str = Query("id", description="排序字段"),
):
    """
    # 获取仓储加工环节信息
    ## params
    - **processing_segment_id**: 加工环节ID, int, 可选
    - **warehouse_id**: 仓库加工计划ID, int, 可选
    - **processing_type**: 加工环节类型, 可选, 可选值：投料 | 压榨 | 精炼 | 分装 | 入库
    - **page**: 页码, int, 可选, 默认1
    - **page_size**: 每页数量, int, 可选, 默认10
    - **order_type**: 排序类型, 可选, 默认asc, 可选值：asc | desc
    - **order_by**: 排序字段, 可选, 默认id
    """
    try:
        with SessionLocal() as db:
            query = db.query(ProcessingSegment).join(Warehouse)
            if processing_segment_id:
                query = query.filter(ProcessingSegment.id == processing_segment_id)
            if warehouse_id:
                query = query.filter(ProcessingSegment.warehouse_id == warehouse_id)
            if processing_type:
                query = query.filter(ProcessingSegment.type == processing_type)
            response = page_with_order(
                ProcessingSegmentSchema,
                query,
                page=page,
                page_size=page_size,
                order_field=order_by,
                order=order_type,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response,
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仓库加工环节信息失败, {e}",
        )


@warehouse_router.post("/add_warehouse", summary="添加仓库信息")
async def add_warehouse(
    order: Union[int, str] = Body(..., description="订单ID或者订单编号"),
    order_field_type: Literal["id", "num"] = Body("id", description="订单字段类型"),
    product: Union[str, int] = Body(..., description="产品名称", examples=["大豆油", "花生油"]),
    product_field_type: Literal["id", "name"] = Body("name", description="产品字段类型"),
    operate_time: Optional[str] = Body(
        None, description="操作时间", examples=["2021-08-01 12:00:00"]
    ),
    amount: int = Body(..., description="加工数量", ge=8, examples=[8, 17]),
    remarks: Optional[str] = Body(None, description="备注"),
    notify: Optional[bool] = Body(False, description="是否通知客户"),
):
    """
    # 添加仓储加工信息
    ## params
    - **order**: 订单ID或者订单编号, int | str, 必选
    - **order_field_type**: 订单字段类型, 可选, 默认id, 可选值：id | num
    - **product**: 产品名称, int | str, 必选
    - **product_field_type**: 产品字段类型, 可选, 默认name, 可选值：id | name
    - **operate_time**: 操作时间, 可选, 例子：2021-08-01 12:00:00
    - **amount**: 加工数量, int, 必选, 大于8
    - **remarks**: 备注, 可选
    - **notify**: 是否通知客户, 可选
    """
    with SessionLocal() as db:
        # 验证订单
        if order_field_type == "id":
            order_obj = db.query(Order).filter(Order.id == order).first()
        else:
            order_obj = db.query(Order).filter(Order.order_number == order).first()
        if not order_obj:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "订单不存在"},
            )

        # 验证加工数量
        completed_warehouse = db.query(Warehouse).filter_by(order_id=order_obj.id).all()
        completed_amount = sum([i.amount for i in completed_warehouse])
        if amount > order_obj.total_amount - completed_amount:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "加工数量大于订单剩余数量"},
            )

        # 验证产品
        if product_field_type == "id":
            product_obj = db.query(Product).filter(Product.id == product).first()
        else:
            product_obj = db.query(Product).filter(Product.name == product).first()
        if not product_obj:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "产品不存在"},
            )

        warehouse = Warehouse(
            remarks=remarks,
            status="准备加工",
            amount=amount,
            operate_time=datetime.strptime(operate_time, "%Y-%m-%d %H:%M:%S"),
            order_id=order_obj.id,
        )
        warehouse.plan = order_obj.plan
        warehouse.product = product_obj

        # 添加质检报告记录
        quality = Quality(
            name="仓储加工质检报告",
            status="未上传",
            type="仓储加工",
        )
        quality.plan = order_obj.plan
        warehouse.qualities.append(quality)

        # 添加加工环节
        for segment in ["投料", "压榨", "精炼", "分装", "入库"]:
            processing_segment = ProcessingSegment(
                type=segment,
            )
            warehouse.processing_segments.append(processing_segment)
        db.add(warehouse)
        db.commit()
        db.refresh(warehouse)

        if notify:
            # 发送消息通知
            add_message(
                title=f"仓储加工通知",
                content=f"您的订单{order_obj.order_number}已经开始加工，请注意查看",
                receiver_id=order_obj.client_id,
                sender="系统",
                message_type="通知",
                tag=3,
                details=json.dumps(transform_schema(WarehouseSchema, warehouse)),
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "添加成功",
                "data": transform_schema(WarehouseSchema, warehouse),
            },
        )


@warehouse_router.put("/update_warehouse_status", summary="更新仓储加工状态信息")
async def update_warehouse_status(
    warehouse_id: int = Body(..., description="仓库ID"),
    warehouse_status: Literal["准备加工", "加工中", "加工完成"] = Body(
        "准备加工", description="状态", examples=["准备加工", "加工中", "加工完成"]
    ),
    notify: bool = Body(False, description="是否通知客户"),
):
    """
    # 更新仓库状态信息
    ## params
    - **warehouse_id**: 仓库ID
    - **warehouse_status**: 状态， 可选值：准备加工 | 加工中 | 加工完成
    - **notify**: 是否通知客户, 可选
    """
    try:
        with SessionLocal() as db:
            warehouse = db.query(Warehouse).filter_by(id=warehouse_id).first()
            if not warehouse:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "仓库不存在"},
                )
            warehouse.status = warehouse_status
            db.commit()
            if notify:
                # 发送消息通知
                add_message(
                    title=f"仓储加工状态变更通知",
                    content=f"您的订单{warehouse.order.order_number}加工状态已变更，当前状态：{warehouse_status}，请注意查看",
                    receiver_id=warehouse.order.client_id,
                    sender="系统",
                    message_type="仓储加工状态变更",
                    tag=3,
                    details=json.dumps(transform_schema(WarehouseSchema, warehouse)),
                )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "更新成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新仓库状态信息失败, {e}",
        )


@warehouse_router.put("/update_warehouse", summary="更新仓储加工信息")
async def update_warehouse(
    warehouse_id: int = Body(..., description="仓库加工ID"),
    amount: Optional[float] = Body(None, description="数量", examples=[100, 200]),
    product: Union[int, str, None] = Body(None, description="产品标识"),
    product_field_type: Literal["id", "name"] = Body("id", description="产品字段类型"),
    plan_id: Optional[int] = Body(None, description="计划ID"),
    processing_status: Optional[Literal["准备加工", "加工中", "加工完成"]] = Body(
        None, description="状态", examples=["准备加工", "加工中", "加工完成"]
    ),
    operate_time: Optional[str] = Body(
        None, description="操作时间", examples=["2021-08-01 12:00:00"]
    ),
    remarks: Optional[str] = Body(None, description="备注"),
    notify: bool = Body(False, description="是否通知客户"),
):
    """
    # 更新仓储加工信息
    ## params
    - **warehouse_id**: 仓库加工ID, int, 必选
    - **amount**: 数量, 可选
    - **product**: 产品标识, 可选
    - **product_field_type**: 产品字段类型, 可选, 默认id, 可选值：id | name
    - **plan_id**: 计划ID, 可选
    - **processing_status**: 状态, 可选, 可选值：准备加工 | 加工中 | 加工完成
    - **operate_time**: 操作时间, 可选, 例子：2021-08-01 12:00:00
    - **remarks**: 备注, 可选
    - **notify**: 是否通知客户, 可选
    """
    try:
        with SessionLocal() as db:
            warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "仓储加工环节不存在"},
                )

            # 验证产品
            if product:
                if product_field_type == "id":
                    product_obj = (
                        db.query(Product).filter(Product.id == product).first()
                    )
                else:
                    product_obj = (
                        db.query(Product).filter(Product.name == product).first()
                    )
                if not product_obj:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "产品不存在"},
                    )
                warehouse.product = product_obj

            # 验证计划
            if plan_id:
                plan = db.query(Plan).filter(Plan.id == plan_id).first()
                if not plan:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "计划不存在"},
                    )
                warehouse.plan = plan
            if amount:
                old_amount = warehouse.amount
                warehouse.amount = amount
                warehouse.product.amount = (
                    warehouse.product.amount - old_amount + amount
                )
            if processing_status:
                warehouse.status = processing_status
            if operate_time:
                warehouse.operate_time = datetime.strptime(
                    operate_time, "%Y-%m-%d %H:%M:%S"
                )
            if remarks:
                warehouse.remarks = remarks
            db.commit()
            if notify:
                # 发送消息通知
                add_message(
                    title=f"仓储加工信息变更通知",
                    content=f"您的订单{warehouse.order.order_number}加工信息已变更，请注意查看",
                    receiver_id=warehouse.order.client_id,
                    sender="系统",
                    message_type="仓储加工信息变更",
                    tag=3,
                    details=json.dumps(transform_schema(WarehouseSchema, warehouse)),
                )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "更新成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新仓储加工信息失败, {e}",
        )


@warehouse_router.put("/update_processing_segment", summary="更新仓储加工环节信息")
async def update_processing_segment(
    processing_segment_id: int = Body(..., description="加工环节ID"),
    operator: Optional[str] = Body(None, description="操作人"),
    completed: Optional[bool] = Body(None, description="是否完成"),
    operate_time: Optional[str] = Body(
        None, description="操作时间", examples=["2021-08-01 12:00:00"]
    ),
    remarks: Optional[str] = Body(None, description="备注"),
    notify: bool = Query(False, description="是否通知客户"),
):
    """
    # 更新仓储加工环节信息
    ## params
    - **processing_segment_id**: 加工环节ID, int, 必选
    - **operator**: 操作人, 可选
    - **completed**: 是否完成, 可选
    - **operate_time**: 操作时间, 可选, 例子：2021-08-01 12:00:00
    - **remarks**: 备注, 可选
    - **notify**: 是否通知客户, 可选
    """
    try:
        with SessionLocal() as db:
            processing_segment = (
                db.query(ProcessingSegment)
                .filter(ProcessingSegment.id == processing_segment_id)
                .first()
            )
            if not processing_segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "加工环节不存在"},
                )
            if operator:
                processing_segment.operator = operator
            if completed is not None:
                processing_segment.completed = completed

            if operate_time:
                processing_segment.operate_time = datetime.strptime(
                    operate_time, "%Y-%m-%d %H:%M:%S"
                )
            if remarks:
                processing_segment.remarks = remarks
            db.commit()
            if completed:
                update_status(processing_segment.warehouse_id)
            if notify:
                # 发送消息通知
                add_message(
                    title=f"仓储加工环节信息变更通知",
                    content=f"您的订单{processing_segment.warehouse.order.order_number}加工环节信息已变更，请注意查看",
                    receiver_id=processing_segment.warehouse.order.client_id,
                    sender="系统",
                    message_type="仓储加工环节信息变更",
                    tag=3,
                    details=json.dumps(
                        transform_schema(WarehouseSchema, processing_segment.warehouse)
                    ),
                )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "更新成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新仓储加工环节信息失败, {e}",
        )


@warehouse_router.post("/upload_file", summary="上传文件")
async def upload_file(
    processing_segment_id: int = Form(..., description="加工环节ID"),
    file_type: Literal["image", "video"] = Form("image", description="文件类型"),
    file: UploadFile = File(..., description="文件"),
    notify: bool = Form(False, description="是否通知客户"),
):
    """
    # 上传文件
    ## params
    - **processing_segment_id**: 加工环节ID, int, 必选
    - **file_type**: 文件类型, 可选, 可选值：image | video
    - **file**: 文件, 必选
    - **notify**: 是否通知客户, 默认False, 可选
    """
    try:
        with SessionLocal() as db:
            processing_segment = (
                db.query(ProcessingSegment)
                .filter(ProcessingSegment.id == processing_segment_id)
                .first()
            )
            if not processing_segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "加工环节不存在"},
                )
            if file_type == "image":
                if processing_segment.image_filename:
                    delete_image(processing_segment.image_filename)
                processing_segment.image_filename = save_upload_image(file)
            else:
                if processing_segment.video_filename:
                    delete_video(processing_segment.video_filename)
                processing_segment.video_filename = save_video(file)
            processing_segment.completed = True
            db.flush()
            db.commit()
            update_status(processing_segment.warehouse_id)
            if notify:
                # 发送消息通知
                add_message(
                    title=f"仓储加工环节文件上传通知",
                    content=f"您的订单{processing_segment.warehouse.order.order_number}关联的仓储加工环节上传了一个文件，文件类型：{file_type}，请注意查看",
                    receiver_id=processing_segment.warehouse.order.client_id,
                    sender="系统",
                    message_type="仓储加工环节文件上传",
                    tag=3,
                    details=json.dumps(
                        transform_schema(ProcessingSegmentSchema, processing_segment)
                    ),
                )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "上传成功",
                    "data": transform_schema(
                        ProcessingSegmentSchema, processing_segment
                    ),
                },
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传文件失败, {e}",
        )


@warehouse_router.delete("/delete_file", summary="删除文件")
async def delete_file(
    processing_segment_id: int = Query(..., description="加工环节ID"),
    file_type: Literal["image", "video", "all"] = Query("all", description="文件类型"),
    notify: bool = Query(False, description="是否通知客户"),
):
    """
    # 删除文件
    ## params
    - **processing_segment_id**: 加工环节ID, int, 必选
    - **file_type**: 文件类型, 可选, 默认all, 可选值：image | video | all
    - **notify**: 是否通知客户, 默认False, 可选
    """
    try:
        with SessionLocal() as db:
            processing_segment = (
                db.query(ProcessingSegment)
                .filter(ProcessingSegment.id == processing_segment_id)
                .first()
            )
            if not processing_segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "加工环节不存在"},
                )
            if file_type == "image":
                if processing_segment.image_filename:
                    delete_image(processing_segment.image_filename)
                processing_segment.image_filename = None
            elif file_type == "video":
                if processing_segment.video_filename:
                    delete_video(processing_segment.video_filename)
                processing_segment.video_filename = None
            else:
                if processing_segment.image_filename:
                    delete_image(processing_segment.image_filename)
                if processing_segment.video_filename:
                    delete_video(processing_segment.video_filename)
                processing_segment.image_filename = None
                processing_segment.video_filename = None
            if (
                processing_segment.video_filename is None
                and processing_segment.image_filename is None
            ):
                processing_segment.completed = False
            db.commit()
            update_status(processing_segment.warehouse_id)
            if notify:
                # 发送消息通知
                add_message(
                    title=f"仓储加工环节文件删除通知",
                    content=f"您的订单{processing_segment.warehouse.order.order_number}关联的仓储加工环节删除了文件，请注意查看",
                    receiver_id=processing_segment.warehouse.order.client_id,
                    sender="系统",
                    message_type="仓储加工环节文件删除",
                    tag=3,
                    details=json.dumps(
                        transform_schema(ProcessingSegmentSchema, processing_segment)
                    ),
                )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败, {e}",
        )


@warehouse_router.delete("/delete_warehouse", summary="删除仓储加工计划")
async def delete_warehouse(
    warehouse_id: int = Query(..., description="仓库ID"),
    notify: bool = Query(False, description="是否通知客户"),
):
    """
    # 删除仓库信息
    ## params
    - **warehouse_id**: 仓库ID, int, 必选
    - **notify**: 是否通知客户, 默认False, 可选
    """
    try:
        with SessionLocal() as db:
            warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "仓储信息不存在"},
                )
            if notify:
                # 发送消息通知
                add_message(
                    title=f"仓储加工计划删除通知",
                    content=f"您的订单{warehouse.order.order_number}关联的仓储加工计划已被删除，请注意查看",
                    receiver_id=warehouse.order.client_id,
                    sender="系统",
                    message_type="仓储加工删除",
                    tag=3,
                    details=json.dumps(transform_schema(WarehouseSchema, warehouse)),
                )
            db.delete(warehouse)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除仓储信息失败, {e}",
        )
