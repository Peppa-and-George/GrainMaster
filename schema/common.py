from typing import Any, Tuple

from sqlalchemy.orm.query import Query
from sqlalchemy import desc, asc
from sqlalchemy.orm import sessionmaker

from models.common import CommonQueryParm
from schema.database import engine


def batch_query(
    schema: Any, common_param: CommonQueryParm, query: Query[Any] = None
) -> Tuple[Query[Any], int]:
    """
    分页查询
    :param schema: 查询的表
    :param common_param: 查询参数
    :param query: 查询对象
    """
    if common_param.order_field not in schema.__table__.columns.keys():
        raise ValueError("order_field参数错误, 不存在该字段")
    if not query:
        with sessionmaker(bind=engine)() as session:
            query = session.query(schema)
    total = query.count()
    query = query.order_by(
        desc(getattr(schema, common_param.order_field))
        if common_param.order == "desc"
        else asc(getattr(schema, common_param.order_field))
    )
    query = query.offset((common_param.page - 1) * common_param.page_size).limit(
        common_param.page_size
    )
    return query, total
