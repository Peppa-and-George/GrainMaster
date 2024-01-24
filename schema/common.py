from typing import Any, Tuple, Literal
from collections.abc import Iterable

from sqlalchemy.orm.query import Query
from sqlalchemy import desc, asc


def transform_schema(schema: Any, data: Any) -> list:
    """
    将schema转换为dict
    :param schema: schema对象
    :param data: 需要转换的数据
    """
    if not isinstance(data, Iterable):
        data = [data]
    return [
        schema.model_validate(item, from_attributes=True).model_dump() for item in data
    ]


def page_with_order(
    schema: Any,
    query: Query,
    page: int = 1,
    page_size: int = 10,
    order_field: str = "id",
    order: Literal["desc", "asc"] = "asc",
) -> dict:
    """
    排序和分页
    :param schema: schema对象
    :param query: 查询对象
    :param page: 页码, 默认1
    :param page_size: 每页数量, 默认10
    :param order_field: 排序字段, 默认id
    :param order: 排序方式, 默认asc
    """
    query = query_with_page_and_order(query, page, page_size, order_field, order)
    total = query.count()
    total_page = (
        total // page_size + 1 if total % page_size != 0 else total // page_size
    )
    data = query.all()
    data = transform_schema(schema, data)
    return {
        "total": total,
        "total_page": total_page,
        "page": page,
        "page_size": page_size,
        "order_field": order_field,
        "order": order,
        "data": data,
        **{
            "code": 0,
            "message": "查询成功",
        },
    }


def verify_fields(table: Any, fields: list) -> None:
    """
    验证字段是否存在
    :param table: 查询的表
    :param fields: 需要验证的字段
    """
    if not isinstance(fields, list):
        raise TypeError("fields参数错误, 请传入list类型")
    for field in fields:
        if field not in table.columns.keys():
            raise ValueError(f"字段: {field} 错误, 不存在该字段")


def query_with_order(
    query: Query, order_field: str = "id", order: Literal["desc", "asc"] = "asc"
) -> Query:
    """
    排序
    :param query: 查询对象
    :param order_field: 排序字段, 默认id
    :param order: 排序方式, 默认asc
    """
    if not len(query.column_descriptions):
        raise ValueError("查询对象错误")
    table = query.column_descriptions[0].get("entity").__table__
    verify_fields(table, [order_field])
    order_field = table.columns.get(order_field)
    query = query.order_by(desc(order_field) if order == "desc" else asc(order_field))
    return query


def query_with_page(query: Query, page: int = 1, page_size: int = 10) -> Query:
    """
    分页
    :param query: 查询对象
    :param page: 页码, 默认1
    :param page_size: 每页数量, 默认10
    """
    query = query.offset((page - 1) * page_size).limit(page_size)
    return query


def query_with_page_and_order(
    query: Query,
    page: int = 1,
    page_size: int = 10,
    order_field: str = "id",
    order: Literal["desc", "asc"] = "asc",
) -> Query:
    """
    分页和排序
    :param query: 查询对象
    :param page: 页码, 默认1
    :param page_size: 每页数量, 默认10
    :param order_field: 排序字段, 默认id
    :param order: 排序方式, 默认asc
    """
    query = query_with_order(query, order_field, order)
    query = query_with_page(query, page, page_size)
    return query


def query_with_filter(query: Query, **kwargs: Any) -> Query:
    """
    过滤
    :param query: 查询对象
    :param kwargs: 过滤条件
    """
    if not len(query.column_descriptions):
        raise ValueError("查询对象错误")
    table = query.column_descriptions[0].get("entity").__table__
    verify_fields(table, list(kwargs.keys()))
    for k, v in kwargs.items():
        query = query.filter_by(**{k: v})
    return query


def query_with_like_filter(query: Query, **kwargs: Any) -> Query:
    """
    模糊过滤
    :param query: 查询对象
    :param kwargs: 过滤条件
    """
    if not len(query.column_descriptions):
        raise ValueError("查询对象错误")
    table = query.column_descriptions[0].get("entity").__table__
    verify_fields(table, list(kwargs.keys()))
    for k, v in kwargs.items():
        query = query.filter(getattr(table.columns, k).like(f"%{v}%"))
    return query
