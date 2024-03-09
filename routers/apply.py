import uuid
from typing import Union, Literal, Optional

from fastapi import APIRouter, status, Body, Query, Request
from fastapi.responses import JSONResponse
import base64
from datetime import datetime

from schema.common import page_with_order, transform_schema
from schema.tables import Apply, ClientPrivilege
from schema.database import SessionLocal
from auth import get_user_by_request
from models.base import ApplySchema

apply_router = APIRouter()


def generate_application_code():
    return base64.b64encode(uuid.uuid4().hex.encode("utf8").rstrip())[:25].decode(
        "utf8"
    )


@apply_router.get(
    "/get_application", summary="获取权益使用申请列表", status_code=status.HTTP_200_OK
)
async def get_application(
    application: Union[str, int, None] = Query(None, description="申请标识", examples=[1]),
    field_type: Literal["application_code", "id"] = Query(
        "application_code", description="字段类型"
    ),
    confirmed: Optional[bool] = Query(None, description="是否确认"),
    agree: Optional[bool] = Query(None, description="是否同意"),
    start_time: Optional[str] = Query(
        None, description="开始时间", examples=["2021-01-01 00:00:00"]
    ),
    end_time: Optional[str] = Query(
        None, description="结束时间", examples=["2021-01-01 00:00:00"]
    ),
    client_id: Optional[int] = Query(None, description="受邀客户ID"),
    order_field: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query(
        "desc", description="排序类型", examples=["asc", "desc"]
    ),
    page: int = Query(1, description="页码", examples=[1]),
    page_size: int = Query(10, description="每页数量", examples=[10]),
):
    """
    # 获取申请列表
    - **application**: 申请标识, str | int, 可选
    - **field_type**: 字段类型, str, required, enum: application_code, id
    - **confirmed**: 是否确认, bool, 可选
    - **agree**: 是否同意, bool, 可选
    - **start_time**: 申请时间过滤字段，最早时间, str, 可选, example: 2021-01-01 00:00:00
    - **end_time**: 申请时间过滤字段，最晚时间, str, 可选, example: 2021-01-01 00:00:00
    - **client_id**: 受邀客户ID, int, 可选
    """
    with SessionLocal() as db:
        query = db.query(Apply)
        if application:
            if field_type == "application_code":
                query = query.filter(Apply.application_code == application)
            else:
                query = query.filter(Apply.id == application)

        if confirmed is not None:
            query = query.filter(Apply.confirmed == confirmed)
        if agree is not None:
            query = query.filter(Apply.agree == agree)
        if start_time:
            query = query.filter(
                Apply.application_time
                >= datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            )
        if end_time:
            query = query.filter(
                Apply.application_time
                <= datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            )
        if client_id:
            query = query.filter(Apply.client_id == client_id)
        response = page_with_order(
            schema=ApplySchema,
            query=query,
            page=page,
            page_size=page_size,
            order_field=order_field,
            order=order,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )


@apply_router.post(
    "/create_application", summary="创建权益使用申请", status_code=status.HTTP_201_CREATED
)
async def create_application(
    client_privilege_id: int = Query(..., description="客户权限ID", examples=[1]),
):
    """
    # 创建申请
    - **client_privilege_id**: 客户权益ID, int, required, example: 1
    """
    with SessionLocal() as db:
        client_privilege = (
            db.query(ClientPrivilege)
            .filter(ClientPrivilege.id == client_privilege_id)
            .first()
        )
        if not client_privilege:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"code": 1, "message": "客户权益不存在"},
            )
        if client_privilege.unused_amount <= 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"code": 1, "message": "客户权益余额不足"},
            )
        application = Apply(
            application_code=generate_application_code(),
            application_time=datetime.now(),
        )
        application.client_privilege = client_privilege
        application.applicant = client_privilege.client
        db.add(application)
        db.flush()
        db.refresh(application)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "code": 0,
                "message": "创建成功",
                "data": transform_schema(ApplySchema, application),
            },
        )


@apply_router.put(
    "/confirm_application", summary="确认权益使用申请", status_code=status.HTTP_200_OK
)
async def confirm_application(
    req: Request,
    application: Union[str, int] = Query(..., description="申请标识", examples=["1"]),
    field_type: Literal["application_code", "id"] = Query(
        "application_code", description="字段类型"
    ),
    agree: bool = Query(None, description="是否同意", examples=[True]),
):
    """
    # 确认申请
    - **application**: 申请标识, str, required, example: 1
    - **field_type**: 字段类型, str, required, example: application_code
    - **agree**: 是否同意, bool, required, example: True
    """
    with SessionLocal() as db:
        if application:
            if field_type == "application_code":
                application_obj = (
                    db.query(Apply)
                    .filter(Apply.application_code == application)
                    .first()
                )
            else:
                application_obj = (
                    db.query(Apply).filter(Apply.id == application).first()
                )
        if not application_obj:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "权益申请不存在"},
            )
        application_obj.confirmed = True
        application_obj.agree = agree
        approve = get_user_by_request(req).get("sub")
        application_obj.approve = approve
        application_obj.confirmed_time = datetime.now()
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "邀约申请确认成功"},
        )


@apply_router.delete(
    "/delete_application", summary="删除权益使用申请", status_code=status.HTTP_200_OK
)
async def delete_application(
    application: Union[str, int] = Query(..., description="申请标识", examples=["1"]),
    field_type: Literal["application_code", "id"] = Query(
        "application_code", description="字段类型"
    ),
):
    """
    # 删除申请
    - **application**: 申请标识, str, required, example: 1
    - **field_type**: 字段类型, str, required, example: application_code
    """
    with SessionLocal() as db:
        if field_type == "application_code":
            application = (
                db.query(Apply).filter(Apply.application_code == application).first()
            )
        else:
            application = db.query(Apply).filter(Apply.id == application).first()
        if not application:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "权益申请不存在"},
            )
        db.delete(application)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "权益申请删除成功"},
        )
