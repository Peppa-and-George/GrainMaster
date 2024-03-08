import io
import uuid
from datetime import datetime
from typing import Optional, Literal

import qrcode

from fastapi.routing import APIRouter
from fastapi import Query, status, HTTPException, Body
from fastapi.responses import JSONResponse, Response

from models.base import (
    LocationSchema,
    PlantPlanSchema,
    TransportSchema,
    WarehouseSchema,
    LogisticsPlanSchema,
    PlanSchema,
)
from schema.database import SessionLocal
from schema.tables import (
    Traceability,
    Plan,
    Location,
    PlantPlan,
    Transport,
    Warehouse,
    LogisticsPlan,
)
from schema.common import query_with_page, query_with_order, transform_schema
from config import BASE_URL

traceability_router = APIRouter()


def datetime_to_str(obj):
    if obj:
        return datetime.strftime(obj, "%Y-%m-%d %H:%M:%S")
    return None


@traceability_router.get("/get_traceability", summary="批量获取溯源信息")
async def get_traceability(
    plan_id: Optional[int] = Query(None, description="计划id"),
    year: Optional[int] = Query(None, description="年份"),
    batch: Optional[int] = Query(None, description="批次"),
    location: Optional[str] = Query(None, description="基地名称"),
    location_id: Optional[int] = Query(None, description="基地id"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序方式"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
):
    """
    # 批量获取溯源信息
    - **plan_id**: 计划id, 可选
    - **year**: 年份, 可选
    - **batch**: 批次, 可选
    - **location**: 基地名称, 可选
    - **location_id**: 基地id, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, 默认为"desc", 可选
    - **page**: 页码, 默认为1, 可选
    - **page_size**: 每页数量, 默认为20, 可选
    """
    try:
        with SessionLocal() as db:
            query = (
                db.query(Traceability)
                .join(Plan, Traceability.plan_id == Plan.id)
                .join(Location, Plan.location_id == Location.id)
            )
            if plan_id:
                query = query.filter(Traceability.plan_id == plan_id)
            if year:
                query = query.filter(Plan.year == year)
            if batch:
                query = query.filter(Plan.batch == batch)
            if location:
                query = query.filter(Location.name == location)
            if location_id:
                query = query.filter(Location.id == location_id)

            # 分页
            total = query.count()
            total_page = (total + page_size - 1) // page_size
            query = query_with_order(query, order_field, order)
            query = query_with_page(query, page, page_size)
            objs = query.all()
            data = []

            for item in objs:
                url = f"/traceability/detail?code={item.traceability_code}"
                data.append(
                    {
                        "id": item.id,
                        "plan_id": item.plan.id,
                        "traceability_code": item.traceability_code,
                        "location_id": item.plan.location_id,
                        "location_name": item.plan.location.name,
                        "year": item.plan.year,
                        "batch": item.plan.batch,
                        "url": url,
                        "print_status": item.print_status,
                        "used_time": datetime_to_str(item.used_time),
                        "used": item.used,
                        "created_time": datetime_to_str(item.create_time),
                        "updated_time": datetime_to_str(item.update_time),
                    }
                )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "查询成功",
                    "data": data,
                    "total": total,
                    "total_page": total_page,
                    "page": page,
                    "page_size": page_size,
                    "order_field": order_field,
                    "order": order,
                },
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@traceability_router.get("/detail", summary="获取溯源详情")
async def get_traceability_detail(
    traceability: str = Query(..., description="溯源码标识"),
    field_type: Literal["id", "code"] = Query("code", description="字段类型"),
):
    """
    # 获取溯源详情
    - **traceability**: 溯源码
    - **field_type**: 字段类型, id: 溯源id, code: 溯源码, 默认为code
    """
    try:
        with SessionLocal() as db:
            if field_type == "id":
                obj = (
                    db.query(Traceability)
                    .filter(Traceability.id == traceability)
                    .first()
                )
            else:
                obj = (
                    db.query(Traceability)
                    .filter(Traceability.traceability_code == traceability)
                    .first()
                )
            if not obj:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "溯源码不存在"},
                )
            obj.used = True
            obj.used_time = datetime.now()
            db.commit()
            plan = db.query(Plan).filter(Plan.id == obj.plan_id).first()

            plants = db.query(PlantPlan).filter(PlantPlan.plan_id == obj.plan_id).all()
            transports = (
                db.query(Transport).filter(Transport.plan_id == obj.plan_id).all()
            )
            warehouses = (
                db.query(Warehouse).filter(Warehouse.plan_id == obj.plan_id).all()
            )
            logistics = (
                db.query(LogisticsPlan)
                .filter(LogisticsPlan.order_id == obj.plan_id)
                .all()
            )
            location = (
                db.query(Location).filter(Location.id == obj.plan.location_id).first()
            )
            data = {
                "id": obj.id,
                "plan_id": obj.plan.id,
                "traceability_code": obj.traceability_code,
                "location_id": obj.plan.location_id,
                "print_status": obj.print_status,
                "used_time": datetime_to_str(obj.used_time),
                "used": obj.used,
                "created_time": datetime_to_str(obj.create_time),
                "updated_time": datetime_to_str(obj.update_time),
                "location": transform_schema(LocationSchema, location)[0],
                "plan": transform_schema(PlanSchema, plan)[0],
                "plants": transform_schema(PlantPlanSchema, plants),
                "transports": transform_schema(TransportSchema, transports),
                "warehouses": transform_schema(WarehouseSchema, warehouses),
                "logistics": transform_schema(LogisticsPlanSchema, logistics),
            }

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "查询成功", "data": data},
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@traceability_router.get("/get_qrcode", summary="获取二维码")
def get_qrcode(
    traceability: str = Query(..., description="溯源码标识"),
    field_type: Literal["id", "code"] = Query("code", description="字段类型"),
    size: int = Query(200, description="二维码尺寸"),
):
    """
    # 获取二维码
    - **traceability**: 溯源码
    - **field_type**: 字段类型, id: 溯源id, code: 溯源码, 默认为code
    - **size**: 二维码尺寸, 默认为200, 单位px， 可选
    """
    if field_type == "code":
        traceability_code = traceability
    else:
        with SessionLocal() as db:
            traceability_code = (
                db.query(Traceability).filter(Traceability.id == traceability).first()
            ).traceability_code
    img = qrcode.make(
        f"{BASE_URL}/traceability/detail?traceability={traceability_code}&field_type={field_type}"
    )
    img = img.resize((size, size))

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr = img_byte_arr.getvalue()

    return Response(
        status_code=status.HTTP_200_OK, content=img_byte_arr, media_type="image/jpeg"
    )


@traceability_router.delete("/delete_traceability", summary="删除溯源信息")
async def delete_traceability(
    traceability: str = Query(..., description="溯源码标识"),
    field_type: Literal["id", "code"] = Query("code", description="字段类型"),
):
    """
    # 删除溯源信息
    - **traceability**: 溯源码
    - **field_type**: 字段类型, id: 溯源id, code: 溯源码, 默认为code
    """
    try:
        with SessionLocal() as db:
            if field_type == "id":
                obj = (
                    db.query(Traceability)
                    .filter(Traceability.id == traceability)
                    .first()
                )
            else:
                obj = (
                    db.query(Traceability)
                    .filter(Traceability.traceability_code == traceability)
                    .first()
                )
            if not obj:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "溯源码不存在"},
                )
            db.delete(obj)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@traceability_router.post("add_traceability", summary="添加溯源信息")
async def add_traceability(
    plan_id: int = Body(..., description="计划id"),
):
    """
    # 添加溯源信息
    - **plan_id**: 计划id
    """
    try:
        with SessionLocal() as db:
            plan = db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "计划不存在"},
                )
            obj = Traceability(
                traceability_code=f"{plan.year}-{plan.batch}-{uuid.uuid4().hex[:8]}"
            )
            obj.plan = plan
            db.add(obj)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@traceability_router.put("/update_traceability", summary="修改溯源信息")
async def update_traceability(
    traceability: str = Body(..., description="溯源码标识"),
    field_type: Literal["id", "code"] = Body("code", description="字段类型"),
    print_status: Optional[bool] = Body(
        None, description="打印状态", examples=[True, False]
    ),
    used: Optional[bool] = Body(None, description="是否使用", examples=[True, False]),
    used_time: Optional[str] = Body(
        None, description="使用时间", examples=["2021-01-01 00:00:00"]
    ),
):
    """
    # 修改溯源信息
    - **traceability**: 溯源码
    - **field_type**: 字段类型, id: 溯源id, code: 溯源码, 默认为code
    - **print_status**: 打印状态, bool类型 可选
    - **used**: 是否使用, bool类型 可选
    - **used_time**: 使用时间, 可选
    """
    try:
        with SessionLocal() as db:
            if field_type == "id":
                obj = (
                    db.query(Traceability)
                    .filter(Traceability.id == traceability)
                    .first()
                )
            else:
                obj = (
                    db.query(Traceability)
                    .filter(Traceability.traceability_code == traceability)
                    .first()
                )
            if not obj:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "溯源码不存在"},
                )
            if print_status is not None:
                obj.print_status = print_status
            if used is not None:
                obj.used = used
            if used_time:
                obj.used_time = datetime.strptime(used_time, "%Y-%m-%d %H:%M:%S")
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "修改成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@traceability_router.get("/print_traceability", summary="根据计划id获取溯源信息")
async def print_traceability(
    traceability: str = Query(..., description="溯源码标识"),
    field_type: Literal["id", "code"] = Query("code", description="字段类型"),
):
    """
    # 根据计划id获取溯源信息
    - **traceability**: 溯源码
    - **field_type**: 字段类型, id: 溯源id, code: 溯源码, 默认为code
    """
    try:
        with SessionLocal() as db:
            if field_type == "id":
                obj = (
                    db.query(Traceability)
                    .filter(Traceability.id == traceability)
                    .first()
                )
            else:
                obj = (
                    db.query(Traceability)
                    .filter(Traceability.traceability_code == traceability)
                    .first()
                )
            if not obj:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "溯源码不存在"},
                )
            obj.print_status = True
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "打印成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
