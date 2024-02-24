from typing import Optional

from fastapi.routing import APIRouter
from fastapi import Body, UploadFile, File, Form, Query, status
from fastapi.responses import JSONResponse

from schema.tables import CompanyInfo
from schema.database import SessionLocal
from dependency.image import save_upload_image, delete_image

company_router = APIRouter()


@company_router.get("/get_companies", summary="获取公司信息")
def get_companies():
    with SessionLocal() as db:
        companies = db.query(CompanyInfo).all()
        data = []
        for company in companies:
            data.append(
                {
                    "id": company.id,
                    "name": company.name,
                    "address": company.address,
                    "phone": company.phone,
                    "email": company.email,
                    "logo": company.logo,
                    "introduction": company.introduction,
                    "process_flow": company.process_flow,
                }
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "success", "data": data, "total": len(data)},
        )


@company_router.post("/add_company", summary="添加公司信息")
def add_company(
    company_name: Optional[str] = Form(
        None, title="公司名称", description="公司名称", example="Company1"
    ),
    company_address: Optional[str] = Form(
        None, title="公司地址", description="公司地址", example="Address1"
    ),
    company_phone: Optional[str] = Form(
        None, title="公司电话", description="公司电话", example="1234567890"
    ),
    company_email: Optional[str] = Form(
        None, title="公司邮箱", description="公司邮箱", example="company@company.com"
    ),
    logo: UploadFile | None = File(None, description="公司logo"),
    introduction: Optional[str] = Form(None, description="公司简介"),
    process_flow: Optional[str] = Form(None, description="工艺流程"),
):
    """
    添加公司信息
    # Form参数
    - **company_name**: 公司名称, str, 可选
    - **company_address**: 公司地址, str, 可选
    - **company_phone**: 公司电话, str, 可选
    - **company_email**: 公司邮箱, str, 可选
    - **logo**: 公司logo, 文件, 可选
    - **introduction**: 公司简介, str, 可选
    - **process_flow**: 工艺流程, str, 可选
    """
    # 保存图片
    filename = save_upload_image(logo) if logo else None
    with SessionLocal() as db:
        company = CompanyInfo(
            name=company_name,
            address=company_address,
            phone=company_phone,
            email=company_email,
            introduction=introduction,
            process_flow=process_flow,
            logo=filename,
        )
        db.add(company)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 200, "msg": "添加成功"}
        )


@company_router.put("/update_company", summary="更新公司信息")
def update_company(
    company_id: int = Body(..., title="公司id", description="公司id"),
    company_name: Optional[str] = Form(
        None, title="公司名称", description="公司名称", example="Company1"
    ),
    company_address: Optional[str] = Form(
        None, title="公司地址", description="公司地址", example="Address1"
    ),
    company_phone: Optional[str] = Form(
        None, title="公司电话", description="公司电话", example="1234567890"
    ),
    company_email: Optional[str] = Form(
        None,
        title="公司邮箱",
        description="公司邮箱",
        example="test@test.com",
    ),
    logo: UploadFile | None = File(None, description="公司logo"),
    introduction: Optional[str] = Form(None, description="公司简介"),
    process_flow: Optional[str] = Form(None, description="工艺流程"),
):
    """
    更新公司信息
    # Form参数
    - **company_id**: 公司id, int, 必选
    - **company_name**: 公司名称, str, 可选
    - **company_address**: 公司地址, str, 可选
    - **company_phone**: 公司电话, str, 可选
    - **company_email**: 公司邮箱, str, 可选
    - **logo**: 公司logo, 文件, 可选
    - **introduction**: 公司简介, str, 可选
    - **process_flow**: 工艺流程, str, 可选
    """
    with SessionLocal() as db:
        company = db.query(CompanyInfo).filter(CompanyInfo.id == company_id).first()
        if not company:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"code": 1, "msg": "公司id不存在"},
            )
        # 删除旧图片
        if company.logo:
            delete_image(company.logo)
        # 保存新图片
        filename = save_upload_image(logo) if logo else None
        company.name = company_name if company_name else company.name
        company.address = company_address if company_address else company.address
        company.phone = company_phone if company_phone else company.phone
        company.email = company_email if company_email else company.email
        company.introduction = introduction if introduction else company.introduction
        company.process_flow = process_flow if process_flow else company.process_flow
        company.logo = filename if filename else company.logo
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 200, "msg": "更新成功"}
        )


@company_router.delete("/delete_company", summary="删除公司信息")
def delete_company(company_id: int = Query(..., title="公司id", description="公司id")):
    """
    删除公司信息
    # Query参数
    - **company_id**: 公司id, int, 必选
    """
    with SessionLocal() as db:
        company = db.query(CompanyInfo).filter(CompanyInfo.id == company_id).first()
        if not company:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"code": 1, "msg": "公司id不存在"},
            )
        # 删除图片
        if company.logo:
            delete_image(company.logo)
        db.delete(company)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 200, "msg": "删除成功"}
        )
