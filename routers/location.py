from typing import Literal
from fastapi import APIRouter, HTTPException, status, Body, Query
from fastapi.responses import JSONResponse

from schema.common import (
    transform_schema,
    page_with_order,
    query_with_filter,
    query_with_like_filter,
)
from models.base import LocationSchema
from schema.database import SessionLocal
from schema.tables import Location

location_router = APIRouter()


@location_router.get("/get_locations", summary="批量获取位置信息")
async def get_locations_api(
    order_field: str = "id",
    order: Literal["asc", "desc"] = "asc",
    page: int = 1,
    page_size: int = 10,
):
    """
    # 批量获取位置信息
    ## params
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认20，范围1-100, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    """
    try:
        with SessionLocal() as db:
            query = db.query(Location)
            response = page_with_order(
                schema=LocationSchema,
                query=query,
                page=page,
                page_size=page_size,
                order_field=order_field,
                order=order,
            )
            response.update({"code": 0, "message": "查询成功"})
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@location_router.get("/filter_locations", summary="过滤位置信息")
async def filter_location(
    name: str = Query(None, description="位置名称"),
    type: str = Query(None, description="位置类型"),
    customized: str = Query(None, description="是否定制"),
    fuzzy: bool = Query(False, description="是否模糊查询"),
    order_field: str = "id",
    order: Literal["asc", "desc"] = "asc",
    page: int = 1,
    page_size: int = 10,
):
    """
    # 过滤位置信息
    ## params
    - **name**: 位置名称, 可选
    - **type**: 位置类型, 可选
    - **customized**: 是否定制, 可选
    - **fuzzy**: 是否模糊查询, 可选
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认20，范围1-100, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    """
    try:
        with SessionLocal() as db:
            query = db.query(Location)
            if name:
                if fuzzy:
                    query = query_with_like_filter(query, name=name)
                else:
                    query = query_with_filter(query, name=name)
            if type:
                query = query_with_filter(query, type=type)
            if customized:
                query = query_with_filter(query, customized=customized)
            response = page_with_order(
                schema=LocationSchema,
                query=query,
                order_field=order_field,
                order=order,
                page=page,
                page_size=page_size,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=response,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@location_router.get("/get_location_by_id", summary="获取单个位置信息")
async def get_location_by_id_api(id: int = Query(..., description="位置id")):
    """
    # 获取单个位置信息
    ## params
    - **id**: 位置id
    """
    try:
        with SessionLocal() as db:
            query = db.query(Location).filter(Location.id == id)
            data = query.first()
            if not data:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 1,
                        "message": "查询失败, 不存在该位置",
                    },
                )
            data = transform_schema(LocationSchema, query.one())
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "查询成功",
                    "data": data,
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@location_router.post("/add_location", summary="添加位置信息")
async def add_location_api(
    name: str = Body(..., description="位置名称"),
    type: str = Body(default="仓库", description="位置类型"),
    longitude: float = Body(..., description="经度"),
    latitude: float = Body(..., description="纬度"),
    address: str = Body(..., description="地址"),
    area: float = Body(None, description="面积"),
    customized: str = Body("其他", description="是否定制"),
):
    """
    # 添加位置信息
    ## params
    - **location**: 位置信息
    """
    try:
        with SessionLocal() as db:
            location = Location(
                name=name,
                type=type,
                longitude=longitude,
                latitude=latitude,
                detail=address,
                area=area,
                customized=customized,
            )
            db.add(location)
            db.commit()

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加成功"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@location_router.put("/update_location", summary="更新位置信息")
async def update_location_api(
    id: int = Body(..., description="位置id"),
    name: str = Body(None, description="位置名称"),
    type: str = Body(None, description="位置类型", example="仓库"),
    longitude: float = Body(None, description="经度"),
    latitude: float = Body(None, description="纬度"),
    address: str = Body(None, description="地址"),
    area: float = Body(None, description="面积"),
    customized: str = Body(None, description="是否定制"),
):
    """
    # 更新位置信息
    ## params
    - **id**: 位置id
    - **name**: 位置名称
    - **type**: 位置类型
    - **longitude**: 经度
    - **latitude**: 纬度
    - **address**: 地址
    - **area**: 面积
    - **customized**: 是否定制
    """
    try:
        with SessionLocal() as db:
            query = db.query(Location).filter(Location.id == id)
            data = query.first()
            if not data:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 1,
                        "message": "更新失败, 不存在该位置",
                    },
                )
            if name:
                data.name = name
            if type:
                data.type = type
            if longitude or longitude == 0:
                data.longitude = longitude
            if latitude or latitude == 0:
                data.latitude = latitude
            if address:
                data.detail = address
            if area or area == 0:
                data.area = area
            if customized:
                data.customized = customized

            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "更新成功"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@location_router.delete("/delete_location", summary="删除位置信息")
async def delete_location_api(
    id: int = Query(..., description="位置id"),
):
    """
    # 删除位置信息
    ## params
    - **id**: 位置id
    """
    try:
        with SessionLocal() as db:
            query = db.query(Location).filter(Location.id == id)
            data = query.first()
            if not data:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 1,
                        "message": "删除失败, 不存在该位置",
                    },
                )
            db.delete(data)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@location_router.get("/get_all_locations_name", summary="获取所有位置名称")
async def get_all_locations_name_api():
    """
    # 获取所有位置名称
    """
    try:
        with SessionLocal() as db:
            query = db.query(Location.name).distinct()
            print(query.all())
            data = [item[0] for item in query.all()]
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "查询成功", "data": data},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
