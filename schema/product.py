from sqlalchemy.orm.query import Query

from schema.tables import Product
from schema.common import (
    query_with_filter,
    query_with_like_filter,
)
from schema.database import SessionLocal


def get_products() -> Query:
    """
    获取商品列表
    """
    with SessionLocal() as db:
        query = db.query(Product)
        return query


def get_products_by_name(
    name: str,
    fuzzy: bool = False,
) -> Query:
    """
    通过name获取商品
    :param name: 商品name
    :param fuzzy: 是否模糊查询
    """
    with SessionLocal() as db:
        query = db.query(Product)
        if fuzzy:
            query = query_with_like_filter(query, name=name)
        else:
            query = query_with_filter(query, name=name)
        return query
