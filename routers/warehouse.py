from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Query, status, Body, HTTPException
from fastapi.responses import JSONResponse

from schema.tables import Transport, Plan, Location, Warehouse
from schema.common import page_with_order
from schema.database import SessionLocal
from models.base import WarehouseSchema

warehouse_router = APIRouter()


@warehouse_router.get("/get_warehouse", summary="获取仓库信息")
async def get_warehouse(
    year: int = Query(None, description="年份"),
    batch: int = Query(None, description="批次"),
    location_name: str = Query(None, description="基地名称"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order: Literal["asc", "desc"] = Query("asc", description="排序"),
    order_field: str = Query("id", description="排序字段"),
):
    """
    # 获取仓库信息
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
            query = db.query(Warehouse).join(Plan, Plan.id == Warehouse.plan_id)
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
                schema=WarehouseSchema,
                query=query,
                page=page,
                page_size=page_size,
                order=order,
                order_field=order_field,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "获取成功", "data": response},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仓库信息失败, {e}",
        )


@warehouse_router.post("/add_warehouse", summary="添加仓库信息")
async def add_warehouse(
    plan_id: int = Body(..., description="计划ID"),
    operate_date: str = Body(..., description="计划操作日期"),
    feeding_place: str = Body(..., description="投料口转运"),
    feeding_warehouse: str = Body(..., description="投料仓转运地点"),
    feeding: str = Body(..., description="投料"),
    press: str = Body(..., description="压榨"),
    refine: str = Body(..., description="精炼"),
    sorting: str = Body(..., description="分装"),
    warehousing: str = Body(..., description="入库"),
    product_warehousing: str = Body(..., description="成品入库地点"),
    notices: str = Body(..., description="备注"),
):
    """
    # 添加仓库信息
    ## params
    - **plan_id**: 计划ID
    - **operate_date**: 计划操作日期
    - **feeding_place**: 投料口转运
    - **feeding_warehouse**: 投料仓转运地点
    - **feeding**: 投料
    - **press**: 压榨
    - **refine**: 精炼
    - **sorting**: 分装
    - **warehousing**: 入库
    - **product_warehousing**: 成品入库地点
    - **notices**: 备注
    """
    try:
        with SessionLocal() as db:
            plan = db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "计划不存在"},
                )
            warehouse = Warehouse(
                plan_id=plan_id,
                operate_date=datetime.strptime(operate_date, "%Y-%m-%d %H:%M:%S"),
                feeding_place=feeding_place,
                feeding_warehouse=feeding_warehouse,
                feeding=feeding,
                press=press,
                refine=refine,
                sorting=sorting,
                warehousing=warehousing,
                product_warehousing=product_warehousing,
                notices=notices,
            )
            db.add(warehouse)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加仓库信息失败, {e}",
        )


@warehouse_router.put("/update_warehouse_status", summary="更新仓储加工状态信息")
async def update_warehouse_status(
    warehouse_id: int = Body(..., description="仓库ID"),
    warehouse_status: str = Body(..., description="状态"),
):
    """
    # 更新仓库状态信息
    ## params
    - **warehouse_id**: 仓库ID
    - **warehouse_status**: 状态
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
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "更新成功"},
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新仓库状态信息失败, {e}",
        )


@warehouse_router.delete("/delete_warehouse", summary="删除仓库信息")
async def delete_warehouse(
    warehouse_id: int = Query(..., description="仓库ID"),
):
    """
    # 删除仓库信息
    ## params
    - **id**: 仓库ID
    """
    try:
        with SessionLocal() as db:
            warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
            if not warehouse:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "仓储信息不存在"},
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
