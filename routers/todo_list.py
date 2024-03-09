from datetime import datetime
from typing import Optional, Literal

from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from fastapi import status, Query, Body

from models.base import TodoListSchema
from schema.common import transform_schema, page_with_order
from schema.tables import TodoList
from schema.database import SessionLocal

todo_list_router = APIRouter()


@todo_list_router.post("/add_todo_list", summary="添加待办事项")
async def add_todo_list(
    title: str = Body(..., embed=True, alias="title"),
    content: str = Body(..., embed=True, alias="content"),
    sender: Optional[str] = Body(None, embed=True, alias="sender"),
):
    """
    # 添加待办事项
    - **title**: 待办事项标题, 必填, str
    - **content**: 待办事项内容, 必填, str
    - **sender**: 发送者, 非必填, str
    """
    with SessionLocal() as session:
        todo_list = TodoList(title=title, content=content, sender=sender)
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
    sender: Optional[str] = Query(None, description="发送者"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    order_by: str = Query("id", description="排序字段"),
    order: Literal["asc", "desc"] = Query("desc", description="排序方式"),
):
    """
    # 获取待办事项
    - **todo_id**: 待办事项id, 非必填, int
    - **sender**: 发送者, 非必填, str
    - **page**: 页码, 非必填, int
    - **page_size**: 每页数量, 非必填, int
    - **order_by**: 排序字段, 非必填, str
    - **order**: 排序方式, 非必填, str
    """
    with SessionLocal() as session:
        query = session.query(TodoList)
        if todo_id:
            query = query.filter(TodoList.id == todo_id)
        if sender:
            query = query.filter(TodoList.sender == sender)
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
    read: Optional[bool] = Query(None, description="是否已读"),
    completed: Optional[bool] = Query(None, description="是否已完成"),
):
    """
    # 更新待办事项
    - **todo_id**: 待办事项id, 必填, int
    - **title**: 待办事项标题, 非必填, str
    - **content**: 待办事项内容, 非必填, str
    - **sender**: 发送者, 非必填, str
    - **read**: 是否已读, 非必填, bool
    - **completed**: 是否已完成, 非必填, bool
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
            todo_list.sender = sender
        if read is not None:
            todo_list.read = read
        if completed is not None:
            todo_list.complete = completed
            todo_list.complete_time = datetime.now()
        session.commit()
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
):
    """
    # 标记已完成
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
        todo_list.complete = True
        todo_list.complete_time = datetime.now()
        session.commit()
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
