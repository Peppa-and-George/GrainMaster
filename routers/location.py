from fastapi import APIRouter, Depends, Body, Query
from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import Field

from models.common import ResStatus
from models.location import (
    BatchQueryLocationsModel,
    LocationNecessaryFields,
    LocationSchema,
    FilterLocationModel,
)
from models.location import BatchQueryLocationsResponseModel
from schema.location import (
    query_locations,
    add_location,
    delete_location,
    get_location_by_id,
    filter_location,
    update_location,
)

location_router = APIRouter(prefix="/location", tags=["位置管理"])


@location_router.get(
    "/get_locations",
    summary="批量获取位置信息",
    response_model=BatchQueryLocationsResponseModel,
)
async def get_locations(params: BatchQueryLocationsModel = Depends()):
    """
    # 批量获取位置信息
    ## params
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认20，范围1-100, 可选
    - **orderField**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    """
    res = query_locations(params)
    if res is None:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(**{"code": 1, "message": "查询失败, 该位置不存在"}).model_dump(),
        )
    res = BatchQueryLocationsResponseModel.model_validate(res, from_attributes=True)

    return JSONResponse(status_code=status.HTTP_200_OK, content=res.model_dump())


@location_router.post(
    "/add_location",
    summary="添加位置信息",
    response_model=ResStatus,
)
async def add_location_api(params: LocationNecessaryFields = Body(...)):
    """
    # 添加位置信息
    ## params
    - **name**: 位置名称, 必填
    - **type**: 位置类型, 必填
    - **detail**: 详细地址, 可选
    - **longitude**: 经度, 必填
    - **latitude**: 纬度, 必填
    """
    try:
        add_location(params)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(**{"code": 0, "message": "添加成功"}).model_dump(),
        )
    except Exception as e:
        raise JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(**{"code": 1, "message": str(e)}).model_dump(),
        )


@location_router.delete(
    "/delete_location",
    summary="删除位置信息",
    response_model=ResStatus,
)
async def delete_location_api(
    location_id: int = Query(..., description="位置id", example=1)
):
    """
    # 删除位置信息
    ## params
    - **location_id**: 位置id, 必填
    """
    deleted_row = delete_location(location_id)
    if deleted_row == 0:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(**{"code": 1, "message": "删除失败, 该位置不存在"}).model_dump(),
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(**{"code": 0, "message": "删除成功"}).model_dump(),
        )


@location_router.get(
    "/get_location_by_id",
    summary="根据id获取位置信息",
    response_model=ResStatus,
)
async def get_location_by_id_api(
    location_id: int = Query(..., description="位置id", example=1)
):
    """
    # 根据id获取位置信息
    ## params
    - **location_id**: 位置id, 必填
    """
    res = get_location_by_id(location_id)
    if res is None:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(**{"code": 1, "message": "查询失败, 该位置不存在"}).model_dump(),
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(
                **{
                    "code": 0,
                    "message": "查询成功",
                    "data": LocationSchema.model_validate(res),
                }
            ).model_dump(),
        )


@location_router.get(
    "/filter_location",
    summary="根据条件筛选位置信息",
    response_model=BatchQueryLocationsResponseModel,
)
async def filter_location_api(params: FilterLocationModel = Depends()):
    """
    # 根据条件筛选位置信息
    ## params
    - **name**: 位置名称, 可选, 默认null
    - **type**: 位置类型, 可选, 默认null
    - **customized**: 是否定制, 可选, 默认null - **fuzzy**: 是否模糊查询, 可选, 默认False
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认20，范围1-100, 可选
    - **orderField**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    """
    res = filter_location(params)

    res = BatchQueryLocationsResponseModel.model_validate(res, from_attributes=True)
    return JSONResponse(status_code=status.HTTP_200_OK, content=res.model_dump())


@location_router.put(
    path="/update_product",
    summary="更新产品信息",
    response_model=ResStatus,
)
async def update_product_api(
    id: int = Body(default=..., title="位置ID", description="位置ID"),
    params: LocationNecessaryFields = Body(...),
):
    """
    # 更新产品信息
    ## params
    - **id**: 位置id, 必填
    - **name**: 位置名称, 必填
    - **type**: 位置类型, 必填
    - **detail**: 详细地址, 可选
    - **longitude**: 经度, 必填
    - **latitude**: 纬度, 必填
    - **customized**: 是否定制, 可选, 默认null
    - **area**: 面积, 可选, 默认null
    """
    res = update_location(id, params)
    if res == 0:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(**{"code": 1, "message": "更新失败, 该位置不存在"}).model_dump(),
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(**{"code": 0, "message": "更新成功"}).model_dump(),
        )
