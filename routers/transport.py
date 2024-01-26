from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Query, status, Body
from fastapi.responses import JSONResponse

from schema.tables import Transport, Plan, Location
from schema.common import page_with_order
from schema.database import SessionLocal
from models.base import TransportSchema

transport_router = APIRouter()


@transport_router.get("/get_transports", summary="批量获取运输信息")
async def get_transports_api(
    location_name: str = Query(None, description="位置名称"),
    year: int = Query(None, description="年份"),
    batch: int = Query(None, description="批次"),
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
                schema=TransportSchema,
                query=query,
                page=page,
                page_size=page_size,
                order_field=order_field,
                order=order,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "success", "data": response},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.post("/add_transport", summary="添加运输信息")
async def add_transport_api(
    plan_id: int = Body(..., description="计划ID", example=1),
    operate_date: str = Body(..., description="操作时间", example="2021-01-01 00:00:00"),
    loader_worker: str = Body("", description="装车人"),
    driver: str = Body("", description="运输人员"),
    unload_worker: str = Body("", description="卸车人"),
    unload_place: str = Body("", description="卸车地点"),
    air_worker: str = Body("", description="晾晒人员"),
    clean_worker: str = Body("", description="清洗人员"),
    after_clean_driver: str = Body("", description="清洗后运输人员"),
    after_unload_worker: str = Body("", description="清洗后卸车人员"),
    after_unload_place: str = Body("", description="清洗后卸车地点"),
    notices: str = Body("", description="备注"),
):
    """
    # 添加运输信息
    ## params
    - **plan_id**: 计划ID
    - **operate_date**: 操作时间
    - **loader_worker**: 装车人, 可选
    - **driver**: 运输人员, 可选
    - **unload_worker**: 卸车人, 可选
    - **unload_place**: 卸车地点, 可选
    - **air_worker**: 晾晒人员, 可选
    - **clean_worker**: 清洗人员, 可选
    - **after_clean_driver**: 清洗后运输人员, 可选
    - **after_unload_worker**: 清洗后卸车人员, 可选
    - **after_unload_place**: 清洗后卸车地点, 可选
    - **notices**: 备注, 可选
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
                plan_id=plan.id,
                operate_date=datetime.strptime(operate_date, "%Y-%m-%d %H:%M:%S"),
                loading_worker=loader_worker,
                driver=driver,
                unload_worker=unload_worker,
                unload_place=unload_place,
                air_worker=air_worker,
                clean_worker=clean_worker,
                after_clean_driver=after_clean_driver,
                after_unload_worker=after_unload_worker,
                after_unload_place=after_unload_place,
                notices=notices,
            )
            db.add(transport)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加错误"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.put("/update_transport_status", summary="修改运输状态")
async def update_transport_status_api(
    transport_id: int = Body(..., description="运输ID"),
    status: str = Body(..., description="状态"),
):
    """
    # 修改运输状态
    ## params
    - **transport_id**: 运输ID
    - **status**: 状态
    """
    try:
        with SessionLocal() as db:
            transport = db.query(Transport).filter(Transport.id == transport_id).first()
            if not transport:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "运输信息不存在"},
                )
            transport.status = status
            db.commit()
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
):
    """
    # 删除运输信息
    ## params
    - **transport_id**: 运输ID
    """
    try:
        with SessionLocal() as db:
            transport = db.query(Transport).filter(Transport.id == transport_id).first()
            if not transport:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "运输信息不存在"},
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
