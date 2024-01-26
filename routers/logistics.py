from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Query, status, Body, HTTPException
from fastapi.responses import JSONResponse

from schema.tables import LogisticsPlan, Plan, Location, Order
from schema.common import page_with_order
from schema.database import SessionLocal
from models.base import LogisticsPlanSchema

logistics_router = APIRouter()


@logistics_router.get("/get_logistics", summary="获取物流计划信息")
async def get_logistics(
    year: int = Query(None, description="年份"),
    batch: int = Query(None, description="批次"),
    location_name: str = Query(None, description="基地名称"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order: Literal["asc", "desc"] = Query("asc", description="排序"),
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
            response = page_with_order(
                schema=LogisticsPlanSchema,
                query=query,
                page=page,
                page_size=page_size,
                order=order,
                order_field=order_field,
            )
            return JSONResponse(status_code=status.HTTP_200_OK, content=response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@logistics_router.post("/add_logistics", summary="添加物流计划")
async def add_logistics(
    plan_id: int = Body(..., description="计划id"),
    operate_date: str = Body(..., description="计划操作日期", example="2021-01-01 00:00:00"),
    operate_people: str = Body(..., description="计划操作人"),
    order_num: str = Body(..., description="订单编号"),
    notices: str = Body(..., description="备注"),
):
    try:
        with SessionLocal() as db:
            plan = db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "计划不存在"},
                )
            order = db.query(Order).filter(Order.num == order_num).first()
            if not order:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "订单不存在"},
                )
            logistics = LogisticsPlan(
                plan_id=plan_id,
                operate_date=datetime.strptime(operate_date, "%Y-%m-%d %H:%M:%S"),
                operate_people=operate_people,
                order_id=order.id,
                notices=notices,
            )
            db.add(logistics)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@logistics_router.put("/update_logistics_status", summary="修改物流计划")
async def update_logistics_status(
    logistics_id: int = Body(..., description="物流计划id"),
    logistics_status: str = Body(..., description="状态"),
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
            logistics.status = logistics_status
            db.commit()
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
            db.delete(logistics)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
