# from typing import Literal
#
# from fastapi import Depends, HTTPException, status, Body, APIRouter, Query
# from fastapi.responses import JSONResponse
#
# from schema.common import page_with_order, transform_schema
#
# segment_router = APIRouter()
#
# @segment_router.get("/get_segments", summary="批量获取种植环节信息")
# async def get_segments_api(
#     plant_id: int = Query(None, description="种植id"),
#     order_field: str = "id",
#     order: Literal["asc", "desc"] = "asc",
#     page: int = 1,
#     page_size: int = 10,
# ):
#     """
#     # 批量获取种植环节信息
#     ## params
#     - **plant_id**: 种植id, 可选
#     - **page**: 页码, 从1开始, 可选
#     - **page_size**: 分页大小，默认20，范围1-100, 可选
#     - **order_field**: 排序字段, 默认为"id", 可选
#     - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
#     """
#     pass
