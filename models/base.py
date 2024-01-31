from pydantic import BaseModel, Field, field_serializer, ConfigDict
from typing import Any, List, Union, Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    name: str
    phone_number: int


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

    location: LocationSchema = Field(description="基地信息")

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


class SegmentSchema(BaseModel):
    id: int = Field(description="种植ID")
    name: str = Field(description="种植名称")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")

    operations: List["OperationSchema"] = Field(description="操作信息")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class PlanSegmentRelationshipSchema(BaseModel):
    plan_id: int = Field(description="计划ID")
    segment_id: int = Field(description="种植ID")
    operator: str = Field(description="操作人")
    operation_date: datetime = Field(description="操作日期")
    remarks: Optional[str] = Field(description="备注")
    image_uri: Optional[str] = Field(description="图片地址")
    video_uri: Optional[str] = Field(description="视频地址")
    status: Optional[str] = Field(description="状态")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")

    segment: SegmentSchema = Field(description="种植信息")
    plan: PlanSchema = Field(description="计划信息")

    @field_serializer("create_time", "update_time", "operation_date")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S")

    model_config = ConfigDict(from_attributes=True)


class OperationSchema(BaseModel):
    id: int = Field(description="操作ID")
    segment_id: int = Field(description="种植ID")
    name: str = Field(description="操作名称")
    index: int = Field(description="操作顺序")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""


class TransportSchema(BaseModel):
    id: int = Field(description="运输ID")
    plant_id: int = Field(description="种植ID")
    operate_date: datetime = Field(description="操作时间")
    loading_worker: str = Field(description="装车人")
    driver: str = Field(description="运输人员")
    unload_worker: str = Field(description="卸车人")
    unload_place: str = Field(description="卸车地点")
    air_worker: str = Field(description="晾晒人员")
    clean_worker: str = Field(description="清洗人员")
    after_clean_driver: str = Field(description="清洗后运输人员")
    after_unload_worker: str = Field(description="清洗后卸车人员")
    after_unload_place: str = Field(description="清洗后卸车地点")
    notices: str = Field(description="备注")
    status: str = Field(description="状态")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "operate_date")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class WarehouseSchema(BaseModel):
    id: int = Field(description="仓库ID")
    plan_id: int = Field(description="计划ID")
    operate_date: datetime = Field(description="计划操作日期")
    feeding_place: str = Field(description="投料口转运")
    feeding_warehouse: str = Field(description="投料仓转运地点")
    feeding: str = Field(description="投料")
    press: str = Field(description="压榨")
    refine: str = Field(description="精炼")
    sorting: str = Field(description="分装")
    warehousing: str = Field(description="入库")
    product_warehousing: str = Field(description="成品入库地点")
    notices: str = Field(description="备注")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "operate_date")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(BaseModel):
    id: int = Field(description="订单ID")
    client_id: int = Field(description="客户ID")
    plan_id: int = Field(description="计划ID")
    product_id: int = Field(description="产品ID")
    camera_id: int = Field(description="摄像头ID")
    num: str = Field(description="订单编号")
    status: str = Field(description="订单状态")
    customized_area: float = Field(description="定制面积")
    create_time: datetime = Field(description="创建时间")
    complete_time: Optional[datetime] = Field(description="完成时间")
    update_time: datetime = Field(description="更新时间")

    client: ClientSchema = Field(description="客户信息")
    plan: PlanSchema = Field(description="计划信息")
    product: ProductSchema = Field(description="产品信息")
    camera: "CameraSchema" = Field(description="摄像头信息")
    address: AddressSchema = Field(description="地址信息")

    @field_serializer("create_time", "update_time", "complete_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class LogisticsPlanSchema(BaseModel):
    id: int = Field(description="物流计划ID")
    plan_id: int = Field(description="计划ID")
    operate_date: datetime = Field(description="计划操作日期")
    operate_people: str = Field(description="操作人员")
    order: int = Field(description="订单ID")
    notices: str = Field(description="备注")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")

    order: OrderSchema = Field(description="订单信息")

    @field_serializer("create_time", "update_time", "operate_date")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class CameraSchema(BaseModel):
    id: int = Field(description="摄像头ID")
    name: Optional[str] = Field(description="摄像头名称", default=None)
    alise_name: Optional[str] = Field(description="摄像头别名", default=None)
    sn: str = Field(description="摄像头序列号")
    status: int = Field(description="摄像头状态")
    address: Optional[str] = Field(description="摄像头地址", default=None)
    location: Optional[str] = Field(description="摄像头位置", default=None)
    stream_url: Optional[str] = Field(description="摄像头流地址", default=None)
    expire_time: Optional[datetime] = Field(description="摄像头过期时间", default=None)
    update_time: datetime = Field(description="更新时间")
    create_time: datetime = Field(description="创建时间")

    @field_serializer("create_time", "update_time", "expire_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class QualitySchema(BaseModel):
    id: int = Field(description="质检报告ID")
    plan_id: int = Field(description="计划ID")
    name: str = Field(description="质检报告名称")
    people: Optional[str] = Field(description="质检人员", default=None)
    status: Optional[str] = Field(description="质检状态", default=None)
    report_url: Optional[str] = Field(description="质检报告地址", default=None)
    upload_time: datetime = Field(description="上传时间")
    create_time: datetime = Field(description="创建时间")
    update_time: datetime = Field(description="更新时间")

    plan: PlanSchema = Field(description="计划信息")

    @field_serializer("create_time", "update_time", "upload_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S")

    model_config = ConfigDict(from_attributes=True)
