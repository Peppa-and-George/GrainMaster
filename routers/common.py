from enum import Enum

from fastapi import Depends, Query
from typing import Optional


class Order(str, Enum):
    ASC = "asc"
    DESC = "desc"


async def sort(
    field: str = Query(..., title="排序字段", description="排序字段", example="id"),
    order: Order = Query(
        Order.ASC, title="排序方式", description="排序方式", example="asc", default=Order.ASC
    ),
):
    return {"field": field, "order": order}


def pagination(
    page: Optional[int] = Query(1, title="页码", description="页码", example=1, ge=1),
    size: Optional[int] = Query(
        20, title="每页数量", description="每页数量", example=10, ge=1, le=100
    ),
):
    return {"page": page, "size": size}
