from pydantic import BaseModel, field_validator, Field
from typing import Literal, Any

from pydantic_core.core_schema import ValidationInfo


class PaginationModel(BaseModel):
    page: int = Field(default=1, title="页码", description="页码, 从1开始")
    page_size: int = Field(default=20, title="分页大小", description="分页大小")

    @field_validator("page")
    @classmethod
    def check_page_field(cls, v, field_info: ValidationInfo):
        if v < 1:
            raise ValueError(f"{field_info.field_name}参数错误, 不能小于1")
        return v

    @field_validator("page_size")
    @classmethod
    def check_page_size_field(cls, v, field_info: ValidationInfo):
        if v < 1:
            raise ValueError(f"{field_info.field_name}参数错误, 不能小于1")
        elif v > 100:
            raise ValueError(f"{field_info.field_name}参数错误, 不能大于100")
        return v


class SortModel(BaseModel):
    order_field: str = Field(default="id", title="排序字段", description="排序字段")
    order: Literal["asc", "desc"] = Field(
        default="asc", title="排序方式", description="排序方式, asc: 升序, desc: 降序, 默认升序"
    )


class ResStatus(BaseModel):
    code: int = Field(default=0, title="状态码", description="状态码, 0: 成功, 1: 失败")
    message: str = Field(default="Successful", title="状态信息", description="状态信息")
    data: Any = Field(default=None, title="返回数据", description="返回数据")


class CommonQueryParm(PaginationModel, SortModel):
    pass


if __name__ == "__main__":
    q = CommonQueryParm(order_field="product_id", order="asc", page=1, page_size=100)
    print(q.model_dump(by_alias=False))
