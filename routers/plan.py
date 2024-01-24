from typing import Literal

from fastapi.responses import JSONResponse
from fastapi import status, Depends
from fastapi.exceptions import HTTPException

from fastapi import APIRouter, Query
from schema.database import SessionLocal
from schema.common import page_with_order, transform_schema
from schema.tables import Plan, Location
from models.base import PlanSchema

plan_router = APIRouter()


@plan_router.get("/plans")
async def get_plans(
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序类型"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    try:
        with SessionLocal() as db:
            query = db.query(Plan)
            data = page_with_order(
                schema=PlanSchema,
                query=query,
                page=page,
                page_size=page_size,
                order_field=order_field,
                order=order,
            )
            return JSONResponse(status_code=status.HTTP_200_OK, content=data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


def get_location_id_by_name(name: str) -> int:
    with SessionLocal() as db:
        location = db.query(Location).filter(Location.name == name).first()
        if not location:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="基地不存在")
        return location.id


@plan_router.post("/add_plan")
async def add_plan(
    year: int = Query(..., description="年份"),
    location: str = Depends(get_location_id_by_name),
    total_material: int = Query(..., description="总产量(L)"),
):
    try:
        with SessionLocal() as db:
            plan = Plan(year=year, location_id=location, total_material=total_material)
            db.add(plan)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@plan_router.put("/update_plan")
async def update_plan(
    plan_id: int = Query(..., description="计划ID"),
    year: int = Query(..., description="年份"),
    location: str = Depends(get_location_id_by_name),
    total_material: int = Query(..., description="总产量(L)"),
):
    try:
        with SessionLocal() as db:
            plan = db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在"
                )
            plan.year = year
            plan.location_id = location
            plan.total_material = total_material
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "修改成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@plan_router.delete("/delete_plan")
async def delete_plan(
    plan_id: int = Query(..., description="计划ID"),
):
    try:
        with SessionLocal() as db:
            plan = db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在"
                )
            db.delete(plan)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@plan_router.get("/filter_plan")
async def filter_plan(
    year: int | None = Query(None, description="年份"),
    location: str | None = Query(None, description="基地名称"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序类型"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    try:
        with SessionLocal() as db:
            query = db.query(Plan)
            if location:
                location_id = get_location_id_by_name(location)
                query = query.filter(Plan.location_id == location_id)
            if year:
                query = query.filter(Plan.year == year)
            plans = query.all()
            if not plans:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="计划不存在"
                )
            response = page_with_order(
                schema=PlanSchema,
                query=query,
                page=page,
                page_size=page_size,
                order_field=order_field,
                order=order,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "查询成功", "data": response},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
