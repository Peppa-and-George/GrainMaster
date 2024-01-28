from typing import Literal

from fastapi import APIRouter, HTTPException, status, Query, Body
from fastapi.responses import JSONResponse

from schema.database import SessionLocal
from schema.tables import Order
from schema.common import page_with_order

order_router = APIRouter()


@order_router.get("get_orders", summary="获取订单列表")
async def get_orders(
    year: int = Query(None, description="年份"),
    batch: int = Query(None, description="批次"),
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
    pass


@order_router.post("add_order", summary="添加订单")
async def add_order(
    plan_id: int = Body(..., description="计划id"),
    client_id: int = Body(..., description="客户id"),
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
                    num=total_number,
                    camera_id=camera_id,
                )
            )
            db.commit()
            return JSONResponse({"code": 200, "msg": "添加成功"})
    except Exception as e:
        return JSONResponse({"code": 500, "msg": str(e)})
