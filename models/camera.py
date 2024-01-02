from datetime import datetime

from pydantic import BaseModel, Field, field_serializer, ConfigDict
from models.common import BatchQueryResponseModel, CommonQueryParm


class CameraSchema(BaseModel):
    id: int = Field(..., description="摄像头ID")
    name: str = Field(..., description="摄像头名称")
    sn: str = Field(..., description="摄像头序列号")
    state: str = Field(..., description="摄像头状态")
    address: str | None = Field(..., description="摄像头地址")
    location: str | None = Field(..., description="摄像头位置")
    step: str | None = Field(..., description="所属环节")
    update_time: datetime = Field(default=datetime.now(), description="更新时间")
    create_time: datetime = Field(datetime.now(), description="创建时间")

    @field_serializer("update_time", "create_time")
    def format_time(self, v):
        return v.strftime("%Y-%m-%d %H:%M:%S")


# ------------query params------------
class AddCameraModel(BaseModel):
    name: str = Field(..., description="摄像头名称")
    sn: str = Field(..., description="摄像头序列号")
    state: str = Field(..., description="摄像头状态")
    address: str | None = Field(default=None, description="摄像头地址")
    location: str | None = Field(default=None, description="摄像头位置")
    step: str | None = Field(default=None, description="所属环节")

    model_config = ConfigDict(
        from_attributes=True,
    )


class FilterCameraModel(CommonQueryParm):
    name: str | None = Field(default=None, description="摄像头名称")
    address: str | None = Field(default=None, description="摄像头地址")
    step: str | None = Field(default=None, description="所属环节")
    fuzzy: bool = Field(default=True, description="是否模糊查询")

    model_config = ConfigDict(
        from_attributes=True,
    )


# ------------response model------------
class BatchQueryCameraResponseModel(BatchQueryResponseModel):
    data: list[CameraSchema] = Field(..., description="摄像头列表")

    model_config = ConfigDict(
        from_attributes=True,
    )
