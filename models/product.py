from pydantic import BaseModel, field_validator, Field, field_serializer, ConfigDict
from pydantic_core.core_schema import ValidationInfo, SerializationInfo
from typing import List
from datetime import datetime

from models.common import CommonQueryParm, ResStatus, BatchQueryResponseModel


class ProductSchema(BaseModel):
    id: int = Field(default=None, title="商品id", description="商品id")
    name: str = Field(
        default=None,
        title="商品名称",
        description="商品名称",
        max_length=50,
        examples=["test product"],
    )
    introduction: str = Field(
        default=None,
        title="商品介绍",
        description="商品介绍",
        max_length=255,
        examples=["test"],
    )
    price: float = Field(title="价格", description="价格", examples=[1, 2, 3, 4, 5])
    unit: float = Field(title="单位", description="单位", examples=[1, 2, 3, 4, 5])
    icon: str = Field(title="图标", description="图标", examples=["test icon"])
    synchronize: bool = Field(default=False, title="是否异步", description="是否异步")
    create_time: datetime = Field(default=None, title="创建时间", description="创建时间")
    update_time: datetime = Field(default=None, title="更新时间", description="更新时间")

    @field_serializer("create_time", "update_time")
    def serializer_datetime(self, v, _field_info: SerializationInfo):
        return v.strftime("%Y-%m-%d %H:%M:%S")

    model_config = ConfigDict(
        from_attributes=True,
    )


# ----------- Response Models -----------
class QueryProductsResponseModel(BatchQueryResponseModel):
    data: List[ProductSchema]

    model_config = ConfigDict(
        from_attributes=True,
    )


class AddProductResponseModel(ResStatus):
    ...


class AddProductsResponseModel(ResStatus):
    ...


# ----------- Query Models -----------
class QueryProductsModel(CommonQueryParm):
    order_field: str = Field(
        default="id",
        title="排序字段",
        description="排序字段, 默认product_id",
        alias="orderField",
    )


class QueryProductByNameModel(CommonQueryParm):
    product_name: str = Field(
        title="商品名称",
        description="商品名称",
        max_length=50,
        examples=["test product"],
        alias="productName",
    )

    fuzzy: bool = Field(
        default=False,
        title="是否模糊查询",
        description="是否模糊查询, 默认False",
        alias="fuzzy",
    )


class AddProductModel(BaseModel):
    name: str = Field(
        title="商品名称",
        description="商品名称",
        max_length=50,
        examples=["test product"],
        alias="productName",
    )
    introduction: str = Field(
        default="",
        title="商品介绍",
        description="商品介绍",
        max_length=255,
        examples=["test intro"],
    )
    price: float = Field(title="价格", description="价格", examples=[1, 2, 3, 4, 5])
    unit: float = Field(title="单位", description="单位", examples=[1, 2, 3, 4, 5])
    icon: str = Field(title="图标", description="图标")
    synchronize: bool = Field(
        default=False, title="是否异步", description="是否异步", alias="synchronize"
    )


class UpdateProductModel(BaseModel):
    product_id: int = Field(default=None, title="商品id", description="商品id", alias="id")
    product: AddProductModel


# --------------------

__all__ = [QueryProductsResponseModel]
