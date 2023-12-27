from datetime import datetime
from typing import List, Type

from sqlalchemy import Column, String, Integer, DateTime, Boolean, desc, asc, FLOAT

from sqlalchemy.orm import declarative_base

from models.product import QueryProductsModel, QueryProductByNameModel
from schema.database import engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker(bind=engine)


class Product(Base):
    __tablename__ = "product"  # noqa

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False, comment="产品名称", name="name")
    introduction = Column(
        String, index=True, nullable=False, comment="产品介绍", name="introduction"
    )
    price = Column(FLOAT, nullable=False, comment="价格", name="price")
    unit = Column(FLOAT, index=True, nullable=False, comment="规格(L)", name="unit")
    icon = Column(String, index=True, nullable=False, comment="产品图片路径", name="icon")
    synchronize = Column(
        Boolean,
        index=True,
        nullable=False,
        comment="是否同步小程序",
        default=False,
        name="synchronize",
    )

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        onupdate=datetime.now,
        default=datetime.now,
        comment="更新时间",
        name="update_time",
    )


def query_products(params: QueryProductsModel) -> dict:
    """
    分页查询查询所有商品
    :param params: 查询参数
    """

    if params.order_field not in Product.__table__.columns.keys():
        raise ValueError("order_field参数错误, 不存在该字段")

    with Session() as session:
        query = session.query(Product)
        total = query.count()
        query = query.order_by(
            desc(getattr(Product, params.order_field))
            if params.order == "desc"
            else asc(getattr(Product, params.order_field))
        )
        query = query.offset((params.page - 1) * params.page_size).limit(
            params.page_size
        )
        products = query.all()
        return {
            "total": total,
            "data": products,
            "page": params.page,
            "page_size": params.page_size,
            "order_field": params.order_field,
            "order": params.order,
        }


def query_product_by_id(product_id: int) -> Type[Product] | None:
    """
    根据id查询商品
    :param product_id: 商品id
    """
    with Session() as session:
        product = session.query(Product).filter_by(id=product_id).first()
        return product


def query_product_by_name(params: QueryProductByNameModel) -> dict:
    """
    根据name查询商品
    :param params: 查询参数
    """
    fuzzy = params.fuzzy
    with Session() as session:
        query = session.query(Product)
        if fuzzy:
            query = query.filter(Product.name.like(f"%{params.product_name}%"))
        else:
            query = query.filter_by(name=params.product_name)
        total = query.count()
        query = query.order_by(
            desc(getattr(Product, params.order_field))
            if params.order == "desc"
            else asc(getattr(Product, params.order_field))
        )
        query = query.offset((params.page - 1) * params.page_size).limit(
            params.page_size
        )

        products = query.all()
        return {
            "total": total,
            "data": products,
            "page": params.page,
            "page_size": params.page_size,
            "order_field": params.order_field,
            "order": params.order,
        }


def add_product(product: Product) -> None:
    """
    添加商品
    :param product: 商品信息
    """
    try:
        with Session() as session:
            session.add(product)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e


def add_products(products: List[Product]) -> None:
    """
    添加商品
    :param products: 商品信息
    :return: 添加成功的条数
    """
    try:
        with Session() as session:
            session.add_all(products)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e


def update_product(product_id: int, product: Product) -> int:
    """
    更新商品
    :param product_id: 商品id
    :param product: 商品信息
    :return: 更新成功的条数
    """
    try:
        with Session() as session:
            row_updated = (
                session.query(Product)
                .filter_by(id=product_id)
                .update(
                    {
                        Product.name: product.name,
                        Product.introduction: product.introduction,
                        Product.price: product.price,
                        Product.unit: product.unit,
                        Product.icon: product.icon,
                        Product.synchronize: product.synchronize,
                        Product.update_time: datetime.now(),
                    }
                )
            )
            session.commit()
            return row_updated
    except Exception as e:
        session.rollback()
        raise e


def delete_product_by_id(product_id: int) -> int:
    """
    删除商品
    :param product_id: 商品id
    :return: 删除成功的条数
    """
    try:
        with Session() as session:
            row_deleted = session.query(Product).filter_by(id=product_id).delete()
            session.commit()
            return row_deleted
    except Exception as e:
        session.rollback()
        raise e


__all__ = [
    "Product",
    "query_products",
    "add_product",
    "add_products",
    "update_product",
    "delete_product_by_id",
    "query_product_by_id",
]
