from datetime import datetime
from typing import Literal, Optional

from fastapi import (
    APIRouter,
    Query,
    HTTPException,
    status,
    Body,
    File,
    UploadFile,
    Form,
)
from fastapi.responses import JSONResponse
from sqlalchemy import desc

from dependency.videos import save_video, delete_video
from schema.tables import Segment, PlantOperate, PlanSegmentRelationship, Plan, Location
from schema.common import page_with_order
from schema.database import SessionLocal
from dependency.upload_image import save_image, delete_image

from models.base import PlanSegmentRelationshipSchema

plant_router = APIRouter()


@plant_router.get("/filter_plant_operation", summary="获取种植环节操作步骤")
async def get_plant_operate_api(
    segment_name: str = Query(None, description="种植环节名称"),
    segment_id: int = Query(None, description="种植环节ID"),
    order_field: str = "id",
    order: Literal["asc", "desc"] = "asc",
    page: int = 1,
    page_size: int = 10,
):
    """
    # 获取种植环节操作步骤,segment_name与segment_id只能传一个，如果两个都传，以segment_id为准
    ## params
    - **segment_name**: 种植环节名称
    - **segment_id**: 种植环节ID
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认20，范围1-100, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    """
    try:
        with SessionLocal() as db:
            query = db.query(PlantOperate).join(
                Segment, Segment.id == PlantOperate.segment_id
            )
            if segment_id:
                query = query.filter(Segment.id == segment_id)
            elif segment_name:
                query = query.filter(Segment.name == segment_name)
            total = query.count()
            if total == 0:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "未查询到数据"},
                )
            query = query.order_by(getattr(PlantOperate, order_field))
            if order == "desc":
                query = desc(query)

            query = query.offset((page - 1) * page_size).limit(page_size)

            data = {}
            operations = []
            for item in query.all():
                operation_name = item.name
                segment_name = item.segment.name
                index = item.index
                if segment_name not in data:
                    data[segment_name] = []
                data[segment_name].append(
                    {"operation_name": operation_name, "index": index}
                )
            response = [
                {"segment_name": segment_name, "operations": data[segment_name]}
                for segment_name in data
            ]

            page = (
                total // page_size + 1 if total % page_size != 0 else total // page_size
            )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 0,
                    "message": "查询成功",
                    "total": total,
                    "page": page,
                    "data": response,
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plant_router.get("/get_plan_segment_relationship", summary="获取田间种植计划")
async def get_plan_segment_relationship_api(
    year: int = Query(None, description="年份"),
    batch: int = Query(None, description="批次"),
    location_name: str = Query(None, description="地点"),
    order_field: str = "plan_id",
    order: Literal["asc", "desc"] = "asc",
    page: int = 1,
    page_size: int = 10,
):
    """
    # 获取田间种植计划
    ## params
    - **year**: 年份
    - **batch**: 批次
    - **location_name**: 基地名称
    - **page**: 页码, 从1开始, 可选
    - **page_size**: 分页大小，默认10，范围1-100, 可选
    - **order_field**: 排序字段, 默认为"id", 可选
    - **order**: 排序方式, asc: 升序, desc: 降序, 默认升序， 可选
    """

    with SessionLocal() as db:
        query = db.query(PlanSegmentRelationship).join(
            Plan, Plan.id == PlanSegmentRelationship.plan_id
        )
        if year:
            query = query.filter(Plan.year == year)
        if batch:
            query = query.filter(Plan.batch == batch)
        if location_name:
            location = db.query(Location).filter(Location.name == location_name).first()

            if not location:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "地点不存在"},
                )
            query = query.filter(Plan.location_id == location.id)

        response = page_with_order(
            schema=PlanSegmentRelationshipSchema,
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


@plant_router.post("/add_plant_segment", summary="添加种植环节")
async def add_plant_segment_api(
    segment_name: str = Body(..., description="种植环节名称"),
    operate_step: list[dict] = Body(
        ...,
        description="操作步骤",
        examples=[
            [
                {"operate_name": "步骤一", "index": 1},
                {"operate_name": "步骤二", "index": 2},
            ]
        ],
    ),
):
    """
    # 添加种植环节
    ## params
    - **segment_name**: 种植环节名称
    - **operate_step**: 操作步骤, 为一个列表，列表中的每个元素为一个字典，字典中包含两个字段，operate_name: 操作名称, index: 操作顺序, 示例：
    ```json
    [
        {"operate_name": "步骤一", "index": 1},
        {"operate_name": "步骤二", "index": 2}
    ]
    ```
    """
    try:
        with SessionLocal() as db:
            segment = db.query(Segment).filter(Segment.name == segment_name).first()
            if segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "种植环节已存在"},
                )
            segment = Segment(name=segment_name)
            for step in operate_step:
                segment.operations.append(
                    PlantOperate(name=step["operate_name"], index=step["index"])
                )
            db.add(segment)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加成功"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plant_router.post("/add_plant_plan", summary="添加种植计划")
async def add_plant_plan_api(
    plan_id: int = Body(..., description="计划ID"),
    segment_name: str = Body(..., description="种植环节名称"),
    operator: str = Body(..., description="操作人"),
    operate_date: str = Body(..., description="操作日期"),
    remark: Optional[str] = Body(None, description="备注"),
):
    """
    # 添加种植环节
    ## params
    - **segment_name**: 种植环节名称
    - operator: 操作人
    - operate_date: 操作日期
    - remark: 备注
    """
    try:
        with SessionLocal() as db:
            segment = db.query(Segment).filter(Segment.name == segment_name).first()
            if not segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "种植环节不存在"},
                )
            plan = db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "计划不存在"},
                )
            plan_segment = PlanSegmentRelationship(
                plan_id=plan_id,
                segment_id=segment.id,
                operator=operator,
                operation_date=datetime.strptime(operate_date, "%Y-%m-%d %H:%M:%S"),
                remarks=remark,
            )
            db.add(plan_segment)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加成功"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plant_router.post("/add_segment_plan_image", summary="添加种植环节图片")
async def add_segment_image_api(
    image: str = Body(..., description="图片, base64编码"),
    plan_id: int = Body(..., description="计划ID"),
    segment_id: int = Body(..., description="种植环节ID"),
):
    """
    # 添加种植环节图片
    ## params
    - **image**: 图片, base64编码
    - **plan_id**: 计划ID
    - **segment_id**: 种植环节ID
    """
    try:
        with SessionLocal() as db:
            plan_segment = (
                db.query(PlanSegmentRelationship)
                .filter(
                    PlanSegmentRelationship.plan_id == plan_id,
                    PlanSegmentRelationship.segment_id == segment_id,
                )
                .first()
            )
            if not plan_segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "种植环节不存在"},
                )
            image_name = save_image(image)
            plan_segment.image_uri = image_name
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "添加成功"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plant_router.put("/update_segment_plan_image", summary="更新种植环节图片")
async def update_segment_image_api(
    image: str = Body(..., description="图片, base64编码"),
    plan_id: int = Body(..., description="计划ID"),
    segment_id: int = Body(..., description="种植环节ID"),
):
    """
    # 更新种植环节图片
    ## params
    - **image**: 图片, base64编码
    - **plan_id**: 计划ID
    - **segment_id**: 种植环节ID
    """
    try:
        with SessionLocal() as db:
            plan_segment = (
                db.query(PlanSegmentRelationship)
                .filter(
                    PlanSegmentRelationship.plan_id == plan_id,
                    PlanSegmentRelationship.segment_id == segment_id,
                )
                .first()
            )
            if not plan_segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "种植环节不存在"},
                )
            if plan_segment.image_uri:
                delete_image(plan_segment.image_uri)
            image_name = save_image(image)
            plan_segment.image_uri = image_name
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "更新成功"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plant_router.post("/add_segment_plan_video", summary="添加种植环节视频")
async def add_segment_video_api(
    video: UploadFile = File(...),
    plan_id: int = Form(..., description="计划ID"),
    segment_id: int = Form(..., description="种植环节ID"),
):
    """
    # 添加种植环节视频
    ## params
    - **video**: 视频
    - **plan_id**: 计划ID
    - **segment_id**: 种植环节ID
    """
    with SessionLocal() as db:
        plan_segment = (
            db.query(PlanSegmentRelationship)
            .filter(
                PlanSegmentRelationship.plan_id == plan_id,
                PlanSegmentRelationship.segment_id == segment_id,
            )
            .first()
        )
        if not plan_segment:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "种植环节不存在"},
            )
        video_name = save_video(video)
        plan_segment.video_uri = video_name
        plan_segment.status = "已上传"
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "添加成功"},
        )


@plant_router.put("/update_segment_plan_video", summary="更新种植环节视频")
async def update_segment_video_api(
    video: UploadFile = File(...),
    plan_id: int = Form(..., description="计划ID"),
    segment_id: int = Form(..., description="种植环节ID"),
):
    """
    # 更新种植环节视频
    ## params
    - **video**: 视频
    - **plan_id**: 计划ID
    - **segment_id**: 种植环节ID
    """
    with SessionLocal() as db:
        plan_segment = (
            db.query(PlanSegmentRelationship)
            .filter(
                PlanSegmentRelationship.plan_id == plan_id,
                PlanSegmentRelationship.segment_id == segment_id,
            )
            .first()
        )
        if not plan_segment:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "种植环节不存在"},
            )
        if plan_segment.video_uri:
            delete_video(plan_segment.video_uri)
        video_name = save_video(video)
        plan_segment.video_uri = video_name
        plan_segment.status = "已上传"
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "更新成功"},
        )


@plant_router.put("/update_plant_segment", summary="更新种植环节")
async def update_plant_segment_api(
    segment_id: int = Body(..., description="种植环节ID"),
    segment_name: str = Body(None, description="种植环节名称"),
):
    """
    # 更新种植环节
    ## params
    - **segment_id**: 种植环节ID
    - **segment_name**: 种植环节名称
    """
    try:
        with SessionLocal() as db:
            segment = db.query(Segment).filter(Segment.id == segment_id).first()
            if not segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "种植环节不存在"},
                )
            if segment_name:
                segment.name = segment_name
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "更新成功"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plant_router.delete("/delete_plant_segment", summary="删除种植环节")
async def delete_plant_segment_api(
    segment_id: int = Query(..., description="种植环节ID"),
):
    """
    # 删除种植环节
    ## params
    - **segment_id**: 种植环节ID
    """
    try:
        with SessionLocal() as db:
            segment = db.query(Segment).filter(Segment.id == segment_id).first()
            if not segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "种植环节不存在"},
                )
            db.delete(segment)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@plant_router.delete("/delete_plant_plan", summary="删除田间种植计划")
async def delete_plant_plan_api(
    plan_id: int = Query(..., description="计划ID"),
    segment_id: int = Query(..., description="种植环节ID"),
):
    """
    # 删除田间种植计划
    ## params
    - **plan_id**: 计划ID
    - **segment_id**: 种植环节ID
    """
    try:
        with SessionLocal() as db:
            plan_segment = (
                db.query(PlanSegmentRelationship)
                .filter(
                    PlanSegmentRelationship.plan_id == plan_id,
                    PlanSegmentRelationship.segment_id == segment_id,
                )
                .first()
            )
            if not plan_segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "种植环节不存在"},
                )
            if plan_segment.image_uri:
                delete_image(plan_segment.image_uri)
            if plan_segment.video_uri:
                delete_video(plan_segment.video_uri)
            db.delete(plan_segment)
            db.commit()
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 0, "message": "删除成功"},
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
