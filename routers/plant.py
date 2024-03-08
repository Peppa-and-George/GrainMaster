import json
from datetime import datetime
from typing import Literal, Optional, List, Dict, Union

from fastapi import (
    APIRouter,
    Query,
    status,
    Body,
    File,
    UploadFile,
    Form,
)
from fastapi.responses import JSONResponse

from dependency.videos import save_video, delete_video
from schema.tables import (
    Segment,
    PlantOperate,
    PlantPlan,
    Plan,
    Location,
    Client,
    Order,
    SegmentFile,
)
from schema.common import (
    page_with_order,
    query_with_order,
    query_with_page,
    transform_schema,
)
from schema.database import SessionLocal
from dependency.image import save_upload_image, delete_image
from routers.message import add_message
from models.base import (
    PlantPlanSchema,
    PlantPlanBaseSchema,
    SegmentSchema,
    SegmentFileSchema,
)

plant_router = APIRouter()


@plant_router.get("/get_plant_plan", summary="获取种植计划")
async def get_plant_plan(
    plan_id: Optional[int] = Query(None, title="计划id"),
    year: Optional[int] = Query(None, title="年份"),
    batch: Optional[int] = Query(None, title="批次"),
    location: Union[str, int, None] = Query(None, title="地点"),
    location_field_type: Literal["id", "name"] = Query("id", title="地点字段类型"),
    page: int = Query(1, title="页数"),
    page_size: int = Query(10, title="每页数量"),
    order_by: str = Query("id", title="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", title="排序方式"),
):
    """
    # 获取种植计划
    - **plan_id**: 计划id, int, required
    - **year**: 年份, int, optional
    - **batch**: 批次, int, optional
    - **location**: 基地标识, string, optional
    - **location_field_type**: 基地字段类型, string, default: id，可选值：id, name
    - **page**: 页数, int, default: 1
    - **page_size**: 每页数量, int, default: 10
    - **order_by**: 排序字段, string, default: id
    - **order**: 排序方式, string, default: desc
    """
    with SessionLocal() as db:
        query = db.query(PlantPlan).join(Plan, PlantPlan.plan_id == Plan.id)
        if plan_id:
            query = query.filter(PlantPlan.plan_id == plan_id)
        if year:
            query = query.filter(Plan.year == year)
        if batch:
            query = query.filter(Plan.batch == batch)
        if location:
            if location_field_type == "id":
                query = query.filter(Plan.location_id == location)
            else:
                query = query.join(Location, Plan.location_id == Location.id).filter(
                    Location.name == location
                )
        response = page_with_order(
            PlantPlanSchema,
            query,
            page,
            page_size,
            order_by,
            order,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "查询成功", "data": response},
        )


@plant_router.get("/get_segment", summary="获取种植环节")
async def get_segment(
    segment: Union[int, str] = Query(None, title="环节标识"),
    segment_field_type: Literal["id", "name"] = Query("id", title="环节字段类型"),
    page: int = Query(1, title="页数"),
    page_size: int = Query(10, title="每页数量"),
    order_by: str = Query("id", title="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", title="排序方式"),
):
    """
    # 获取种植环节
    - **segment**: 种植环节标识, 可选
    - **segment_field_type**: 种植环节字段类型, string, default: id, 可选值：id, name
    - **page**: 页数, int, default: 1
    - **page_size**: 每页数量, int, default: 10
    - **order_by**: 排序字段, string, default: id
    - **order**: 排序方式, string, default: desc
    """
    with SessionLocal() as db:
        query = db.query(Segment).join(
            PlantOperate, Segment.id == PlantOperate.segment_id
        )
        if segment:
            if segment_field_type == "id":
                query = query.filter(Segment.id == segment)
            else:
                query = query.filter(Segment.name == segment)
        total = query.count()
        query = query_with_order(query, order_by, order)
        query = query_with_page(query, page, page_size)
        objs = query.all()
        data = []
        for obj in objs:
            segment_data = {"name": obj.name, "segment_id": obj.id, "operations": []}
            for operate in obj.operations:
                segment_data["operations"].append(
                    {
                        "operate_name": operate.name,
                        "index": operate.index,
                        "operate_id": operate.id,
                    }
                )
            data.append(segment_data)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "查询成功",
                "data": data,
                "total": total,
                "total_page": (total + page_size - 1) // page_size,
                "order_by": order_by,
                "order": order,
                "page": page,
                "page_size": page_size,
            },
        )


@plant_router.get("/get_segment_file", summary="获取种植环节文件")
async def get_segment_file(
    segment: Union[int, str, None] = Query(None, title="环节标识"),
    segment_field_type: Literal["id", "name"] = Query("id", title="环节字段类型"),
    file_type: Literal["image", "video", "all"] = Query("all", title="文件类型"),
    page: int = Query(1, title="页数"),
    page_size: int = Query(10, title="每页数量"),
    order_by: str = Query("id", title="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", title="排序方式"),
):
    """
    # 获取种植环节文件
    - **segment**: 种植环节标识, 可选
    - **file_type**: 文件类型, string, optional, 可选值：image, video, all
    - **page**: 页数, int, default: 1
    - **page_size**: 每页数量, int, default: 10
    - **order_by**: 排序字段, string, default: id
    - **order**: 排序方式, string, default: desc
    """
    with SessionLocal() as db:
        query = db.query(SegmentFile)
        if segment:
            if segment_field_type == "id":
                query = query.filter(SegmentFile.segment_id == segment)
            else:
                query = query.join(
                    Segment, SegmentFile.segment_id == Segment.id
                ).filter(Segment.name == segment)
        if file_type != "all":
            query = query.filter(SegmentFile.type == file_type)
        response = page_with_order(
            SegmentFileSchema, query, page, page_size, order_by, order
        )
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)


@plant_router.post("/add_plant_plan", summary="添加种植计划")
async def add_plant_plan(
    plan_id: int = Body(..., title="计划id"),
    segment_id: int = Body(..., title="种植环节id"),
    operator_id: int = Body(..., title="操作人id"),
    operate_time: str = Body(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        title="操作时间",
        examples=["2021-01-01 12:00:00"],
    ),
    remark: Optional[str] = Body(None, title="备注"),
    notify: Optional[bool] = Body(False, title="是否通知客户"),
):
    """
    # 添加种植计划
    - **plan_id**: 计划id, int, required
    - **segment_id**: 种植环节id, int, required
    - **operator_id**: 操作人id, int, required
    - **operate_time**: 操作时间, string, required, default: 当前时间
    - **remark**: 备注, string, optional
    - **notify**: 是否通知客户, bool, optional, default: False
    """
    with SessionLocal() as db:
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"code": 1, "message": "计划不存在"}
            )

        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "种植环节不存在"},
            )

        operator = db.query(Client).filter(Client.id == operator_id).first()
        if not operator:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "操作人不存在"},
            )

        plant_plan = PlantPlan(
            operation_date=datetime.strptime(operate_time, "%Y-%m-%d %H:%M:%S"),
            remarks=remark,
        )
        plant_plan.plan = plan
        plant_plan.segment = segment
        plant_plan.operator = operator
        db.add(plant_plan)
        db.commit()

        if notify:
            # 添加消息
            orders = (
                db.query(Order.client_id)
                .filter(Order.plan_id == plan_id)
                .group_by(Order.client_id)
                .all()
            )

            for order in orders:
                add_message(
                    title="添加种植计划",
                    content=f"{operator.name}添加了一个种植计划，操作时间：{operate_time}，备注：{remark}，环节：{segment.name}",
                    receiver_id=order[0],
                    sender="系统",
                    message_type="添加种植计划",
                    details=json.dumps(transform_schema(PlantPlanSchema, plant_plan)),
                    tag=1,
                )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "添加成功"},
        )


@plant_router.post("/add_plant_segment", summary="添加种植环节")
async def add_segment(
    name: str = Body(..., title="环节名称"),
    operate_steps: Optional[List[Dict]] = Body(
        None,
        title="环节描述",
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
    - **name**: 环节名称, string, required
    - **operate_steps**: 种植环节操作, list, optional
    """
    with SessionLocal() as db:
        old_segment = db.query(Segment).filter_by(name=name).first()
        if old_segment:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": f"种植环节：{name}已存在"},
            )

        segment = Segment(name=name)
        if operate_steps:
            for step in operate_steps:
                operate = PlantOperate(name=step["operate_name"], index=step["index"])
                segment.operations.append(operate)
        db.add(segment)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 0, "message": "添加成功"}
        )


@plant_router.put("/update_segment", summary="更新种植环节")
async def update_segment(
    segment_id: int = Body(..., title="环节id"),
    name: Optional[str] = Body(None, title="环节名称"),
    operate_steps: Optional[List[Dict]] = Body(
        None,
        title="环节描述",
        examples=[
            [
                {"operate_name": "步骤一", "index": 1},
                {"operate_name": "步骤二", "index": 2},
            ]
        ],
    ),
    notify: Optional[bool] = Body(False, title="是否通知客户"),
):
    """
    # 更新种植环节
    - **segment_id**: 环节id, int, required
    - **name**: 环节名称, string, optional
    - **operate_steps**: 种植环节操作, list, optional
    - **notify**: 是否通知客户, bool, optional, default: False
    """
    with SessionLocal() as db:
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "环节不存在"},
            )

        if name:
            segment.name = name

        if operate_steps:
            # 删除原有操作
            for operate in segment.operations:
                db.delete(operate)
            for step in operate_steps:
                operate = PlantOperate(name=step["operate_name"], index=step["index"])
                segment.operations.append(operate)
        db.commit()

        if notify:
            # 添加消息
            orders = (
                db.query(Order.client_id)
                .join(Plan, Order.plan_id == Plan.id)
                .join(PlantPlan, Plan.id == PlantPlan.plan_id)
                .filter(PlantPlan.segment_id == segment_id)
                .group_by(Order.client_id)
                .all()
            )

            for order in orders:
                add_message(
                    title="更新种植环节",
                    content=f"种植环节：{segment.name}更新成功",
                    receiver_id=order[0],
                    sender="系统",
                    message_type="更新种植环节",
                    details=json.dumps(transform_schema(SegmentSchema, segment)),
                    tag=1,
                )

        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 0, "message": "更新成功"}
        )


@plant_router.put("/update_plant_plan", summary="更新种植计划")
async def update_plant_plan(
    plant_plan_id: int = Body(..., title="种植计划id"),
    plan_id: Optional[int] = Body(None, title="计划id"),
    segment_id: Optional[int] = Body(None, title="种植环节id"),
    operator_id: Optional[int] = Body(None, title="操作人id"),
    operate_time: Optional[str] = Body(
        None,
        title="操作时间",
        examples=["2021-01-01 12:00:00"],
    ),
    remark: Optional[str] = Body(None, title="备注"),
    notify: Optional[bool] = Body(False, title="是否通知客户"),
):
    """
    # 更新种植计划
    - **plant_plan_id**: 种植计划id, int, required
    - **plan_id**: 计划id, int, optional
    - **segment_id**: 种植环节id, int, optional
    - **operator_id**: 操作人id, int, optional
    - **operate_time**: 操作时间, string, optional
    - **remark**: 备注, string, optional
    - **notify**: 是否通知客户, bool, optional, default: False
    """
    with SessionLocal() as db:
        plant_plan = db.query(PlantPlan).filter(PlantPlan.id == plant_plan_id).first()
        if not plant_plan:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "种植计划不存在"},
            )

        if plan_id:
            plan = db.query(Plan).filter(Plan.id == plan_id).first()
            if not plan:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "计划不存在"},
                )
            plant_plan.plan = plan

        if segment_id:
            segment = db.query(Segment).filter(Segment.id == segment_id).first()
            if not segment:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "种植环节不存在"},
                )
            plant_plan.segment = segment

        if operator_id:
            operator = db.query(Client).filter(Client.id == operator_id).first()
            if not operator:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "操作人不存在"},
                )
            plant_plan.operator = operator

        if operate_time:
            plant_plan.operation_date = datetime.strptime(
                operate_time, "%Y-%m-%d %H:%M:%S"
            )

        if remark:
            plant_plan.remarks = remark
        db.commit()

        if notify:
            # 添加消息
            orders = (
                db.query(Order.client_id)
                .filter(Order.plan_id == plant_plan.plan_id)
                .group_by(Order.client_id)
                .all()
            )

            for order in orders:
                add_message(
                    title="更新种植计划",
                    content=f"种植计划更新成功",
                    receiver_id=order[0],
                    sender="系统",
                    message_type="更新种植计划",
                    details=json.dumps(transform_schema(PlantPlanSchema, plant_plan)),
                    tag=1,
                )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 0, "message": "更新成功"}
        )


@plant_router.delete("/delete_segment", summary="删除种植环节")
async def delete_segment(
    segment_id: int = Body(..., title="环节id"),
    notify: Optional[bool] = Body(False, title="是否通知客户"),
):
    """
    # 删除种植环节
    - **segment_id**: 环节id, int, required
    - **notify**: 是否通知客户, bool, optional, default: False
    """
    with SessionLocal() as db:
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "环节不存在"},
            )
        if notify:
            # 添加消息
            orders = (
                db.query(Order.client_id)
                .join(Plan, Order.plan_id == Plan.id)
                .join(PlantPlan, Plan.id == PlantPlan.plan_id)
                .filter(PlantPlan.segment_id == segment_id)
                .group_by(Order.client_id)
                .all()
            )

            for order in orders:
                add_message(
                    title="删除种植环节",
                    content=f"种植环节：{segment.name}删除成功",
                    receiver_id=order[0],
                    sender="系统",
                    message_type="删除种植环节",
                    details=json.dumps(transform_schema(SegmentSchema, segment)),
                    tag=1,
                )

        db.delete(segment)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 0, "message": "删除成功"}
        )


@plant_router.delete("/delete_plant_plan", summary="删除种植计划")
async def delete_plant_plan(
    plant_plan_id: int = Body(..., title="种植计划id"),
    notify: Optional[bool] = Body(False, title="是否通知客户"),
):
    """
    # 删除种植计划
    - **plant_plan_id**: 种植计划id, int, required
    - **notify**: 是否通知客户, bool, optional, default: False
    """
    with SessionLocal() as db:
        plant_plan = db.query(PlantPlan).filter(PlantPlan.id == plant_plan_id).first()
        if not plant_plan:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "种植计划不存在"},
            )
        if notify:
            # 添加消息
            orders = (
                db.query(Order.client_id)
                .filter(Order.plan_id == plant_plan.plan_id)
                .group_by(Order.client_id)
                .all()
            )

            for order in orders:
                add_message(
                    title="删除种植计划",
                    content=f"种植计划删除成功",
                    receiver_id=order[0],
                    sender="系统",
                    message_type="删除种植计划",
                    details=json.dumps(transform_schema(PlantPlanSchema, plant_plan)),
                    tag=1,
                )

        db.delete(plant_plan)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 0, "message": "删除成功"}
        )


@plant_router.post("/upload_file", summary="上传文件")
async def upload_file(
    segment_id: int = Form(..., title="种植环节id"),
    file: UploadFile = File(..., title="图片文件"),
    file_type: Literal["image", "video"] = Form("image", title="文件类型"),
    filename: Optional[str] = Form(None, title="文件名"),
    notify: Optional[bool] = Form(False, title="是否通知客户"),
):
    """
    # 上传文件
    - **segment_id**: 种植环节id, int, required
    - **file**: 图片文件, file, required
    - **file_type**: 文件类型, string, optional, default: image, 可选值：image, video
    - **filename**: 文件名, string, optional
    - **notify**: 是否通知客户, bool, optional, default: False
    """
    with SessionLocal() as db:
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "环节不存在"},
            )
        if not filename:
            name = file.filename
        else:
            name = filename

        if file_type == "image":
            filename = save_upload_image(file)
        else:
            filename = save_video(file)

        segment_file = SegmentFile(
            name=name,
            filename=filename,
            type=file_type,
        )
        segment_file.segment = segment
        db.add(segment_file)
        db.commit()
        if notify:
            # 添加消息
            orders = (
                db.query(Order.client_id)
                .join(Plan, Order.plan_id == Plan.id)
                .join(PlantPlan, Plan.id == PlantPlan.plan_id)
                .filter(PlantPlan.segment_id == segment_id)
                .group_by(Order.client_id)
                .all()
            )

            for order in orders:
                add_message(
                    title="上传文件",
                    content=f"种植环节：{segment.name}更新了一个文件，文件名：{name}，文件类型：{file_type}",
                    receiver_id=order[0],
                    sender="系统",
                    message_type="种植环节上传文件",
                    details=json.dumps(
                        transform_schema(SegmentFileSchema, segment_file)
                    ),
                    tag=1,
                )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "上传成功",
                "data": [
                    {
                        "filename": filename,
                        "original_filename": name,
                    }
                ],
            },
        )


@plant_router.delete("/delete_file", summary="删除文件")
async def delete_file(
    file_id: int = Body(..., title="文件id"),
    notify: Optional[bool] = Body(False, title="是否通知客户"),
):
    """
    # 删除文件
    - **file_id**: 文件id, int, required
    - **notify**: 是否通知客户, bool, optional, default: False
    """
    with SessionLocal() as db:
        segment_file = db.query(SegmentFile).filter(SegmentFile.id == file_id).first()
        if not segment_file:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "文件不存在"},
            )
        if notify:
            # 添加消息
            orders = (
                db.query(Order.client_id)
                .join(Plan, Order.plan_id == Plan.id)
                .join(PlantPlan, Plan.id == PlantPlan.plan_id)
                .filter(PlantPlan.segment_id == segment_file.segment_id)
                .group_by(Order.client_id)
                .all()
            )

            for order in orders:
                add_message(
                    title="删除文件",
                    content=f"种植环节：{segment_file.segment.name}删除了一个文件，文件名：{segment_file.name}，文件类型：{segment_file.type}",
                    receiver_id=order[0],
                    sender="系统",
                    message_type="种植环节删除文件",
                    details=json.dumps(
                        transform_schema(SegmentFileSchema, segment_file)
                    ),
                    tag=1,
                )
        if segment_file.type == "image":
            delete_image(segment_file.filename)
        else:
            delete_video(segment_file.filename)
        db.delete(segment_file)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 0, "message": "删除成功"}
        )
