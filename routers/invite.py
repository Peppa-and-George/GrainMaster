import uuid
from typing import Union, Literal, Optional

from fastapi import APIRouter, status, Body, Query, Request
from fastapi.responses import JSONResponse
import base64
from datetime import datetime

from models.base import InviteSchema
from routers.todo_list import add_todo
from schema.common import page_with_order, transform_schema
from schema.tables import Invite, ClientPrivilege
from schema.database import SessionLocal
from auth import get_user_by_request

invite_router = APIRouter()


def generate_invite_code():
    return base64.b64encode(uuid.uuid4().hex.encode("utf8").rstrip())[:25].decode(
        "utf8"
    )


@invite_router.get("/get_invite", summary="获取邀请列表", status_code=status.HTTP_200_OK)
async def get_invite(
    invite: Union[str, int, None] = Query(None, description="邀请者标识", examples=[1]),
    field_type: Literal["invite_code", "id"] = Query("invite_code", description="字段类型"),
    confirmed: Optional[bool] = Query(None, description="是否确认"),
    start_time: Optional[str] = Query(
        None, description="开始时间", examples=["2021-01-01 00:00:00"]
    ),
    end_time: Optional[str] = Query(
        None, description="结束时间", examples=["2021-01-01 00:00:00"]
    ),
    client: Optional[int] = Query(None, description="受邀客户ID"),
    order_field: str = Query("id", description="排序字段", examples=["invite_time"]),
    order: Literal["asc", "desc"] = Query(
        "desc", description="排序类型", examples=["asc", "desc"]
    ),
    page: int = Query(1, description="页码", examples=[1]),
    page_size: int = Query(10, description="每页数量", examples=[10]),
):
    """
    # 获取邀请列表
    - **invite**: 邀请者标识, str | int, 可选
    - **field_type**: 字段类型, str, required, enum: invite_code, id
    - **confirmed**: 是否确认, bool, 可选
    - **start_time**: 邀请时间过滤字段，最早时间, str, 可选, example: 2021-01-01 00:00:00
    - **end_time**: 邀请时间过滤字段，最晚时间, str, 可选, example: 2021-01-01 00:00:00
    - **client**: 受邀客户ID, int, 可选
    """
    with SessionLocal() as db:
        query = db.query(Invite)
        if invite:
            if field_type == "invite_code":
                query = query.filter(Invite.invite_code == invite)
            else:
                query = query.filter(Invite.id == invite)

        if confirmed is not None:
            query = query.filter(Invite.confirmed == confirmed)

        if start_time:
            query = query.filter(
                Invite.invite_time >= datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            )

        if end_time:
            query = query.filter(
                Invite.invite_time <= datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            )

        if client:
            query = query.filter(Invite.client_id == client)

        response = page_with_order(
            InviteSchema, query, page, page_size, order_field, order
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response,
        )


@invite_router.post(
    "/create_invite", summary="创建邀请", status_code=status.HTTP_201_CREATED
)
async def create_invite(
    req: Request,
    client_privilege_id: int = Query(
        ..., description="客户权益ID", examples=[1], embed=True
    ),
    notify: bool = Query(False, description="是否通知", examples=[False], embed=True),
):
    """
    # 创建邀请
    - **client_privilege**: 客户权益, int, required
    - **notify**: 是否通知, bool, optional, example: False
    """
    with SessionLocal() as db:
        client_privilege = (
            db.query(ClientPrivilege)
            .filter(ClientPrivilege.id == client_privilege_id)
            .first()
        )

        if not client_privilege:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "客户权益不存在"},
            )

        if client_privilege.unused_amount <= 0:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "受邀客户权益已用完"},
            )
        current_user = get_user_by_request(req).get("sub")
        invite = Invite(
            sponsor=current_user,
            invite_code=generate_invite_code(),
            invite_time=datetime.now(),
        )
        invite.invited_customer = client_privilege.client
        invite.client_privilege = client_privilege
        db.add(invite)
        db.commit()
        db.flush()
        db.refresh(invite)

        if notify:
            add_todo(
                title="权限使用申请",
                content=f"您收到了来自{client_privilege.client.name}的权限是使用申请, 请及时处理, 申请时间: {datetime.strftime(invite.invite_time, '%Y-%m-%d %H:%M:%S')}, 权限名称: {client_privilege.privilege.name}",
                sender=client_privilege.client.id,
                sender_field_type="id",
                tag=6,
            )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "code": 0,
                "message": "邀请创建成功",
                "data": transform_schema(InviteSchema, invite),
            },
        )


@invite_router.put("confirm_invite", summary="确认邀请", status_code=status.HTTP_200_OK)
async def confirm_invite(
    invite: Union[str, int] = Body(..., description="邀请者标识", examples=[1]),
    field_type: Literal["invite_code", "id"] = Body("invite_code", description="字段类型"),
):
    """
    # 确认邀请
    - **invite**: 邀请者标识, str | int, required
    - **field_type**: 字段类型, str, required, enum: invite_code, id
    """
    with SessionLocal() as db:
        if field_type == "invite_code":
            invite = db.query(Invite).filter(Invite.invite_code == invite).first()
        else:
            invite = db.query(Invite).filter(Invite.id == invite).first()

        if not invite:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "不存在的邀请"},
            )

        invite.confirmed = True
        invite.confirmed_time = datetime.now()
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "邀请确认成功"},
        )


@invite_router.delete("/delete_invite", summary="删除邀请", status_code=status.HTTP_200_OK)
async def delete_invite(
    invite: Union[str, int] = Body(..., description="邀请者标识", examples=[1]),
    field_type: Literal["invite_code", "id"] = Body("invite_code", description="字段类型"),
):
    """
    # 删除邀请
    - **invite**: 邀请者标识, str | int, required
    - **field_type**: 字段类型, str, required, enum: invite_code, id
    """
    with SessionLocal() as db:
        if field_type == "invite_code":
            invite = db.query(Invite).filter(Invite.invite_code == invite).first()
        else:
            invite = db.query(Invite).filter(Invite.id == invite).first()

        if not invite:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "message": "不存在的邀请"},
            )

        db.delete(invite)
        db.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "邀请删除成功"},
        )
