import json
from datetime import datetime
from typing import Optional, Literal, Union

from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status, Query, Body

from models.base import TodoListSchema
from routers.message import add_message
from schema.common import transform_schema, page_with_order
from schema.tables import TodoList, Client
from schema.database import SessionLocal

todo_list_router = APIRouter()


@todo_list_router.post("/add_todo_list", summary="添加待办事项")
async def add_todo_list(
    title: str = Body(..., description="待办事项标题"),
    content: str = Body(..., description="待办事项内容"),
    sender: Union[str, int, None] = Body(None, description="发送者"),
    sender_field_type: Literal["id", "name", "phone_number"] = Body(
        "id", description="发送者字段类型"
    ),
    tag: int = Body(default=9, description="标签"),
):
    """
    # 添加待办事项
    - **title**: 待办事项标题, 必填, str
    - **content**: 待办事项内容, 必填, str
    - **sender**: 发送者, 非必填, str
    - **tag**: 标签, 必填, int, 1: 田间种植 2: 原料运输 3: 仓储加工 4: 物流运输 9: 普通消息
    """
    with SessionLocal() as session:
        if sender_field_type == "name":
            sender = session.query(Client).filter(Client.name == sender).first()
        elif sender_field_type == "phone_number":
            sender = session.query(Client).filter(Client.phone_number == sender).first()
        else:
            sender = session.query(Client).filter(Client.id == sender).first()
        todo_list = TodoList(title=title, content=content, tag=tag)
        todo_list.sender = sender
        session.add(todo_list)
        session.flush()
        session.refresh(todo_list)
        session.commit()
        session.refresh(todo_list)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "code": 0,
                "message": "添加成功",
                "data": transform_schema(TodoListSchema, todo_list),
            },
        )


@todo_list_router.get("/get_todo_list", summary="获取待办事项")
async def get_todo_list(
    todo_id: Optional[int] = Query(None, description="待办事项id"),
    sender: Union[str, int, None] = Query(None, description="发送者"),
    sender_field_type: Literal["id", "name", "phone_number"] = Query(
        "id", description="发送者字段类型"
    ),
    read: Optional[bool] = Query(None, description="是否已读"),
    completed: Optional[bool] = Query(None, description="是否已完成"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order_by: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序方式"),
):
    """
    # 获取待办事项
    - **todo_id**: 待办事项id, 非必填, int
    - **sender**: 发送者, 非必填, str | int
    - **sender_field_type**: 发送者字段类型, 非必填, str, id | name | phone_number
    - **read**: 是否已读, 非必填, bool
    - **completed**: 是否已完成, 非必填, bool
    - **page**: 页码, 非必填, int
    - **page_size**: 每页数量, 非必填, int
    - **order_by**: 排序字段, 非必填, str
    - **order**: 排序方式, 非必填, str, asc | desc
    """
    with SessionLocal() as session:
        query = session.query(TodoList)
        if todo_id:
            query = query.filter(TodoList.id == todo_id)
        if sender:
            if sender_field_type == "name":
                sender = session.query(Client).filter(Client.name == sender).first()
            elif sender_field_type == "phone_number":
                sender = (
                    session.query(Client).filter(Client.phone_number == sender).first()
                )
            else:
                sender = session.query(Client).filter(Client.id == sender).first()
            query = query.filter(TodoList.sender == sender)
        if read is not None:
            query = query.filter(TodoList.read == read)
        if completed is not None:
            query = query.filter(TodoList.status == completed)
        response = page_with_order(
            schema=TodoListSchema,
            query=query,
            page=page,
            page_size=page_size,
            order_field=order_by,
            order=order,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "获取成功",
                "data": response,
            },
        )


@todo_list_router.put("/read_todo_list", summary="标记已读")
async def read_todo_list(
    todo_id: int = Query(..., description="待办事项id"),
):
    """
    # 标记已读
    - **todo_id**: 待办事项id, 必填, int
    """
    with SessionLocal() as session:
        todo_list = session.query(TodoList).filter(TodoList.id == todo_id).first()
        if not todo_list:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 1,
                    "message": "待办事项不存在",
                },
            )
        todo_list.read = True
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "标记已读成功",
            },
        )


@todo_list_router.put("/un_read_todo_list", summary="标记未读")
async def un_read_todo_list(
    todo_id: int = Query(..., description="待办事项id"),
):
    """
    # 标记未读
    - **todo_id**: 待办事项id, 必填, int
    """
    with SessionLocal() as session:
        todo_list = session.query(TodoList).filter(TodoList.id == todo_id).first()
        if not todo_list:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 1,
                    "message": "待办事项不存在",
                },
            )
        todo_list.read = False
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "标记未读成功",
            },
        )


@todo_list_router.put("/update_todo_list", summary="更新待办事项")
async def update_todo_list(
    todo_id: int = Query(..., description="待办事项id"),
    title: Optional[str] = Query(None, description="待办事项标题"),
    content: Optional[str] = Query(None, description="待办事项内容"),
    sender: Optional[str] = Query(None, description="发送者"),
    sender_field_type: Literal["id", "name", "phone_number"] = Query(
        "id", description="发送者字段类型"
    ),
    read: Optional[bool] = Query(None, description="是否已读"),
    completed: Optional[bool] = Query(None, description="是否已完成"),
    notify: bool = Query(False, embed=True, alias="notify"),
):
    """
    # 更新待办事项
    - **todo_id**: 待办事项id, 必填, int
    - **title**: 待办事项标题, 非必填, str
    - **content**: 待办事项内容, 非必填, str
    - **sender**: 发送者, 非必填, str
    - **read**: 是否已读, 非必填, bool
    - **completed**: 是否已完成, 非必填, bool
    - **notify**: 是否通知, 非必填, bool
    """
    with SessionLocal() as session:
        todo_list = session.query(TodoList).filter(TodoList.id == todo_id).first()
        if not todo_list:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 1,
                    "message": "待办事项不存在",
                },
            )
        if title:
            todo_list.title = title
        if content:
            todo_list.content = content
        if sender:
            if sender_field_type == "name":
                sender = session.query(Client).filter(Client.name == sender).first()
            elif sender_field_type == "phone_number":
                sender = (
                    session.query(Client).filter(Client.phone_number == sender).first()
                )
            else:
                sender = session.query(Client).filter(Client.id == sender).first()
            todo_list.sender = sender
        if read is not None:
            todo_list.read = read
        if completed is not None:
            todo_list.status = completed
            todo_list.complete_time = datetime.now()
        session.flush()
        session.commit()
        if notify:
            if todo_list.sender_id:
                add_message(
                    title="待办事项更新",
                    content=f"您的待办事项已更新: {todo_list.title}",
                    sender="系统",
                    receiver_id=todo_list.sender_id,
                    message_type="待办事项更新",
                    tag=todo_list.tag,
                    details=json.dumps(transform_schema(TodoListSchema, todo_list)),
                )
            else:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 0,
                        "message": "更新成功, 但接收者不存在, 无法通知",
                    },
                )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "更新成功",
            },
        )


@todo_list_router.put("/complete_todo", summary="标记已完成")
async def complete_todo(
    todo_id: int = Query(..., embed=True, alias="todo_id"),
    notify: bool = Query(False, embed=True, alias="notify"),
):
    """
    # 标记已完成
    - **todo_id**: 待办事项id, 必填, int
    - **notify**: 是否通知, 非必填, bool
    """
    with SessionLocal() as session:
        todo_list = session.query(TodoList).filter(TodoList.id == todo_id).first()
        if not todo_list:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 1,
                    "message": "待办事项不存在",
                },
            )
        todo_list.complete = True
        todo_list.complete_time = datetime.now()
        session.flush()
        session.refresh(todo_list)
        session.commit()
        if notify:
            if todo_list.sender_id:
                add_message(
                    title="待办事项更新",
                    content=f"您的待办事项已完成: {todo_list.title}",
                    sender="系统",
                    receiver_id=todo_list.sender_id,
                    message_type="待办事项更新",
                    tag=todo_list.tag,
                    details=json.dumps(transform_schema(TodoListSchema, todo_list)),
                )
            else:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "code": 0,
                        "message": "标记已完成成功, 但接收者不存在, 无法通知",
                    },
                )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "标记已完成成功",
            },
        )


@todo_list_router.delete("/delete_todo_list", summary="删除待办事项")
async def delete_todo_list(
    todo_id: int = Query(..., embed=True, alias="todo_id"),
):
    """
    # 删除待办事项
    - **todo_id**: 待办事项id, 必填, int
    """
    with SessionLocal() as session:
        todo_list = session.query(TodoList).filter(TodoList.id == todo_id).first()
        if not todo_list:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "code": 1,
                    "message": "待办事项不存在",
                },
            )
        session.delete(todo_list)
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 0,
                "message": "删除成功",
            },
        )
