# from datetime import datetime
# from typing import Literal
#
# from fastapi import APIRouter, Query, HTTPException, status, Body
# from fastapi.responses import JSONResponse
#
# from schema.tables import Plant, Location, PlantSegment
# from schema.common import page_with_order, transform_schema
# from schema.database import SessionLocal
#
# from models.base import PlantSchema
#
#
# plant_router = APIRouter()
#
#
# @plant_router.get("/get_plants", summary="批量获取田间种植信息")
# async def get_plants_api(
#     location_name: str = Query(None, description="位置名称"),
#     year: int = Query(None, description="年份"),
#     batch: int = Query(None, description="批次"),
#     order_field: str = "id",
#     order: Literal["asc", "desc"] = "asc",
#     page: int = 1,
#     page_size: int = 10,
# ):
#     """
#     # 批量获取田间种植信息
#     ## params
#     - **location_name**: 位置名称, 可选
#     - **year**: 年份, 可选
#     - **batch**: 批次, 可选
#     - **page**: 页码, 从1开始, 可选
#     - **page_size**: 分页大小，默认20，范围1-100, 可选
#     - **order_field**: 排序字段, 默认为"id", 可选
#     - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
#     """
#     try:
#         with SessionLocal() as db:
#             query = db.query(Plant)
#             if year:
#                 query = query.filter(Plant.year == year)
#             if batch:
#                 query = query.filter(Plant.batch == batch)
#             if location_name:
#                 location = (
#                     db.query(Location).filter(Location.name == location_name).first()
#                 )
#                 if not location:
#                     return JSONResponse(
#                         status_code=status.HTTP_200_OK,
#                         content={"code": 1, "message": "位置不存在"},
#                     )
#                 query = query.filter(Plant.location_name == location_name)
#             response = page_with_order(
#                 schema=PlantSchema,
#                 query=query,
#                 page=page,
#                 page_size=page_size,
#                 order_field=order_field,
#                 order=order,
#             )
#             response.update({"code": 0, "message": "查询成功"})
#             return response
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @plant_router.post("/add_plant", summary="添加田间种植信息")
# async def add_plant_api(
#     plan_id: int = Body(..., description="计划ID"),
#     operator: str = Body(..., description="操作人"),
#     operation_date: str = Body(..., description="操作时间"),
#     segment_name: str = Body(..., description="种植环节名称"),
#     remarks: str = Body(None, description="备注"),
# ):
#     """
#     # 添加田间种植信息
#     ## params
#     - **plant**: 田间种植信息
#     """
#     try:
#         with SessionLocal() as db:
#             segment = (
#                 db.query(PlantSegment).filter(PlantSegment.name == segment_name).first()
#             )
#             if not segment:
#                 return JSONResponse(
#                     status_code=status.HTTP_200_OK,
#                     content={"code": 1, "message": "种植环节不存在"},
#                 )
#             plant = Plant(
#                 plan_id=plan_id,
#                 operator=operator,
#                 operation_date=datetime.strptime(operation_date, "%Y-%m-%d %H:%M:%S"),
#                 segment=segment.id,
#                 remarks=remarks,
#             )
#             db.add(plant)
#             db.commit()
#             return JSONResponse(
#                 status_code=status.HTTP_200_OK,
#                 content={"code": 0, "message": "添加成功", "data": plant},
#             )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
