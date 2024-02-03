from datetime import datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse

from models.base import OrderSchema
from schema.database import SessionLocal
from schema.tables import Order, Plan, Client, Location
from schema.common import page_with_order

order_router = APIRouter()


@order_router.get("/get_orders", summary="获取订单列表")
async def get_orders(
    year: int = Query(None, description="年份"),
    batch: int = Query(None, description="批次"),
    location_name: str = Query(None, description="基地名称"),
    order_status: str = Query(None, description="订单状态"),
    start_time: str = Query(None, description="开始时间"),
    end_time: str = Query(None, description="结束时间"),
    client_name: str = Query(None, description="客户名称"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序方式"),
):
    """
    # 获取订单列表
    - **year**: 年份, 可选
    - **batch**: 批次, 可选
    - **order_status**: 订单状态, 可选
    - **start_time**: 开始时间, 可选
    - **end_time**: 结束时间, 可选
    - **client_name**: 客户名称, 可选
    - **page**: 页码
    - **page_size**: 每页数量
    - **order_field**: 排序字段
    - **order**: 排序方式
    """
    try:
        with SessionLocal() as db:
            query = (
                db.query(Order)
                .join(Plan, Order.plan_id == Plan.id)
                .join(Client, Order.client_id == Client.id)
            )
            if year:
                query = query.filter(Plan.year == year)
            if batch:
                query = query.filter(Plan.batch == batch)
            if order_status:
                query = query.filter(Order.status == order_status)
            if start_time:
                start_time = datetime.strptime(start_time, "%Y-%m-%d")
                query = query.filter(Order.create_time >= start_time)
            if end_time:
                end_time = datetime.strptime(end_time, "%Y-%m-%d")
                query = query.filter(Order.complete_time <= end_time)
            if client_name:
                query = query.filter(Client.name == client_name)
            if location_name:
                location = (
                    db.query(Location).filter(Location.name == location_name).first()
                )
                if not location:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "msg": "基地不存在"},
                    )
                query = query.filter(Plan.location == location.id)

            response = page_with_order(
                schema=OrderSchema,
                query=query,
                page=page,
                page_size=page_size,
                order_field=order_field,
                order=order,
            )
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)
    except Exception as e:
        return JSONResponse({"code": 500, "msg": str(e)})


@order_router.get("/filter_orders_by_client", summary="根据客户获取订单列表")
async def filter_orders_by_client(
    client_id: int = Query(..., description="客户id"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序方式"),
):
    """
    # 根据客户获取订单列表
    - **client_id**: 客户id
    - **page**: 页码
    - **page_size**: 每页数量
    - **order_field**: 排序字段
    - **order**: 排序方式
    """
    try:
        with SessionLocal() as db:
            query = db.query(Order).filter(Order.client_id == client_id)
            response = page_with_order(
                schema=OrderSchema,
                query=query,
                page=page,
                page_size=page_size,
                order_field=order_field,
                order=order,
            )
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)
    except Exception as e:
        return JSONResponse({"code": 500, "msg": str(e)})


@order_router.post("/add_order", summary="添加订单")
async def add_order(
    plan_id: int = Body(..., description="计划id"),
    client_id: int = Body(..., description="客户id"),
    address_id: int = Body(..., description="地址id"),
    product_id: int = Body(..., description="产品id"),
    customized_area: float = Body(..., description="定制面积"),
    total_number: int = Body(..., description="总数量"),
    camera_id: int = Body(..., description="相机id"),
):
    """
    # 添加订单
    - **plan_id**: 计划id
    - **client_id**: 客户id
    - **product_id**: 产品id
    - **customized_area**: 定制面积
    - **total_number**: 总数量
    - **camera_id**: 相机id
    """
    try:
        with SessionLocal() as db:
            db.add(
                Order(
                    plan_id=plan_id,
                    client_id=client_id,
                    product_id=product_id,
                    customized_area=customized_area,
                    address_id=address_id,
                    num=total_number,
                    camera_id=camera_id,
                )
            )
            db.commit()
            return JSONResponse({"code": 200, "msg": "添加成功"})
    except Exception as e:
        return JSONResponse({"code": 500, "msg": str(e)})


@order_router.put("/complete_order", summary="完成订单")
async def complete_order(
    order_id: int = Query(..., description="订单id"),
):
    """
    # 完成订单
    - **order_id**: 订单id
    """
    try:
        with SessionLocal() as db:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "msg": "订单不存在"},
                )
            order.status = "已完成"
            order.complete_time = datetime.now()
            db.commit()
            return JSONResponse({"code": 200, "msg": "完成成功"})
    except Exception as e:
        return JSONResponse({"code": 500, "msg": str(e)})


@order_router.put("/update_order", summary="更新订单")
async def update_order_status(
    order_id: int = Body(..., description="订单id"),
    order_status: str = Body(None, description="订单状态"),
    plan_id: int = Body(None, description="计划id"),
    product_id: int = Body(None, description="产品id"),
    total_number: int = Body(None, description="总数量"),
    client_id: int = Body(None, description="客户id"),
    camera_id: int = Body(None, description="相机id"),
    customized_area: float = Body(None, description="定制面积"),
):
    """
    # 更新订单状态
    - **order_id**: 订单id
    - **order_status**: 订单状态
    y
    """
    try:
        with SessionLocal() as db:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "msg": "订单不存在"},
                )
            if order_status:
                order.status = order_status
            if plan_id:
                order.plan_id = plan_id
            if product_id:
                order.product_id = product_id
            if total_number:
                order.num = total_number
            if client_id:
                order.client_id = client_id
            if camera_id:
                order.camera_id = camera_id
            if customized_area:
                order.customized_area = customized_area
            db.commit()
            return JSONResponse({"code": 200, "msg": "更新成功"})
    except Exception as e:
        return JSONResponse({"code": 500, "msg": str(e)})


@order_router.delete("/delete_order", summary="删除订单")
async def delete_order(
    order_id: int = Body(..., description="订单id"),
):
    """
    # 删除订单
    - **order_id**: 订单id
    """
    try:
        with SessionLocal() as db:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "msg": "订单不存在"},
                )
            db.delete(order)
            db.commit()
            return JSONResponse({"code": 200, "msg": "删除成功"})
    except Exception as e:
        return JSONResponse({"code": 500, "msg": str(e)})
