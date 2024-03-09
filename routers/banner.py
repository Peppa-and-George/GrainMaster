from typing import Optional, Literal, List

from fastapi.routing import APIRouter
from fastapi import Query, status, Form, UploadFile, File
from fastapi.responses import JSONResponse

from models.base import BannerSchema
from schema.tables import Banner, BannerFile
from schema.database import SessionLocal
from dependency.file import save_upload_file, delete_file
from dependency.image import save_upload_image, delete_image
from schema.common import transform_schema, page_with_order

banner_router = APIRouter()


@banner_router.get("/get_banner", summary="获取banner列表")
async def get_banner(
    banner_id: Optional[int] = Query(None, description="banner id"),
    name: Optional[str] = Query(None, description="banner标题"),
    fuzzy: bool = Query(False, description="模糊查询"),
    synchronize: Optional[bool] = Query(None, description="同步状态"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order: Literal["asc", "desc"] = Query("asc", description="排序"),
    order_field: str = Query("id", description="排序字段"),
):
    """
    # 获取banner信息
    ## params
    - **name**: banner标题, 可选
    - **synchronize**: 同步状态, 可选
    - **fuzzy**: 模糊查询, 可选, 默认False
    - **page**: 页码, 从1开始, 可选, 默认1
    - **page_size**: 分页大小，默认10，范围1-100, 可选, 默认10
    - **order**: 排序方式, 可选, 默认asc
    - **order_field**: 排序字段, 可选, 默认id
    """
    with SessionLocal() as db:
        query = db.query(Banner).join(BannerFile)
        if banner_id:
            query = query.filter(Banner.id == banner_id)
        if name:
            if fuzzy:
                query = query.filter(Banner.name.like(f"%{name}%"))
            else:
                query = query.filter(Banner.name == name)
        if synchronize is not None:
            query = query.filter(Banner.synchronize == synchronize)
        response = page_with_order(
            schema=BannerSchema,
            query=query,
            page=page,
            page_size=page_size,
            order=order,
            order_field=order_field,
            distinct_field=Banner.id,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "获取成功", "data": response},
        )


@banner_router.post("/add_banner", summary="添加banner")
async def add_banner(
    name: str = Form(..., description="banner标题"),
    icons: List[UploadFile] = File(..., description="banner封面"),
    synchronize: bool = Form(False, description="同步状态"),
):
    """
    # 添加banner
    ## params
    - **name**: banner标题, 必填, str
    - **icon**: banner封面, 必填, List[File]
    - **synchronize**: 同步状态, 可选, 默认False
    """
    with SessionLocal() as db:
        if synchronize:
            db.query(Banner).filter(Banner.synchronize == True).update(
                {Banner.synchronize: False}
            )
            db.commit()
        banner = Banner(name=name, synchronize=synchronize)
        for icon in icons:
            icon_filename = save_upload_image(icon)
            banner_file = BannerFile(filename=icon_filename)
            banner.files.append(banner_file)
        db.add(banner)
        db.flush()
        db.refresh(banner)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "添加成功",
                "data": transform_schema(BannerSchema, banner),
            },
        )


@banner_router.put("/update_banner", summary="更新banner")
async def update_banner(
    banner_id: int = Query(..., description="banner id"),
    name: Optional[str] = Query(None, description="banner标题"),
    synchronize: Optional[bool] = Query(None, description="同步状态"),
):
    """
    # 更新banner
    ## params
    - **banner_id**: banner id, 必填, int
    - **name**: banner标题, 可选, str
    - **synchronize**: 同步状态, 可选, bool
    """
    with SessionLocal() as db:
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        if not banner:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "banner不存在"},
            )
        if name:
            banner.name = name
        if synchronize is not None:
            if synchronize:
                db.query(Banner).filter(Banner.synchronize == True).update(
                    {Banner.synchronize: False}
                )
            banner.synchronize = synchronize
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "更新成功",
                "data": transform_schema(BannerSchema, banner),
            },
        )


@banner_router.delete("/delete_banner", summary="删除banner")
async def delete_banner(
    banner_id: int = Form(..., description="banner id"),
):
    """
    # 删除banner
    ## params
    - **banner_id**: banner id, 必填, int
    """
    with SessionLocal() as db:
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        if not banner:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "banner不存在"},
            )
        for file in banner.files:
            if file.filename:
                delete_image(file.filename)
            db.delete(file)
        db.delete(banner)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "删除成功"},
        )
