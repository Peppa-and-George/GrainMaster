from pydantic import BaseModel, Field, field_serializer, ConfigDict
from typing import Any, List, Union
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    name: str
    phone_number: int


class UserInfo(User):
    password: str


class UserRestPasswd(BaseModel):
    name: str | int
    new_password: str


class ProductSchema(BaseModel):
    id: int = Field(description="商品id")
    name: str = Field(description="商品名称")
    introduction: str = Field(description="商品简介", default="")
    price: float = Field(description="商品价格")
    unit: float = Field(description="商品规格")
    icon: str = Field(description="商品图片")
    synchronize: bool = Field(description="是否同步", default=False)
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class LocationSchema(BaseModel):
    id: int = Field(description="地址id")
    name: str = Field(description="地址名称")
    type: str = Field(description="位置类型")
    detail: str = Field(description="位置详情")
    longitude: float = Field(description="经度")
    latitude: float = Field(description="纬度")
    area: float = Field(description="面积")
    customized: str = Field(description="是否定制")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class PlanSchema(BaseModel):
    id: int = Field(description="计划ID")
    location_id: int | None = Field(description="基地ID")
    create_people: str | None = Field(description="创建人")
    year: int | None = Field(description="年份")
    batch: int | None = Field(description="批次")
    total_product: int | None = Field(description="总产量(L)")
    surplus_product: int | None = Field(description="剩余产量(L)")
    notices: str | None = Field(description="备注")
    create_time: datetime | None = Field(description="创建时间")
    update_time: datetime | None = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        if v:
            return v.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None

    model_config = ConfigDict(from_attributes=True)


class AddressSchema(BaseModel):
    id: int = Field(description="地址id")
    client_id: int = Field(description="客户id")
    name: str = Field(description="客户名称")
    phone_num: str = Field(description="手机号")
    region: str = Field(description="地区")
    detail_address: str = Field(description="地址")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")
    # client: Union["ClientSchema"] = Field(description="客户信息")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class ClientSchema(BaseModel):
    id: int = Field(description="客户ID")
    type: str = Field(description="客户类型")
    account: str = Field(description="客户账号")
    name: str = Field(description="客户名称")
    activate: bool = Field(description="是否激活", default=False)
    category: str | None = Field(description="客户类别", default=None)
    delete_time: datetime | None = Field(description="删除时间", default=None)
    is_delete: bool = Field(description="是否删除", default=False)
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")
    addresses: Union[List[AddressSchema]] = Field(description="地址列表", default=[])

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class PrivilegeSchema(BaseModel):
    id: int = Field(description="权限ID")
    name: str = Field(description="权限名称")
    privilege_type: str = Field(description="权限类型")
    description: str = Field(description="权限描述")
    deleted: bool = Field(description="权益是否删除")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class ClientPrivilegeRelationSchema(BaseModel):
    id: int = Field(description="客户权限关系ID")
    privilege_number: str = Field(description="权益编号")
    client_id: int = Field(description="客户ID")
    privilege_id: int = Field(description="权限ID")
    expired_date: datetime = Field(description="过期时间")
    effective_time: datetime = Field(description="生效时间")
    use_time: datetime | None = Field(description="使用时间")
    usable: bool = Field(description="是否使用")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")

    client: Union[ClientSchema] = Field(description="客户信息")
    privilege: Union[PrivilegeSchema] = Field(description="权益信息")

    @field_serializer(
        "create_time", "update_time", "use_time", "expired_date", "effective_time"
    )
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)
