from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

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
):
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
            return JSONResponse(
                status_code=status.HTTP_200_OK, content={"code": 1, "message": "接收者不存在"}
            )

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
        db.commit()
        return {"code": 0, "message": "消息添加成功"}


# @message_router.post("/add")
