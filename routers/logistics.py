# 物流计划
import json
from datetime import datetime
from typing import Literal, Union, Optional

from fastapi import APIRouter, Query, status, Body, HTTPException
from fastapi.responses import JSONResponse

from schema.tables import (
    LogisticsPlan,
    Plan,
    Location,
    Order,
    Address,
    Warehouse,
)
from schema.common import page_with_order, transform_schema
from schema.database import SessionLocal
from models.base import LogisticsPlanSchema
from routers.message import add_message

logistics_router = APIRouter()


def get_amount_info(order: Union[str, int], order_field_type: Literal["id", "num"]):
    """
    获取订单的发货信息
    :param order: 订单标识
    :param order_field_type: 订单标识类型，id或num
    :return:
        order_amount: 订单总数量
        processed_amount: 已加工数量
        shipping_amount: 待发货数量
        transport_amount: 运输中数量
        received_amount: 已签收数量
        available_amount: 可发货数量
    """
    with SessionLocal() as db:
        if order_field_type == "id":
            order = db.query(Order).filter(Order.id == order).first()
        else:
            order = db.query(Order).filter(Order.order_number == order).first()
        if not order:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "订单不存在"},
            )

        processed_warehouse = (
            db.query(Warehouse)
            .filter(Warehouse.status == "加工完成", Warehouse.order_id == order.id)
            .all()
        )
        processed_amount = sum([warehouse.amount for warehouse in processed_warehouse])

        total_amount = order.total_amount
        query = db.query(LogisticsPlan).filter(LogisticsPlan.order_id == order.id)
        shipping_amount = sum(
            [
                logistics.amount
                for logistics in query.filter(
                    LogisticsPlan.express_status == "待发货"
                ).all()
            ]
        )
        transport_amount = sum(
            [
                logistics.amount
                for logistics in query.filter(
                    LogisticsPlan.express_status == "运输中"
                ).all()
            ]
        )
        received_amount = sum(
            [
                logistics.amount
                for logistics in query.filter(
                    LogisticsPlan.express_status == "已签收"
                ).all()
            ]
        )
        available_amount = (
            processed_amount - shipping_amount - transport_amount - received_amount
        )
        return {
            "order_amount": total_amount,
            "processed_amount": processed_amount,
            "shipping_amount": shipping_amount,
            "transport_amount": transport_amount,
            "received_amount": received_amount,
            "available_amount": available_amount,
        }


@logistics_router.get("/get_logistics_info", summary="获取物流计划信息")
async def get_logistics_info(
    logistics_id: Optional[int] = Query(None, description="物流计划id"),
    order: Optional[Union[int, str]] = Query(None, description="订单标识"),
    order_field_type: Literal["id", "num"] = Query("id", description="订单标识类型"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order_by: str = Query("create_time", description="排序字段"),
    order_by_type: Literal["asc", "desc"] = Query("desc", description="排序方式"),
):
    """
    # 获取物流计划信息
    ## params
    - **logistics_id**: 物流计划id, int, 可选
    - **order**: 订单标识, 可选, int or str
    - **order_field_type**: 订单标识类型, 可选, 可选值: id, num
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认10，范围1-100, 可选
    - **order_by**: 排序字段, 可选
    - **order_by_type**: 排序方式, 可选
    """
    try:
        with SessionLocal() as db:
            query = db.query(LogisticsPlan)
            if logistics_id:
                query = query.filter(LogisticsPlan.id == logistics_id)
            if order:
                if order_field_type == "id":
                    query = query.filter(LogisticsPlan.order_id == order)
                else:
                    query = query.join(
                        Order, Order.id == LogisticsPlan.order_id
                    ).filter(Order.order_number == order)
            response = page_with_order(
                schema=LogisticsPlanSchema,
                query=query,
                page=page,
                page_size=page_size,
                order=order_by_type,
                order_field=order_by,
            )
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@logistics_router.get("/get_amount_info", summary="获取物流计划数量信息")
async def get_amount_info_api(
    order: Union[str, int] = Query(..., description="订单标识"),
    order_field_type: Literal["id", "num"] = Query("id", description="订单标识类型"),
):
    """
    # 获取物流计划数量信息
    ## params
    - **order**: 订单标识
    - **order_field_type**: 订单标识类型, 可选值: id, num
    # response
    - **order_amount**: 订单总数量
    - **processed_amount**: 已加工数量
    - **shipping_amount**: 待发货数量
    - **transport_amount**: 运输中数量
    - **received_amount**: 已签收数量
    - **available_amount**: 可发货数量
    """
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 0,
            "message": "获取成功",
            "data": get_amount_info(order, order_field_type),
        },
    )


@logistics_router.get("/get_logistics", summary="获取物流计划信息")
async def get_logistics(
    year: int = Query(None, description="年份"),
    batch: int = Query(None, description="批次"),
    location_name: str = Query(None, description="基地名称"),
    order: Union[str, int, None] = Query(None, description="订单标识"),
    order_field_type: Literal["id", "num"] = Query("id", description="订单标识类型"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order_by: Literal["asc", "desc"] = Query("asc", description="排序"),
    order_field: str = Query("id", description="排序字段"),
):
    """
    # 获取物流计划信息
    ## params
    - **year**: 年份, 可选
    - **batch**: 批次, 可选
    - **location_name**: 基地名称, 可选
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认10，范围1-100, 可选
    - **order**: 排序方式, 可选
    - **search**: 搜索, 可选
    """
    try:
        with SessionLocal() as db:
            query = db.query(LogisticsPlan).join(Plan, Plan.id == LogisticsPlan.plan_id)
            if year:
                query = query.filter(Plan.year == year)
            if batch:
                query = query.filter(Plan.batch == batch)
            if location_name:
                location = (
                    db.query(Location).filter(Location.name == location_name).first()
                )
                if not location:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "位置不存在"},
                    )
                query = query.filter(Plan.location_id == location.id)
            if order:
                query = query.join(Order, Order.id == LogisticsPlan.order_id)
                if order_field_type == "id":
                    query = query.filter(Order.id == order)
                else:
                    query = query.filter(Order.order_number == order)
            response = page_with_order(
                schema=LogisticsPlanSchema,
                query=query,
                page=page,
                page_size=page_size,
                order=order_by,
                order_field=order_field,
            )
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# 已完成
@logistics_router.post("/add_logistics", summary="添加物流计划")
async def add_logistics(
    order: Union[int, str] = Body(..., description="订单标识"),
    order_field_type: Literal["id", "num"] = Body("id", description="订单标识类型"),
    amount: int = Body(..., description="发货数量"),
    address_id: int = Body(..., description="地址id"),
    operate_time: str = Body(
        ..., description="计划操作时间", examples=["2021-01-01 00:00:00"]
    ),
    remarks: str = Body(..., description="备注"),
    notify: bool = Body(False, description="是否通知"),
):
    """
    # 添加物流计划
    order_number和order_id必须有一个, 优先使用order_id
    ## params
    - **order_number**: 订单编号, 可选
    - **order_id**: 订单id, 可选
    - **address_id**: 地址id
    - **operate_time**: 计划操作日期
    - **operate_people**: 计划操作人
    - **remarks**: 备注
    - **notify**: 是否通知
    """
    with SessionLocal() as db:
        if order_field_type == "id":
            order = db.query(Order).filter(Order.id == order).first()
        else:
            order = db.query(Order).filter(Order.order_number == order).first()

        if not order:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "订单不存在"},
            )

        # 验证地址是否存在
        address = (
            db.query(Address)
            .filter(Address.id == address_id and Address.client_id == order.client_id)
            .first()
        )
        if not address:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "地址不存在或者不属于该客户"},
            )

        # 验证发货数量
        amount_info = get_amount_info(order.id, order_field_type)
        if amount > amount_info["available_amount"]:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 1,
                    "message": "计划发货数量不能大于可发货数量，可发货数量: %s"
                    % amount_info["available_amount"],
                },
            )

        logistics = LogisticsPlan(
            amount=amount,
            operate_time=datetime.strptime(operate_time, "%Y-%m-%d %H:%M:%S"),
            remarks=remarks,
            express_status="待发货",
        )
        logistics.order = order
        logistics.address = address
        logistics.plan = order.plan
        logistics.client = order.client
        db.add(logistics)
        db.flush()
        db.refresh(logistics)
        db.commit()
        if notify:
            add_message(
                receiver_id=order.client_id,
                title="新增物流计划通知",
                content=f"您有一个新的物流计划, 计划操作时间: {operate_time}, 备注: {remarks}",
                sender="系统",
                message_type="新增物流计划",
                tag=4,
                details=json.dumps(transform_schema(LogisticsPlanSchema, logistics)),
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "添加成功",
                "data": transform_schema(LogisticsPlanSchema, logistics),
            },
        )


@logistics_router.put("/update_logistics_status", summary="修改物流计划状态")
async def update_logistics_status(
    logistics_id: int = Body(..., description="物流计划id"),
    logistics_status: Literal["待发货", "运输中", "已签收"] = Body(..., description="状态"),
    notify: bool = Body(False, description="是否通知"),
):
    """
    # 修改物流计划状态
    ## params
    - **logistics_id**: 物流计划id
    - **logistics_status**: 状态，可选值: 待发货, 运输中, 已签收
    """
    try:
        with SessionLocal() as db:
            logistics = (
                db.query(LogisticsPlan).filter(LogisticsPlan.id == logistics_id).first()
            )
            if not logistics:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "物流计划不存在"},
                )
            logistics.express_status = logistics_status
            db.commit()
            if notify:
                add_message(
                    receiver_id=logistics.client_id,
                    title="修改物流计划状态通知",
                    content=f"您的物流计划状态已被修改, 当前状态: {logistics_status}",
                    sender="系统",
                    message_type="修改物流计划状态",
                    tag=4,
                    details=json.dumps(
                        transform_schema(LogisticsPlanSchema, logistics)
                    ),
                )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "修改成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@logistics_router.put("/upload_express_info", summary="上传物流单号")
async def upload_express_info(
    logistics_id: int = Body(..., description="物流计划id"),
    express_number: str = Body(..., description="物流单号"),
    express_company: str = Body(..., description="物流公司"),
    notify: bool = Body(False, description="是否通知"),
):
    """
    # 上传物流单号
    ## params
    - **logistics_id**: 物流计划id
    - **express_number**: 物流单号
    - **express_company**: 物流公司
    - **notify**: 是否通知
    """
    try:
        with SessionLocal() as db:
            logistics = (
                db.query(LogisticsPlan).filter(LogisticsPlan.id == logistics_id).first()
            )
            if not logistics:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "物流计划不存在"},
                )
            logistics.express_number = express_number
            logistics.express_company = express_company
            logistics.express_status = "运输中"
            db.commit()
            if notify:
                add_message(
                    receiver_id=logistics.client_id,
                    title="上传物流单号通知",
                    content=f"您的物流单号已上传, 物流公司: {express_company}, 物流单号: {express_number}",
                    sender="系统",
                    message_type="上传物流单号",
                    tag=4,
                    details=json.dumps(
                        transform_schema(LogisticsPlanSchema, logistics)
                    ),
                )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "上传成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@logistics_router.put("/update_logistics", summary="修改物流计划")
async def update_logistics(
    logistics_id: int = Body(..., description="物流计划id"),
    address_id: Optional[int] = Body(None, description="地址id"),
    amount: Optional[int] = Body(None, description="发货数量"),
    operate_time: Optional[str] = Body(
        None, description="计划操作时间", examples=["2021-01-01 00:00:00"]
    ),
    remarks: Optional[str] = Body(None, description="备注"),
    notify: bool = Body(False, description="是否通知"),
):
    """
    # 修改物流计划
    ## params
    - **logistics_id**: 物流计划id
    - **address_id**: 地址id, 可选
    - **operate_date**: 计划操作日期, 可选
    - **operate_people**: 计划操作人, 可选
    - **remarks**: 备注, 可选
    - **notify**: 是否通知, 可选
    """
    try:
        with SessionLocal() as db:
            logistics = (
                db.query(LogisticsPlan).filter(LogisticsPlan.id == logistics_id).first()
            )
            if not logistics:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "物流计划不存在"},
                )
            if address_id:
                address = db.query(Address).filter(Address.id == address_id).first()
                if not address:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "地址不存在"},
                    )
                logistics.address = address
            # 验证发货数量
            if amount:
                amount_info = get_amount_info(logistics.order_id, "id")
                if amount > amount_info["available_amount"] + logistics.amount:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={
                            "code": 1,
                            "message": "计划发货数量不能大于可发货数量，可发货数量: %s"
                            % amount_info["available_amount"]
                            + logistics.amount,
                        },
                    )
                logistics.amount = amount
            if operate_time:
                logistics.operate_time = datetime.strptime(
                    operate_time, "%Y-%m-%d %H:%M:%S"
                )
            if remarks:
                logistics.remarks = remarks
            db.commit()
            if notify:
                add_message(
                    receiver_id=logistics.client_id,
                    title="修改物流计划通知",
                    content=f"您的物流计划已被修改, 修改时间: {operate_time}, 备注: {remarks}",
                    sender="系统",
                    message_type="修改物流计划",
                    tag=4,
                    details=json.dumps(
                        transform_schema(LogisticsPlanSchema, logistics)
                    ),
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "修改成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@logistics_router.delete("/delete_logistics", summary="删除物流计划")
async def delete_logistics(
    logistics_id: int = Query(..., description="物流计划id"),
    notify: bool = Query(False, description="是否通知"),
):
    try:
        with SessionLocal() as db:
            logistics = (
                db.query(LogisticsPlan).filter(LogisticsPlan.id == logistics_id).first()
            )
            if not logistics:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "物流计划不存在"},
                )
            if logistics.express_status != "待发货":
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 1,
                        "message": f"当前运输状态为{logistics.express_status}, 只能删除待发货状态的物流计划",
                    },
                )
            db.delete(logistics)
            db.commit()
            if notify:
                add_message(
                    receiver_id=logistics.client_id,
                    title="删除物流计划通知",
                    content=f"您的物流计划已被删除",
                    sender="系统",
                    message_type="删除物流计划",
                    tag=4,
                    details=json.dumps(
                        transform_schema(LogisticsPlanSchema, logistics)
                    ),
                )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
