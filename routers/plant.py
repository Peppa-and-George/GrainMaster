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
    Plan,
    Location,
    Client,
    Order,
    SegmentPlan,
    OperationImplementationInformation,
)
from schema.common import (
    page_with_order,
    transform_schema,
)
from schema.database import SessionLocal
from dependency.image import save_upload_image, delete_image
from routers.message import add_message
from models.base import (
    SegmentSchema,
    SegmentPlanSchema,
    OperationImplementBaseSchema,
)

plant_router = APIRouter()


@plant_router.get("/get_operation_implementation", summary="获取操作步骤实施信息")
async def get_operation_implementation(
    implementation_id: Optional[int] = Query(None, title="操作步骤id"),
    segment_plan_id: Optional[int] = Query(None, title="种植环节计划id"),
    operation: Union[int, str] = Query(None, title="操作标识"),
    operation_field_type: Literal["id", "name"] = Query("id", title="操作字段类型"),
    page: int = Query(1, title="页数"),
    page_size: int = Query(10, title="每页数量"),
    order_by: str = Query("id", title="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", title="排序方式"),
):
    """
    # 获取操作步骤信息
    - **implementation_id**: 操作步骤id, int, optional
    - **segment_plan_id**: 种植环节计划id, int, optional
    - **operation**: 操作标识, 可选
    - **operation_field_type**: 操作字段类型, string, default: id, 可选值：id, name
    - **page**: 页数, int, default: 1
    - **page_size**: 每页数量, int, default: 10
    - **order_by**: 排序字段, string, default: id
    - **order**: 排序方式, string, default: desc
    """
    with SessionLocal() as db:
        query = (
            db.query(OperationImplementationInformation)
            .join(
                SegmentPlan,
                OperationImplementationInformation.segment_plan_id == SegmentPlan.id,
            )
            .join(
                PlantOperate,
                OperationImplementationInformation.operation_id == PlantOperate.id,
            )
        )
        if implementation_id:
            query = query.filter(
                OperationImplementationInformation.id == implementation_id
            )
        if segment_plan_id:
            query = query.filter(SegmentPlan.id == segment_plan_id)
        if operation:
            if operation_field_type == "id":
                query = query.filter(PlantOperate.id == operation)
            else:
                query = query.filter(PlantOperate.name == operation)
        response = page_with_order(
            schema=OperationImplementBaseSchema,
            query=query,
            page_size=page_size,
            page=page,
            order_field=order_by,
            order=order,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )


@plant_router.get("/get_segment_plan", summary="获取种植环节计划")
async def get_segment_plan(
    segment_plan_id: Optional[int] = Query(None, title="种植环节计划id"),
    plan_id: Optional[int] = Query(None, title="计划id"),
    segment: Union[int, str] = Query(None, title="种植环节标识"),
    segment_field_type: Literal["id", "name"] = Query("id", title="种植环节字段类型"),
    year: Optional[int] = Query(None, title="年份"),
    batch: Optional[int] = Query(None, title="批次"),
    location: Optional[str] = Query(None, title="地点"),
    location_field_type: Literal["id", "name"] = Query("id", title="地点字段类型"),
    page: int = Query(1, title="页数"),
    page_size: int = Query(10, title="每页数量"),
    order_by: str = Query("id", title="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", title="排序方式"),
):
    """
    # 获取种植环节计划
    - **segment_plan_id**: 种植环节计划id, int, optional
    - **plan_id**: 计划id, int, optional
    - **segment**: 种植环节标识, 可选
    - **segment_field_type**: 种植环节字段类型, string, default: id, 可选值：id, name
    - **year**: 年份, int, optional
    - **batch**: 批次, int, optional
    - **location**: 地点, string, optional
    - **location_field_type**: 地点字段类型, string, default: id, 可选值：id, name
    - **page**: 页数, int, default: 1
    - **page_size**: 每页数量, int, default: 10
    - **order_by**: 排序字段, string, default: id
    - **order**: 排序方式, string, default: desc
    """
    with SessionLocal() as db:
        query = (
            db.query(SegmentPlan)
            .join(Plan, SegmentPlan.plan_id == Plan.id)
            .outerjoin(Segment, SegmentPlan.segment_id == Segment.id)
            .outerjoin(Location, Plan.location_id == Location.id)
        )
        if segment_plan_id:
            query = query.filter(SegmentPlan.id == segment_plan_id)
        if plan_id:
            query = query.filter(SegmentPlan.plan_id == plan_id)
        if segment:
            if segment_field_type == "id":
                query = query.filter(SegmentPlan.segment_id == segment)
            else:
                query = query.filter(Segment.name == segment)
        if year:
            query = query.filter(Plan.year == year)
        if batch:
            query = query.filter(Plan.batch == batch)
        if location:
            if location_field_type == "id":
                query = query.filter(Plan.location_id == location)
            else:
                query = query.filter(Location.name == location)
        response = page_with_order(
            schema=SegmentPlanSchema,
            query=query,
            page_size=page_size,
            page=page,
            order_field=order_by,
            order=order,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
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
        query = db.query(Segment)
        if segment:
            if segment_field_type == "id":
                query = query.filter(Segment.id == segment)
            else:
                query = query.filter(Segment.name == segment)
        response = page_with_order(
            schema=SegmentSchema,
            query=query,
            page_size=page_size,
            page=page,
            order_field=order_by,
            order=order,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )


@plant_router.post("/add_segment_plan", summary="添加种植环节计划")
async def add_segment_plan(
    plan_id: int = Body(..., title="计划id"),
    segment: int = Body(..., title="种植环节标识"),
    segment_field_type: Literal["id", "name"] = Body("id", title="种植环节字段类型"),
    operator: Union[int, str] = Body(..., title="操作人标识"),
    operator_field_type: Literal["id", "name", "phone_number"] = Body(
        "id", title="操作人字段类型"
    ),
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
    - **segment**: 种植环节标识, int, required
    - **segment_field_type**: 种植环节字段类型, string, default: id, 可选值：id, name
    - **operator**: 操作人标识, string | int, required
    - **operator_field_type**: 操作人字段类型, string, default: id, 可选值：id(int), name(string), phone_number(string)
    - **operate_time**: 操作时间, string, required, default: 当前时间
    - **remark**: 备注, string, optional
    - **notify**: 是否通知客户, bool, optional, default: False
    """
    with SessionLocal() as db:
        # 验证是否存在该年度的种植计划
        old_plant_plan = (
            db.query(SegmentPlan)
            .filter(SegmentPlan.plan_id == plan_id, SegmentPlan.segment_id == segment)
            .first()
        )
        if old_plant_plan:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "种植计划已存在，不可重复添加"},
            )

        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"code": 1, "message": "计划不存在"}
            )
        if segment_field_type == "id":
            segment = db.query(Segment).filter(Segment.id == segment).first()
        else:
            segment = db.query(Segment).filter(Segment.name == segment).first()
        if not segment:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "种植环节不存在"},
            )

        if operator_field_type == "id":
            operator = db.query(Client).filter(Client.id == operator).first()
        elif operator_field_type == "name":
            operator = db.query(Client).filter(Client.name == operator).first()
        else:
            operator = db.query(Client).filter(Client.phone_number == operator).first()
        if not operator:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "未查询到操作人"},
            )

        segment_plan = SegmentPlan(
            operate_time=datetime.strptime(operate_time, "%Y-%m-%d %H:%M:%S"),
            remarks=remark,
            status="未开始",
        )
        segment_plan.plan = plan
        segment_plan.segment = segment
        segment_plan.operator = operator

        # 添加实施步骤
        for operation in segment.operations:
            implementation = OperationImplementationInformation(
                status="未开始",
            )
            implementation.segment_plan = segment_plan
            implementation.operation = operation
            segment_plan.implementations.append(implementation)

        db.add(segment_plan)
        db.flush()
        db.refresh(segment_plan)
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
                    details=json.dumps(
                        transform_schema(SegmentPlanSchema, segment_plan)
                    ),
                    tag=1,
                )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "添加成功",
                "data": transform_schema(SegmentPlanSchema, segment_plan),
            },
        )


@plant_router.post("/add_segment", summary="添加种植环节")
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

        segment = Segment(name=name, status="未开始")
        if operate_steps:
            for step in operate_steps:
                operate = PlantOperate(
                    name=step["operate_name"], index=step.get("index", 0)
                )
                segment.operations.append(operate)
        db.add(segment)
        db.flush()
        db.refresh(segment)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "添加成功",
                "data": transform_schema(SegmentSchema, segment),
            },
        )


@plant_router.post("/upload_file", summary="上传文件")
async def upload_file(
    segment_plan_id: int = Form(..., description="种植环节计划id"),
    operate: Union[int, str] = Form(..., description="操作标识"),
    operate_field_type: Literal["id", "name"] = Form("id", description="操作字段类型"),
    image: Optional[UploadFile] = File(
        None,
        description="图片文件",
    ),
    video: Optional[UploadFile] = File(None, description="视频文件"),
    operator_name: Optional[str] = Form(None, description="操作人名称"),
    operate_time: str = Form(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        description="操作时间",
        examples=["2021-01-01 12:00:00"],
    ),
    operate_status: Literal["未开始", "进行中", "已完成"] = Form("已完成", description="变更状态"),
    remarks: Optional[str] = Form(None, description="备注"),
    notify: bool = Form(False, description="是否通知客户"),
):
    """
    # 上传操作文件
    - **segment_plan_id**: 种植环节计划id, int, required
    - **operate**: 操作步骤标识, string | int, required
    - **operate_field_type**: 操作字段类型, string, default: id, 可选值：id, name
    - **image**: 图片文件, file, required
    - **video**: 视频文件, file, required
    - **operator_name**: 操作人名称, string, optional
    - **operate_status**: 变更状态, string, default: 未开始, 可选值：未开始, 进行中, 已完成
    - **operate_time**: 操作时间, string, required, default: 当前时间
    - **remarks**: 备注, string, optional
    - **notify**: 是否通知客户, bool, optional, default: False
    """
    with SessionLocal() as db:
        query = (
            db.query(OperationImplementationInformation)
            .join(
                SegmentPlan,
                OperationImplementationInformation.segment_plan_id == SegmentPlan.id,
            )
            .join(
                PlantOperate,
                OperationImplementationInformation.operation_id == PlantOperate.id,
            )
            .filter(SegmentPlan.id == segment_plan_id)
        )

        if operate_field_type == "id":
            query = query.filter(
                OperationImplementationInformation.operation_id == operate
            )
        else:
            query = query.filter(PlantOperate.name == operate)

        implementation = query.first()
        if not implementation:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "未查询到操作实施步骤"},
            )
        if image:
            if implementation.image_filename:
                delete_image(implementation.image_filename)
            implementation.image_filename = save_upload_image(image)
        if video:
            if implementation.video_filename:
                delete_video(implementation.video_filename)
            implementation.video_filename = save_video(video)

        implementation.operator = operator_name
        implementation.operate_time = datetime.strptime(
            operate_time, "%Y-%m-%d %H:%M:%S"
        )
        implementation.status = operate_status
        implementation.remarks = remarks

        implementation.segment_plan.status = "进行中"

        db.flush()
        db.refresh(implementation)
        db.commit()

        if notify:
            # 添加消息
            orders = (
                db.query(Order.client_id)
                .join(Plan, Plan.id == Order.plan_id)
                .filter(Plan.id == implementation.segment_plan.plan_id)
                .group_by(Order.client_id)
                .all()
            )

            for order in orders:
                add_message(
                    title="田间种植操作视频上传",
                    content=f"{operator_name}上传了一个操作视频，操作时间：{operate_time}，备注：{remarks}，环节：{implementation.segment_plan.segment.name}，操作：{implementation.operation.name}",
                    receiver_id=order[0],
                    sender="系统",
                    message_type="操作视频上传",
                    details=json.dumps(
                        transform_schema(OperationImplementBaseSchema, implementation)
                    ),
                    tag=1,
                )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "上传成功"},
        )


@plant_router.put("/update_segment_plan", summary="更新种植环节计划")
async def update_segment_plan(
    segment_plan_id: int = Body(..., description="种植环节计划id"),
    operator: Union[int, str] = Body(None, description="操作人标识"),
    operator_field_type: Literal["id", "name", "phone_number"] = Body(
        "id", description="操作人字段类型"
    ),
    operate_time: Optional[str] = Body(
        None, description="操作时间", examples=["2021-01-01 12:00:00"]
    ),
    remarks: Optional[str] = Body(None, description="备注"),
    plan_status: Optional[Literal["未开始", "进行中", "已完成"]] = Body(None, description="状态"),
    notify: bool = Body(False, description="是否通知客户"),
):
    """
    # 更新种植环节计划
    - **segment_plan_id**: 种植环节计划id, int, required
    - **operate_time**: 操作时间, string, optional
    - **remarks**: 备注, string, optional
    - **plan_status**: 状态, string, optional
    - **notify**: 是否通知客户, bool, optional, default: False
    """
    with SessionLocal() as db:
        segment_plan = (
            db.query(SegmentPlan).filter(SegmentPlan.id == segment_plan_id).first()
        )
        if not segment_plan:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "未查询到种植环节计划"},
            )

        if operate_time:
            segment_plan.operate_time = datetime.strptime(
                operate_time, "%Y-%m-%d %H:%M:%S"
            )
        if remarks:
            segment_plan.remarks = remarks
        if status:
            segment_plan.status = plan_status
        if operator:
            if operator_field_type == "id":
                operator = db.query(Client).filter(Client.id == operator).first()
            elif operator_field_type == "name":
                operator = db.query(Client).filter(Client.name == operator).first()
            else:
                operator = (
                    db.query(Client).filter(Client.phone_number == operator).first()
                )
            if not operator:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={"code": 1, "message": "未查询到操作人"},
                )
            segment_plan.operator = operator

        db.commit()

        if notify:
            # 添加消息
            orders = (
                db.query(Order.client_id)
                .join(Plan, Plan.id == Order.plan_id)
                .filter(Plan.id == segment_plan.plan_id)
                .group_by(Order.client_id)
                .all()
            )

            for order in orders:
                add_message(
                    title="更新种植环节计划",
                    content=f"种植环节计划：{segment_plan.segment.name}已被更新",
                    receiver_id=order[0],
                    sender="系统",
                    message_type="更新种植环节计划",
                    details=json.dumps(
                        transform_schema(SegmentPlanSchema, segment_plan)
                    ),
                    tag=1,
                )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "更新成功",
                "data": transform_schema(SegmentPlanSchema, segment_plan),
            },
        )


@plant_router.put("/update_segment", summary="更新种植环节")
async def update_segment(
    segment: Union[int, str] = Body(..., description="种植环节标识"),
    segment_field_type: Literal["id", "name"] = Body("id", description="种植环节字段类型"),
    name: Optional[str] = Body(None, description="环节名称"),
    notify: bool = Body(False, description="是否通知客户"),
):
    """
    # 更新种植环节
    - **segment**: 种植环节标识, string | int, required
    - **segment_field_type**: 种植环节字段类型, string, default: id, 可选值：id, name
    - **name**: 环节名称, string, optional
    """
    with SessionLocal() as db:
        if segment_field_type == "id":
            segment = db.query(Segment).filter(Segment.id == segment).first()
        else:
            segment = db.query(Segment).filter(Segment.name == segment).first()
        if not segment:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "未查询到种植环节"},
            )

        if name:
            segment.name = name

        db.commit()

        if notify:
            # 添加消息
            orders = (
                db.query(Order.client_id)
                .join(Plan, Plan.id == Order.plan_id)
                .join(SegmentPlan, Plan.id == SegmentPlan.plan_id)
                .join(Segment, SegmentPlan.segment_id == Segment.id)
                .filter(Segment.id == segment.id)
                .group_by(Order.client_id)
                .all()
            )

            for order in orders:
                add_message(
                    title="更新种植环节",
                    content=f"种植环节：{segment.name}已被更新",
                    receiver_id=order[0],
                    sender="系统",
                    message_type="更新种植环节",
                    details=json.dumps(transform_schema(SegmentSchema, segment)),
                    tag=1,
                )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "更新成功",
                "data": transform_schema(SegmentSchema, segment),
            },
        )


@plant_router.delete("/delete_segment", summary="删除种植环节")
async def delete_operation_video(
    segment: Union[int, str] = Form(..., description="种植环节标识"),
    segment_field_type: Literal["id", "name"] = Form("id", description="种植环节字段类型"),
):
    """
    # 删除种植环节
    - **segment**: 种植环节标识, string | int, required
    - **segment_field_type**: 种植环节字段类型, string, default: id, 可选值：id, name
    """
    with SessionLocal() as db:
        if segment_field_type == "id":
            segment = db.query(Segment).filter(Segment.id == segment).first()
        else:
            segment = db.query(Segment).filter(Segment.name == segment).first()
        if not segment:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "未查询到种植环节"},
            )
        if segment.plant_segment_plans:
            names = [plan.segment.name for plan in segment.plant_segment_plans]
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 1,
                    "message": f"种植计划: [{','.join(names)}]引用了该种植环节，不可删除",
                },
            )

        db.delete(segment)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "删除成功"},
        )


@plant_router.delete("/delete_segment_plan", summary="删除种植环节计划")
async def delete_segment_plan(
    segment_plan_id: int = Query(..., title="种植环节计划id"),
    notify: bool = Query(False, title="是否通知客户"),
):
    """
    # 删除种植环节计划
    - **segment_plan_id**: 种植环节计划id, int, required
    - **notify**: 是否通知客户, bool, optional, default: False
    """
    with SessionLocal() as db:
        segment_plan = (
            db.query(SegmentPlan).filter(SegmentPlan.id == segment_plan_id).first()
        )
        if not segment_plan:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "未查询到种植环节计划"},
            )
        for implementation in segment_plan.implementations:
            if implementation.image_filename:
                delete_image(implementation.image_filename)
            if implementation.video_filename:
                delete_video(implementation.video_filename)
            db.delete(implementation)

        if notify:
            # 添加消息
            orders = (
                db.query(Order.client_id)
                .join(Plan, Plan.id == Order.plan_id)
                .filter(Plan.id == segment_plan.plan_id)
                .group_by(Order.client_id)
                .all()
            )

            for order in orders:
                add_message(
                    title="删除种植环节计划",
                    content=f"种植环节计划：{segment_plan.segment.name}已被删除",
                    receiver_id=order[0],
                    sender="系统",
                    message_type="删除种植环节计划",
                    details=json.dumps(
                        transform_schema(SegmentPlanSchema, segment_plan)
                    ),
                    tag=1,
                )

        db.delete(segment_plan)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "删除成功"},
        )
