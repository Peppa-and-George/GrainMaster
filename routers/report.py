from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Query, status, Body, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse

from dependency.report import save_report, delete_report
from schema.common import page_with_order
from schema.database import SessionLocal
from schema.tables import Quality, Plan, Location, Warehouse
from models.base import QualitySchema
from auth import get_user_by_request

report_router = APIRouter()


@report_router.get("/filter_report", summary="筛选质报告")
async def filter_quality_api(
    year: Optional[int] = Query(None, description="年份"),
    batch: Optional[int] = Query(None, description="批次"),
    location_name: Optional[str] = Query(None, description="位置"),
    report_status: Optional[str] = Query(
        None, description="报告上传状态", examples=["已上传", "未上传"]
    ),
    report_type: Optional[Literal["仓储加工", "原料运输"]] = Query(
        None, description="报告类型", examples=["仓储加工", "原料运输"]
    ),
    order_field: str = Query("id", description="排序字段"),
    order_desc: Literal["asc", "desc"] = Query("asc", description="是否降序"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    """
    # 筛选质报告
    - **year**: 年份, 可选
    - **batch**: 批次, 可选
    - **location_name**: 位置, 可选
    - **report_status**: 报告上传状态, 可选, 一般设置为"已上传"和"为上传"
    - **report_type**: 报告类型, 可选, 一般设置为"仓储加工"和"原料运输"
    - **order_field**: 排序字段, 默认为id
    - **order_desc**: 是否降序, 默认为asc
    - **page**: 页码, 默认为1
    - **page_size**: 每页数量, 默认为10
    """
    with SessionLocal() as db:
        query = db.query(Quality).join(Plan, Plan.id == Quality.plan_id)
        if year:
            query = query.filter(Plan.year == year)
        if batch:
            query = query.filter(Plan.batch == batch)
        if location_name:
            location = db.query(Location).filter(Location.name == location_name).first()
            query = query.filter(Plan.location_id == location.id)
        if report_status:
            query = query.filter(Quality.report_status == report_status)
        if report_type:
            query = query.filter(Quality.type == report_type)

        response = page_with_order(
            schema=QualitySchema,
            query=query,
            order_field=order_field,
            order=order_desc,
            page=page,
            page_size=page_size,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )


@report_router.post(
    "/create_report",
    summary="创建质检报告",
    deprecated=True,
)
async def create_quality(
    req: Request,
    warehouse_id: int = Form(..., description="仓库id"),
    report_type: Literal["仓储加工", "原料运输"] = Form(..., description="报告类型"),
    report_name: Optional[str] = Form(None, description="质检报告名称"),
    file: Optional[UploadFile] = File(None, description="质检报告"),
):
    """
    # 创建质报告
    - **warehouse_id**: 仓库id, 必填
    - **report_name**: 质检报告名称, str, 可选
    - **file**: 质检报告, 可选
    - **report_type**: 报告类型, 必填 范围：仓储加工|原料运输
    """
    filename = save_report(file) if file else None
    with SessionLocal() as db:
        warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not warehouse:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "仓储加工环节不存在"},
            )
        report_name = report_name if report_name else file.filename
        quality = Quality(
            name=report_name,
            report=filename,
            type=report_type,
            status="已上传" if filename else "未上传",
            people=get_user_by_request(req).get("sub") if file else None,
            upload_time=datetime.now() if file else None,
        )
        quality.plan = warehouse.plan
        db.add(quality)
        db.commit()


@report_router.put("/update_report", summary="更新质报告")
async def update_quality(
    req: Request,
    report_id: int = Form(..., description="质检报告id"),
    report_type: Optional[Literal["仓储加工", "原料运输"]] = Form(None, description="报告类型"),
    report_name: Optional[str] = Form(None, description="质检报告名称"),
    file: Optional[UploadFile] = File(None, description="质检报告"),
):
    """
    # 更新质报告
    - **report_id**: 质检报告id
    - **report_name**: 质检报告名称, 可选
    - **file**: 质检报告, 可选, 文件类型
    - **report_type**: 报告类型, 可选 范围：仓储加工|原料运输
    """
    with SessionLocal() as db:
        quality = db.query(Quality).filter(Quality.id == report_id).first()
        if not quality:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "质检记录不存在"},
            )
        if file:
            delete_report(quality.report)
            filename = save_report(file)
            quality.report = filename
            quality.status = "已上传"
            quality.people = get_user_by_request(req).get("sub")
            quality.upload_time = datetime.now()
        if report_name:
            quality.name = report_name
        else:
            if file:
                quality.name = file.filename
        if report_type:
            quality.type = report_type
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "更新成功"},
        )


@report_router.delete("/delete_report", summary="删除质报告")
async def delete_quality(
    report_id: int = Query(..., description="质检报告id"),
):
    """
    # 删除质报告
    - **report_id**: 质检报告id
    """
    with SessionLocal() as db:
        quality = db.query(Quality).filter(Quality.id == report_id).first()
        if quality.report:
            delete_report(quality.report)
        db.delete(quality)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "success"},
        )
