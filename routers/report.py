from datetime import datetime
from typing import Literal, Optional

from fastapi import APIRouter, Query, status, Body, Form, UploadFile, File
from fastapi.responses import JSONResponse

from dependency.report import save_report, delete_report
from schema.common import page_with_order
from schema.database import SessionLocal
from schema.tables import Quality, Plan, Location
from models.base import QualitySchema

report_router = APIRouter()


@report_router.get("/filter_report", summary="筛选质报告")
async def filter_quality_api(
    year: Optional[int] = Query(None, description="年份"),
    batch: Optional[int] = Query(None, description="批次"),
    location_name: Optional[str] = Query(None, description="位置"),
    report_status: Optional[str] = Query(
        None, description="报告上传状态", examples=["已上传", "未上传"]
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
            content={"code": 0, "message": "success", "data": response},
        )


@report_router.post("/upload_report", summary="创建质报告")
async def create_quality(
    plan_id: int = Form(..., description="计划id"),
    report_name: str = Form(..., description="质检报告名称"),
    upload_people: str = Form(..., description="上传人"),
    file: UploadFile = File(..., description="质检报告"),
):
    """
    # 创建质报告
    - **plan_id**: 计划id
    - **upload_people**: 上传人
    - **report**: 质检报告
    """
    filename = save_report(file)
    with SessionLocal() as db:
        quality = Quality(
            plan_id=plan_id,
            name=report_name,
            people=upload_people,
            report=filename,
            upload_time=datetime.now(),
        )
        db.add(quality)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "success"},
        )


@report_router.put("/update_report", summary="更新质报告")
async def update_quality(
    report_id: int = Body(..., description="质检报告id"),
    report_name: Optional[str] = Body(None, description="质检报告名称"),
    upload_people: Optional[str] = Body(None, description="上传人"),
    file: UploadFile = File(None, description="质检报告"),
):
    """
    # 更新质报告
    - **report_id**: 质检报告id
    - **upload_people**: 上传人
    - **report**: 质检报告
    """
    with SessionLocal() as db:
        quality = db.query(Quality).filter(Quality.id == report_id).first()
        quality.people = upload_people
        if file:
            filename = save_report(file)
            delete_report(quality.report)
            quality.report = filename
        if report_name:
            quality.name = report_name
        if upload_people:
            quality.people = upload_people
        quality.status = "已上传"
        quality.upload_time = datetime.now()
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "success"},
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
