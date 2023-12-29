from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict, field_serializer

from models.common import CommonQueryParm, BatchQueryResponseModel


class LocationSchema(BaseModel):
    """
    数据库中位置表的字段
    """

    id: int = Field(..., title="位置ID")
    name: str = Field(..., title="位置名称")
    type: str = Field(..., title="位置类型")
    detail: str = Field("", title="详细地址")
    longitude: float = Field(..., title="经度")
    latitude: float = Field(..., title="纬度")
    area: float | None = Field(0.0, title="面积")
    customized: str | None = Field("", title="是否定制")
    create_time: datetime | None = Field(title="创建时间", default=datetime.now)
    update_time: datetime | None = Field(title="更新时间", default=datetime.now)

    model_config = ConfigDict(
        from_attributes=True,
    )

    @field_serializer("create_time", "update_time")
    def serializer_datetime(self, v):
        return v.strftime("%Y-%m-%d %H:%M:%S")


class LocationNecessaryFields(BaseModel):
    """
    位置必要字段
    """

    name: str = Field(..., title="位置名称", examples=["测试位置"])
    type: str = Field(..., title="位置类型", examples=["测试类型"])
    detail: str = Field("", title="详细地址", examples=["测试详情"])
    longitude: float = Field(..., title="经度", examples=[0.0])
    latitude: float = Field(..., title="纬度", examples=[0.0])
    area: float | None = Field(None, title="面积", examples=[0.0])
    customized: str | None = Field(None, title="是否定制", examples=[None])

    model_config = ConfigDict(
        from_attributes=True,
    )


#  ----------- Request Models -----------
class BatchQueryLocationsModel(CommonQueryParm):
    pass


class FilterLocationModel(CommonQueryParm):
    name: str | None = Field(default=None, title="位置名称", example="测试位置")
    type: str | None = Field(default=None, title="位置类型", example="测试类型")
    customized: str | None = Field(default=None, title="是否定制", example="非定制")
    fuzzy: bool = Field(default=False, title="是否模糊查询", example=False)


# ----------- Response Models -----------
class BatchQueryLocationsResponseModel(BatchQueryResponseModel):
    data: List[LocationSchema]

    model_config = ConfigDict(
        from_attributes=True,
    )
