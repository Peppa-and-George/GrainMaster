from typing import Union, Literal

from fastapi import APIRouter, status, Query
from fastapi.responses import JSONResponse

from models.base import MessageSchema
from schema.common import transform_schema, page_with_order
from schema.tables import Message, Client
from schema.database import SessionLocal

message_router = APIRouter()


def add_message(
    title: str,
    content: str,
    receiver_id: int,
    sender: str,
    message_type: str,
    tag: int,
    details: str,
) -> Message:
    """
    # 添加消息
    - **title**: 标题, string, required
    - **content**: 内容, string, required
    - **receiver_id**: 接收者id, int, required
    - **sender**: 发送者, string, required
    - **message_type**: 消息类型, string, required
    -
    - **details**: 详情, string, required
    """
    with SessionLocal() as db:
        receiver = db.query(Client).filter(Client.id == receiver_id).first()
        if not receiver:
            raise ValueError("接收者不存在")
        message = Message(
            title=title,
            content=content,
            sender=sender,
            type=message_type,
            details=details,
            tag=tag,
        )
        message.receiver = receiver
        db.add(message)
        db.flush()
        db.refresh(message)
        db.commit()
        return message


@message_router.get("/get_message", summary="获取消息")
def get_message(
    receiver: Union[str, int] = Query(
        ..., description="接收者", exapmles=["1", "张山", "18687803452"]
    ),
    receiver_field_type: Literal["id", "name", "phone_number"] = Query(
        "id", description="接收者字段类型"
    ),
    order_by: str = Query("create_time", description="排序字段", examples=["create_time"]),
    order: Literal["asc", "desc"] = Query("desc", description="排序方式"),
    page: int = Query(1, description="页码", examples=[1]),
    page_size: int = Query(10, description="每页数量", examples=[10]),
):
    """
    # 获取消息
    - **receiver**: 接收者, str | int, required, example: 1，张山，18687803452
    - **receiver_field_type**: 接收者字段类型, str, required, enum: id, name, phone_number
    - **order_by**: 排序字段, str, required, example: create_time
    - **order**: 排序方式, str, required, enum: asc, desc
    - **page**: 页码, int, required, example: 1
    - **page_size**: 每页数量, int, required, example: 10
    """
    with SessionLocal() as db:
        query = db.query(Message).join(Client, Message.receiver_id == Client.id)
        if receiver_field_type == "id":
            query = query.filter(Client.id == receiver)
        elif receiver_field_type == "name":
            query = query.filter(Client.name == receiver)
        else:
            query = query.filter(Client.phone_number == receiver)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "msg": "获取成功",
                "data": page_with_order(
                    schema=MessageSchema,
                    query=query,
                    page=page,
                    page_size=page_size,
                    order_field=order_by,
                    order=order,
                ),
            },
        )


@message_router.post("/add_message", summary="添加消息")
def add_message_api(
    title: str,
    content: str,
    receiver_id: int,
    sender: str,
    message_type: str,
    tag: int,
    details: str,
):
    message = add_message(
        title, content, receiver_id, sender, message_type, tag, details
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "code": 0,
            "msg": "添加成功",
            "data": transform_schema(MessageSchema, message),
        },
    )


@message_router.put("/update_message_status", summary="更新消息状态")
def update_message_status(
    message_id: int = Query(..., description="消息id"),
    message_status: bool = Query(..., description="消息状态"),
):
    """
    # 更新消息状态
    - **message_id**: 消息id, int, required
    - **message_status**: 消息状态, bool, required
    """
    with SessionLocal() as db:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "msg": "消息不存在"},
            )
        message.status = message_status
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "msg": "更新成功"},
        )


@message_router.delete("/delete_message", summary="删除消息")
def delete_message(message_id: int = Query(..., description="消息id")):
    """
    # 删除消息
    - **message_id**: 消息id, int, required
    """
    with SessionLocal() as db:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"code": 1, "msg": "消息不存在"},
            )
        db.delete(message)
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "msg": "删除成功"},
        )


@message_router.delete("/delete_all_message", summary="删除所有消息")
def delete_all_message(receiver_id: int = Query(..., description="接收者id")):
    """
    # 删除所有消息
    - **receiver_id**: 接收者id, int, required
    """
    with SessionLocal() as db:
        db.query(Message).filter(Message.receiver_id == receiver_id).delete()
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "msg": "删除成功"},
        )


@message_router.put("/update_all_message_status", summary="更新所有消息状态")
def update_all_message_status(
    receiver_id: int = Query(..., description="接收者id"),
    message_status: bool = Query(..., description="消息状态"),
):
    """
    # 更新所有消息状态
    - **receiver_id**: 接收者id, int, required
    - **message_status**: 消息状态, bool, required
    """
    with SessionLocal() as db:
        db.query(Message).filter(Message.receiver_id == receiver_id).update(
            {Message.status: message_status}
        )
        db.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "msg": "更新成功"},
        )
