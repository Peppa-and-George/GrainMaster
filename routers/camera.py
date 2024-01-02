from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from models.camera import (
    BatchQueryCameraResponseModel,
    AddCameraModel,
    FilterCameraModel,
)
from schema.camera import (
    query_cameras,
    add_camera,
    filter_cameras,
    delete_camera,
    update_camera,
)
from models.common import CommonQueryParm, ResStatus

camera_router = APIRouter(prefix="/camera", tags=["摄像头管理"])


@camera_router.get(
    "/get_cameras", summary="批量获取摄像头信息", response_model=BatchQueryCameraResponseModel
)
async def get_cameras_api(
    params: CommonQueryParm = Depends(),
):
    """
    # 批量获取摄像头信息
    ## params
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认20，范围1-100, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    """
    try:
        res = query_cameras(params)
        cameras_data = BatchQueryCameraResponseModel.model_validate(
            res, from_attributes=True
        )
        return cameras_data.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@camera_router.get(
    path="filter_cameras",
    summary="筛选摄像头信息",
    response_model=BatchQueryCameraResponseModel,
)
async def filter_cameras_api(params: FilterCameraModel = Depends()):
    """
    # 筛选摄像头信息
    ## params
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认20，范围1-100, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    - **name**: 摄像头名称, 可选
    - **address**: 摄像头地址, 可选
    - **step**: 所属环节, 可选
    """
    try:
        res = filter_cameras(params)
        cameras_data = BatchQueryCameraResponseModel.model_validate(
            res, from_attributes=True
        )
        return cameras_data.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@camera_router.post("/add_camera", summary="添加摄像头")
async def add_camera_api(params: AddCameraModel):
    """
    # 添加摄像头
    ## params
    - **name**: 摄像头名称, 必填
    - **sn**: 摄像头序列号, 必填
    - **state**: 摄像头状态, 必填
    - **address**: 摄像头地址, 可选
    - **location**: 摄像头位置, 可选
    - **step**: 所属环节, 可选
    """
    try:
        add_camera(params)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(**{"code": 0, "message": "添加成功"}).model_dump(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@camera_router.delete("/delete_camera", summary="删除摄像头")
async def delete_camera_api(camera_id: int):
    """
    # 删除摄像头
    ## params
    - **camera_id**: 摄像头id, 必填
    """
    try:
        deleted_row = delete_camera(camera_id)
        if deleted_row == 0:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResStatus(
                    **{"code": 1, "message": "删除失败, 该摄像头不存在"}
                ).model_dump(),
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(**{"code": 0, "message": "删除成功"}).model_dump(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@camera_router.put("/update_camera", summary="更新摄像头")
async def update_camera_api(camera_id: int, params: AddCameraModel):
    """
    # 更新摄像头
    ## params
    - **camera_id**: 摄像头id, 必填
    - **name**: 摄像头名称, 必填
    - **sn**: 摄像头序列号, 必填
    - **state**: 摄像头状态, 必填
    - **address**: 摄像头地址, 可选
    - **location**: 摄像头位置, 可选
    - **step**: 所属环节, 可选
    """
    try:
        updated_row = update_camera(camera_id, params)
        if updated_row == 0:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content=ResStatus(
                    **{"code": 1, "message": "更新失败, 该摄像头不存在"}
                ).model_dump(),
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ResStatus(**{"code": 0, "message": "更新成功"}).model_dump(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
