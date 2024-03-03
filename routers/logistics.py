# 物流计划
from datetime import datetime
from typing import Literal, Union, Optional

from fastapi import APIRouter, Query, status, Body, HTTPException
from fastapi.responses import JSONResponse

from schema.tables import LogisticsPlan, Plan, Location, Order, Address, Client
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
    order: Union[int, str] = Body(..., description="订单标识"),
    order_field_type: Literal["id", "num"] = Body("id", description="订单标识类型"),
    amount: int = Body(..., description="发货数量"),
    address_id: int = Body(..., description="地址id"),
    operate_date: str = Body(
        ..., description="计划操作日期", examples=["2021-01-01 00:00:00"]
    ),
    operate_people: str = Body(..., description="计划操作人"),
    notices: str = Body(..., description="备注"),
):
    """
    # 添加物流计划
    order_number和order_id必须有一个, 优先使用order_id
    ## params
    - **order_number**: 订单编号, 可选
    - **order_id**: 订单id, 可选
    - **address_id**: 地址id
    - **operate_date**: 计划操作日期
    - **operate_people**: 计划操作人
    - **notices**: 备注
    """
    with SessionLocal() as db:
        if order_field_type == "id":
            order = db.query(Order).filter(Order.id == order).first()
        else:
            order = db.query(Order).filter(Order.order_number == order).first()

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
        if not order:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "订单不存在"},
            )
        # 验证发货数量
        if amount > order.total_amount:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "发货数量不能大于订单数量"},
            )

        logistics = LogisticsPlan(
            order_id=order.id,
            order_number=order.order_number,
            address_id=address_id,
            plan_id=order.plan_id,
            amount=amount,
            operate_date=datetime.strptime(operate_date, "%Y-%m-%d %H:%M:%S"),
            operate_people=operate_people,
            notices=notices,
        )
        logistics.order = order
        db.add(logistics)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "添加成功"},
        )


@logistics_router.put("/update_logistics_status", summary="修改物流计划")
async def update_logistics_status(
    logistics_id: int = Body(..., description="物流计划id"),
    logistics_status: str = Body(..., description="状态"),
):
    """
    # 修改物流计划状态
    ## params
    - **logistics_id**: 物流计划id
    - **logistics_status**: 状态
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


@logistics_router.put("/update_logistics", summary="修改物流计划")
async def update_logistics(
    logistics_id: int = Body(..., description="物流计划id"),
    address_id: Optional[int] = Body(None, description="地址id"),
    amount: Optional[int] = Body(None, description="发货数量"),
    operate_date: Optional[str] = Body(None, description="计划操作日期"),
    operate_people: Optional[str] = Body(None, description="计划操作人"),
    notices: Optional[str] = Body(None, description="备注"),
):
    """
    # 修改物流计划
    ## params
    - **logistics_id**: 物流计划id
    - **address_id**: 地址id, 可选
    - **operate_date**: 计划操作日期, 可选
    - **operate_people**: 计划操作人, 可选
    - **notices**: 备注, 可选
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
                logistics.address_id = address_id
            if operate_date:
                logistics.operate_date = datetime.strptime(
                    operate_date, "%Y-%m-%d %H:%M:%S"
                )
            if operate_people:
                logistics.operate_people = operate_people
            if notices:
                logistics.notices = notices
            if amount:
                # 验证发货数量
                if amount > logistics.order.total_amount:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "发货数量不能大于订单数量"},
                    )
                logistics.amount = amount
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
