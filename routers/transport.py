# 原料运输
from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Query, status, Body
from fastapi.responses import JSONResponse

from schema.tables import Transport, Plan, Location, Quality
from schema.common import page_with_order
from schema.database import SessionLocal
from models.base import TransportSchema

transport_router = APIRouter()


@transport_router.get("/get_transports", summary="批量获取运输信息")
async def get_transports_api(
    location: str = Query(None, description="位置信息"),
    location_type: Literal["id", "name"] = Query(id, description="位置类型"),
    year: int = Query(None, description="年份"),
    batch: int = Query(None, description="批次"),
    transport_status: Literal["准备运输", "运输中", "运输完成"] = Query(None, description="运输状态"),
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
            if location:
                if location_type == "id":
                    query = query.filter(Plan.location_id == location)
                else:
                    query = query.join(
                        Location, Location.id == Plan.location_id
                    ).filter(Location.name == location)
            if transport_status:
                query = query.filter(Transport.status == transport_status)
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
                content=response,
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.post("/add_transport", summary="添加运输信息")
async def add_transport_api(
    plan_id: int = Body(..., description="计划ID", examples=[1]),
    operate_date: str = Body(..., description="操作时间", examples=["2021-01-01 00:00:00"]),
    driver: Optional[str] = Body(None, description="运输人员"),
    unloading_place: Optional[str] = Body("", description="卸车地点"),
    loading_place: Optional[str] = Body("", description="装车地点"),
    remark: Optional[str] = Body("", description="备注"),
):
    """
    # 添加运输信息
    ## params
    - **plan_id**: 计划ID, int
    - **operate_date**: 操作时间, str, 格式为"2021-01-01 00:00:00"
    - **driver**: 运输人员, str, 可选
    - **unloading_place**: 卸车地点, str
    - **loading_place**: 装车地点, str
    - **remark**: 备注, str, 可选
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
                driver=driver,
                unloading_place=unloading_place,
                loading_place=loading_place,
                remark=remark,
            )

            quality = Quality(type="原料运输", status="未上传", name="原料运输质检报告")
            transport.qualities.append(quality)

            db.add(transport)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加成功"},
            )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 1, "message": str(e)},
        )


@transport_router.put("/update_transport_status", summary="修改运输状态")
async def update_transport_status_api(
    transport_id: int = Body(..., description="运输ID"),
    transport_status: Literal["准备运输", "运输中", "运输完成"] = Body(..., description="状态"),
):
    """
    # 修改运输状态
    ## params
    - **transport_id**: 运输ID, int
    - **transport_status**: 状态, 枚举类型, 可选值: "准备运输", "运输中", "运输完成"
    """
    try:
        with SessionLocal() as db:
            transport = db.query(Transport).filter(Transport.id == transport_id).first()
            if not transport:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "运输信息不存在"},
                )
            transport.status = transport_status
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


@transport_router.put("/update_transport", summary="更新运输信息")
async def update_transport_api(
    transport_id: int = Body(..., description="运输ID"),
    plan_id: Optional[int] = Body(None, description="计划ID"),
    operate_date: Optional[str] = Body(
        None, description="操作时间", examples=["2021-01-01 00:00:00"]
    ),
    driver: Optional[str] = Body(None, description="运输人员"),
    unloading_place: Optional[str] = Body(None, description="卸车地点"),
    loading_place: Optional[str] = Body(None, description="装车地点"),
    remark: Optional[str] = Body(None, description="备注"),
):
    """
    # 更新运输信息
    ## params
    - **transport_id**: 运输ID, int
    - **plan_id**: 计划ID, int, 可选
    - **operate_date**: 操作时间, str, 可选
    - **driver**: 运输人员, str, 可选
    - **unloading_place**: 卸车地点, str, 可选
    - **loading_place**: 装车地点, str, 可选
    - **remark**: 备注, str, 可选
    """
    try:
        with SessionLocal() as db:
            transport = db.query(Transport).filter(Transport.id == transport_id).first()
            if not transport:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "运输信息不存在"},
                )
            if plan_id:
                plan = db.query(Plan).filter(Plan.id == plan_id).first()
                if not plan:
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={"code": 1, "message": "关联的计划不存在"},
                    )
                transport.plan_id = plan.id
            if operate_date:
                transport.operate_date = datetime.strptime(
                    operate_date, "%Y-%m-%d %H:%M:%S"
                )
            if driver:
                transport.driver = driver
            if unloading_place:
                transport.unloading_place = unloading_place
            if loading_place:
                transport.loading_place = loading_place
            if remark:
                transport.remark = remark
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
