import json

from pydantic import BaseModel, Field, field_serializer, ConfigDict
from typing import Any, List, Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    name: str
    phone_number: str


class UserInfoSchema(BaseModel):
    id: int = Field(description="用户ID")
    name: Optional[str] = Field(description="用户名")
    phone_number: Optional[str] = Field(description="手机号")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class ProductBaseSchema(BaseModel):
    id: int = Field(description="商品id")
    name: Optional[str] = Field(description="商品名称")
    introduction: Optional[str] = Field(description="商品简介", default="")
    price: Optional[float] = Field(description="商品价格")
    unit: Optional[float] = Field(description="商品规格")
    amount: Optional[int] = Field(description="库存数量")
    icon: Optional[str] = Field(description="商品图片")
    synchronize: Optional[bool] = Field(description="是否同步", default=False)
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class ProductSchema(ProductBaseSchema):
    product_banners: Optional[List["ProductBannerBaseSchema"]] = Field(
        description="商品banner", default=[]
    )
    product_details: Optional[List["ProductDetailBaseSchema"]] = Field(
        description="商品详情", default=[]
    )


class ProductBannerBaseSchema(BaseModel):
    id: int = Field(description="商品banner id")
    product_id: Optional[int] = Field(description="商品id")
    filename: Optional[str] = Field(description="banner图片")
    index: Optional[int] = Field(description="banner顺序")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class ProductBannerSchema(ProductBannerBaseSchema):
    product: Optional[ProductBaseSchema] = Field(description="商品信息", default={})


class ProductDetailBaseSchema(BaseModel):
    id: int = Field(description="商品详情 id")
    product_id: Optional[int] = Field(description="商品id")
    filename: Optional[str] = Field(description="详情图片")
    index: Optional[int] = Field(description="详情顺序")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class ProductDetailSchema(ProductDetailBaseSchema):
    product: Optional[ProductBaseSchema] = Field(description="商品信息", default={})


class LocationBaseSchema(BaseModel):
    id: int = Field(description="地址id")
    name: Optional[str] = Field(description="地址名称")
    type: Optional[str] = Field(description="位置类型")
    detail: Optional[str] = Field(description="位置详情")
    longitude: Optional[float] = Field(description="经度")
    latitude: Optional[float] = Field(description="纬度")
    area: Optional[float] = Field(description="面积")
    customized: Optional[str] = Field(description="是否定制")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class LocationSchema(LocationBaseSchema):
    pass


class PlanBaseSchema(BaseModel):
    id: int = Field(description="计划ID")
    location_id: Optional[int] = Field(description="基地ID")
    create_people: Optional[str] = Field(description="创建人")
    year: Optional[int] = Field(description="年份")
    batch: Optional[int] = Field(description="批次")
    total_product: Optional[int] = Field(description="总产量(L)")
    total_material: Optional[int] = Field(description="总材料(L)")
    surplus_product: Optional[int] = Field(description="剩余产量(L)")
    notices: Optional[str] = Field(description="备注")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class PlanSchema(PlanBaseSchema):
    location: Optional[LocationBaseSchema] = Field(description="基地信息", default={})


class PlanSchemaWithLocation(PlanBaseSchema):
    location: Optional[LocationBaseSchema] = Field(description="基地信息", default={})


class AddressBaseSchema(BaseModel):
    id: int = Field(description="地址id")
    client_id: Optional[int] = Field(description="客户id")
    name: Optional[str] = Field(description="客户名称")
    phone_num: Optional[str] = Field(description="手机号")
    region: Optional[str] = Field(description="地区")
    detail_address: Optional[str] = Field(description="地址")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class AddressSchema(AddressBaseSchema):
    pass


class ClientBaseSchema(BaseModel):
    id: int = Field(description="客户ID")
    type: Optional[str] = Field(description="客户类型")
    account: Optional[str] = Field(description="账号")
    name: Optional[str] = Field(description="账号名")
    phone_number: Optional[str] = Field(description="绑定手机号")
    region: Optional[str] = Field(description="地区")
    address: Optional[str] = Field(description="地址")
    signing_people: Optional[str] = Field(description="签约人")
    signing_phone: Optional[str] = Field(description="签约人手机号")
    activate: Optional[bool] = Field(description="是否激活", default=False)
    category: Optional[str] = Field(description="客户类别", default=None)
    delete_time: Optional[datetime] = Field(description="删除时间", default=None)
    is_delete: Optional[bool] = Field(description="是否删除", default=False)
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "delete_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class ClientSchema(ClientBaseSchema):
    addresses: Optional[List[AddressBaseSchema]] = Field(description="地址列表", default=[])


class PrivilegeBaseSchema(BaseModel):
    id: int = Field(description="权限ID")
    name: Optional[str] = Field(description="权限名称")
    privilege_type: Optional[str] = Field(description="权限类型")
    privilege_number: Optional[str] = Field(description="权限编号")
    description: Optional[str] = Field(description="权限描述")
    deleted: Optional[bool] = Field(description="权益是否删除")
    effective_time: Optional[datetime] = Field(description="生效时间")
    expired_time: Optional[datetime] = Field(description="过期时间")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "expired_time", "effective_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class PrivilegeSchema(PrivilegeBaseSchema):
    pass


class ClientPrivilegeRelationBaseSchema(BaseModel):
    id: int = Field(description="客户权限关系ID")
    client_id: Optional[int] = Field(description="客户ID")
    privilege_id: Optional[int] = Field(description="权限ID")
    amount: Optional[int] = Field(description="权益总数量")
    used_amount: Optional[int] = Field(description="已使用数量")
    unused_amount: Optional[int] = Field(description="未使用数量")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class ClientPrivilegeRelationSchema(ClientPrivilegeRelationBaseSchema):
    privilege: Optional[PrivilegeBaseSchema] = Field(description="权益信息", default={})
    usage: Optional[List["PrivilegeUsageBaseSchema"]] = Field(
        description="权益使用信息", default=[]
    )
    client: Optional["ClientBaseSchema"] = Field(description="客户信息", default={})


class SegmentBaseSchema(BaseModel):
    id: int = Field(description="种植ID")
    name: Optional[str] = Field(description="种植名称")
    status: Optional[str] = Field(description="种植状态")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class SegmentSchemaContainOperation(SegmentBaseSchema):
    operations: Optional[List["OperationBaseSchema"]] = Field(
        description="操作步骤信息", default=[]
    )


class SegmentSchema(SegmentBaseSchema):
    operations: Optional[List["OperationBaseSchema"]] = Field(
        description="操作步骤信息", default=[]
    )
    plant_segment_plans: Optional[List["SegmentPlanBaseSchema"]] = Field(
        description="种植环节计划信息", default=[]
    )


class SegmentPlanBaseSchema(BaseModel):
    id: int = Field(description="种植环节计划ID")
    plan_id: int = Field(description="计划ID")
    segment_id: Optional[int] = Field(description="种植ID")
    operator_id: Optional[int] = Field(description="操作人ID")
    operate_time: Optional[datetime] = Field(description="操作日期")
    remarks: Optional[str] = Field(description="备注")
    status: Optional[str] = Field(description="状态")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "operate_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S")

    model_config = ConfigDict(from_attributes=True)


class SegmentPlanSchema(SegmentPlanBaseSchema):
    segment: Optional[SegmentSchemaContainOperation] = Field(
        description="种植环节信息", default={}
    )
    plan: Optional[PlanBaseSchema] = Field(description="计划信息", default={})
    operator: Optional[ClientBaseSchema] = Field(description="操作人信息", default={})
    implementations: Optional[List["OperationImplementSchemaWithOperation"]] = Field(
        description="操作实施信息", default=[]
    )


class OperationBaseSchema(BaseModel):
    id: int = Field(description="操作ID")
    segment_id: Optional[int] = Field(description="种植ID")
    name: Optional[str] = Field(description="操作名称")
    index: Optional[int] = Field(description="操作顺序")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""


class OperationSchema(OperationBaseSchema):
    segment: Optional[SegmentBaseSchema] = Field(description="种植信息", default={})
    records: Optional[List["OperationImplementBaseSchema"]] = Field(
        description="操作记录信息", default=[]
    )


class OperationImplementBaseSchema(BaseModel):
    id: int = Field(description="操作实施ID")
    operation_id: Optional[int] = Field(description="操作ID")
    segment_plan_id: Optional[int] = Field(description="种植环节与种植计划关系ID")
    status: Optional[str] = Field(description="操作状态")
    video_filename: Optional[str] = Field(description="视频文件名")
    image_filename: Optional[str] = Field(description="图片文件名")
    operator: Optional[str] = Field(description="操作人")
    remarks: Optional[str] = Field(description="备注")
    operate_time: Optional[datetime] = Field(description="操作时间")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "operate_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class OperationImplementSchema(OperationImplementBaseSchema):
    operation: Optional[OperationBaseSchema] = Field(description="操作信息", default={})
    segment_plan: Optional[SegmentPlanBaseSchema] = Field(
        description="种植环节计划", default={}
    )


class OperationImplementSchemaWithOperation(OperationImplementBaseSchema):
    operation: Optional[OperationBaseSchema] = Field(description="操作信息", default={})


class TransportBaseSchema(BaseModel):
    id: int = Field(description="运输ID")
    plan_id: Optional[int] = Field(description="计划ID")
    operate_time: Optional[datetime] = Field(description="操作时间")
    load_place: Optional[str] = Field(description="装载地点")
    unload_place: Optional[str] = Field(description="卸载地点")
    vehicle: Optional[str] = Field(description="车辆")
    driver: Optional[str] = Field(description="司机")
    weight: Optional[float] = Field(description="重量")
    unit: Optional[str] = Field(description="单位")
    remark: Optional[str] = Field(description="备注")
    status: Optional[str] = Field(description="状态")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "operate_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class TransportSchema(TransportBaseSchema):
    plan: Optional[PlanBaseSchema] = Field(description="计划信息", default={})
    segments: Optional[List["TransportSegmentBaseSchema"]] = Field(
        description="运输环节信息", default=[]
    )
    qualities: Optional[List["QualityBaseSchema"]] = Field(
        description="质检报告信息", default=[]
    )


class TransportSegmentBaseSchema(BaseModel):
    id: int = Field(description="运输种植ID")
    transport_id: Optional[int] = Field(description="运输ID")
    type: Optional[str] = Field(description="运输环节类型")
    completed: Optional[bool] = Field(description="是否完成")
    operator: Optional[str] = Field(description="操作人")
    operate_time: Optional[datetime] = Field(description="操作时间")
    operate_place: Optional[str] = Field(description="操作地点")
    video_filename: Optional[str] = Field(description="视频文件名")
    image_filename: Optional[str] = Field(description="图片文件名")
    remarks: Optional[str] = Field(description="备注")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "operate_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class TransportSegmentSchema(TransportSegmentBaseSchema):
    transport: Optional[TransportBaseSchema] = Field(description="运输信息", default={})


class WarehouseBaseSchema(BaseModel):
    id: int = Field(description="仓库ID")
    plan_id: Optional[int] = Field(description="计划ID")
    product_id: Optional[int] = Field(description="产品ID")
    order_id: Optional[int] = Field(description="订单ID")
    amount: Optional[int] = Field(description="加工数量")
    status: Optional[str] = Field(description="状态")
    operate_time: Optional[datetime] = Field(description="计划操作时间")
    remarks: Optional[str] = Field(description="备注")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "operate_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class WarehouseSchema(WarehouseBaseSchema):
    plan: Optional["PlanBaseSchema"] = Field(description="计划信息", default={})
    product: Optional["ProductBaseSchema"] = Field(description="产品信息", default={})
    order: Optional["OrderBaseSchema"] = Field(description="订单信息", default={})
    qualities: Optional[List["QualityBaseSchema"]] = Field(
        description="质检报告信息", default=[]
    )


class OrderBaseSchema(BaseModel):
    id: int = Field(description="订单ID")
    client_id: Optional[int] = Field(description="客户ID")
    plan_id: Optional[int] = Field(description="计划ID")
    product_id: Optional[int] = Field(description="产品ID")
    camera_id: Optional[int] = Field(description="摄像头ID")
    order_number: Optional[str] = Field(description="订单编号")
    total_amount: Optional[int] = Field(description="总数量")
    status: Optional[str] = Field(description="订单状态")
    customized_area: Optional[float] = Field(description="定制面积")
    create_time: Optional[datetime] = Field(description="创建时间")
    complete_time: Optional[datetime] = Field(description="完成时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "complete_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class OrderSchema(OrderBaseSchema):
    client: Optional[ClientBaseSchema] = Field(description="客户信息", default={})
    plan: Optional[PlanSchema] = Field(description="计划信息", default={})
    product: Optional[ProductBaseSchema] = Field(description="产品信息", default={})
    camera: Optional["CameraBaseSchema"] = Field(description="摄像头信息", default={})
    logistics_plans: List["LogisticsPlanBaseSchema"] = Field(
        description="物流计划信息", default=[]
    )


class OrderSchemaWithProduct(OrderBaseSchema):
    product: Optional[ProductBaseSchema] = Field(description="产品信息", default={})


class LogisticsPlanBaseSchema(BaseModel):
    id: int = Field(description="物流计划ID")
    plan_id: Optional[int] = Field(description="计划ID")
    order_id: Optional[int] = Field(description="订单ID")
    address_id: Optional[int] = Field(description="地址ID")
    client_id: Optional[int] = Field(description="客户ID")
    amount: Optional[int] = Field(description="发货数量")
    express_number: Optional[str] = Field(description="快递单号")
    express_company: Optional[str] = Field(description="快递公司")
    express_status: Optional[str] = Field(description="快递状态")
    operate_time: Optional[datetime] = Field(description="计划操作时间")
    remarks: Optional[str] = Field(description="备注")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "operate_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class LogisticsPlanSchema(LogisticsPlanBaseSchema):
    address: Optional[AddressBaseSchema] = Field(description="地址信息", default={})
    order: Optional[OrderSchemaWithProduct] = Field(description="订单信息", default={})
    plan: Optional[PlanBaseSchema] = Field(description="计划信息", default={})
    client: Optional[ClientBaseSchema] = Field(description="客户信息", default={})


class CameraBaseSchema(BaseModel):
    id: int = Field(description="摄像头ID")
    name: Optional[str] = Field(description="摄像头名称", default=None)
    alise_name: Optional[str] = Field(description="摄像头别名", default=None)
    sn: Optional[str] = Field(description="摄像头序列号")
    status: Optional[int] = Field(description="摄像头状态")
    address: Optional[str] = Field(description="摄像头地址", default=None)
    location: Optional[str] = Field(description="摄像头位置", default=None)
    stream_url: Optional[str] = Field(description="摄像头流地址", default=None)
    token: Optional[str] = Field(description="access_token", default=None)
    expire_time: Optional[datetime] = Field(description="摄像头过期时间", default=None)
    update_time: Optional[datetime] = Field(description="更新时间")
    create_time: Optional[datetime] = Field(description="创建时间")

    @field_serializer("create_time", "update_time", "expire_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class CameraSchema(CameraBaseSchema):
    pass


class QualityBaseSchema(BaseModel):
    id: int = Field(description="质检报告ID")
    plan_id: Optional[int] = Field(description="计划ID")
    warehouse_id: Optional[int] = Field(description="仓储加工ID")
    type: Optional[str] = Field(description="质检类型")
    name: Optional[str] = Field(description="质检报告名称")
    people: Optional[str] = Field(description="质检人员", default=None)
    status: Optional[str] = Field(description="质检状态", default=None)
    report_url: Optional[str] = Field(description="质检报告地址", default=None)
    upload_time: Optional[datetime] = Field(description="上传时间")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "upload_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class QualitySchema(QualityBaseSchema):
    plan: Optional[PlanBaseSchema] = Field(description="计划信息", default={})
    warehouse: Optional[WarehouseBaseSchema] = Field(description="仓储加工信息", default={})
    transport: Optional[TransportBaseSchema] = Field(description="运输信息", default={})


class QualitySchemaWithLocation(QualityBaseSchema):
    plan: Optional[PlanSchemaWithLocation] = Field(description="计划信息", default={})
    warehouse: Optional[WarehouseBaseSchema] = Field(description="仓储加工信息", default={})
    transport: Optional[TransportBaseSchema] = Field(description="运输信息", default={})
    location: Optional[LocationBaseSchema] = Field(description="地址信息", default={})


class BannerBaseSchema(BaseModel):
    id: int = Field(description="banner id")
    name: Optional[str] = Field(description="banner标题")
    synchronize: Optional[bool] = Field(description="是否同步")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class BannerSchema(BannerBaseSchema):
    files: Optional[List["BannerFileBaseSchema"]] = Field(
        description="文件信息", default=[]
    )


class BannerFileBaseSchema(BaseModel):
    id: int = Field(description="文件ID")
    banner_id: Optional[int] = Field(description="banner ID")
    filename: Optional[str] = Field(description="文件名称")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class BannerFileSchema(BannerFileBaseSchema):
    banner: Optional[BannerBaseSchema] = Field(description="banner信息", default={})


class PrivilegeUsageBaseSchema(BaseModel):
    id: int = Field(description="权益使用ID")
    client_id: Optional[int] = Field(description="客户ID")
    privilege_id: Optional[int] = Field(description="权益ID")
    client_privilege_id: Optional[int] = Field(description="客户权益关系ID")
    used_amount: Optional[int] = Field(description="使用数量")
    used_time: Optional[datetime] = Field(description="使用时间")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "used_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class PrivilegeUsageSchema(PrivilegeUsageBaseSchema):
    pass


class AppletsOrderBaseSchema(BaseModel):
    id: int = Field(description="订单ID")
    order_number: Optional[str] = Field(description="订单编号")
    client_id: Optional[int] = Field(description="客户ID")
    address_id: Optional[int] = Field(description="地址ID")
    amounts_payable: Optional[float] = Field(description="应付金额")
    payment_amount: Optional[float] = Field(description="实付金额")
    payment_method: Optional[str] = Field(description="支付方式")
    payment_time: Optional[datetime] = Field(description="支付时间")
    status: Optional[str] = Field(description="订单状态")
    complete_time: Optional[datetime] = Field(description="完成时间")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "complete_time", "payment_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class AppletsOrderDetailBaseSchema(BaseModel):
    id: int = Field(description="订单详情ID")
    order_id: Optional[int] = Field(description="订单ID")
    product_id: Optional[int] = Field(description="产品ID")
    quantity: Optional[int] = Field(description="数量")
    price: Optional[float] = Field(description="单价")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class AppletsOrderSchema(AppletsOrderBaseSchema):
    details: Optional[List[AppletsOrderDetailBaseSchema]] = Field(description="订单详情")
    client: Optional[ClientBaseSchema] = Field(description="客户信息", default={})
    address: Optional[AddressBaseSchema] = Field(description="地址信息", default={})


class AppletsOrderDetailSchema(AppletsOrderDetailBaseSchema):
    product: Optional[ProductBaseSchema] = Field(description="产品信息", default={})
    order: Optional[AppletsOrderBaseSchema] = Field(description="订单信息", default={})


class InviteBaseSchema(BaseModel):
    id: int = Field(description="邀请ID")
    client_id: Optional[int] = Field(description="客户ID")
    client_privilege_id: Optional[int] = Field(description="客户权益关系ID")
    sponsor: Optional[str] = Field(description="邀请人")
    invite_code: Optional[str] = Field(description="邀请码")
    invite_time: Optional[datetime] = Field(description="邀请时间")
    confirmed: Optional[bool] = Field(description="是否确认")
    confirmed_time: Optional[datetime] = Field(description="确认时间")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "invite_time", "confirmed_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class InviteSchema(InviteBaseSchema):
    invited_customer: Optional[ClientBaseSchema] = Field(
        description="受邀客户信息", default={}
    )
    client_privilege: Optional[ClientPrivilegeRelationBaseSchema] = Field(
        description="客户权益关系信息", default={}
    )


class ApplyBaseSchema(BaseModel):
    id: int = Field(description="申请ID")
    client_id: Optional[int] = Field(description="客户ID")
    client_privilege_id: Optional[int] = Field(description="客户权益关系ID")
    approve: Optional[str] = Field(description="审批人")
    application_code: Optional[str] = Field(description="申请编号")
    application_time: Optional[datetime] = Field(description="申请时间")
    confirmed: Optional[bool] = Field(description="是否确认")
    confirmed_time: Optional[datetime] = Field(description="确认时间")
    agree: Optional[bool] = Field(description="是否同意")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer(
        "create_time", "update_time", "application_time", "confirmed_time"
    )
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class ApplySchema(ApplyBaseSchema):
    applicant: Optional[ClientBaseSchema] = Field(description="申请人信息", default={})
    client_privilege: Optional[ClientPrivilegeRelationBaseSchema] = Field(
        description="客户权益关系信息", default={}
    )


class MessageBaseSchema(BaseModel):
    id: int = Field(description="消息ID")
    title: Optional[str] = Field(description="标题")
    content: Optional[str] = Field(description="内容")
    status: Optional[bool] = Field(description="是否已读")
    sender: Optional[str] = Field(description="发送者")
    receiver_id: Optional[int] = Field(description="接收者ID")
    type: Optional[str] = Field(description="消息类型")
    tag: Optional[int] = Field(description="消息标签")
    details: Optional[str] = Field(description="详情")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    @field_serializer("details")
    def format_details(self, v: Any) -> Any:
        return json.loads(v) if v else {}

    model_config = ConfigDict(from_attributes=True)


class MessageSchema(MessageBaseSchema):
    receiver: Optional[ClientBaseSchema] = Field(description="接收者信息", default={})

    model_config = ConfigDict(from_attributes=True)


class SegmentFileBaseSchema(BaseModel):
    id: int = Field(description="文件ID")
    name: Optional[str] = Field(description="文件原始名称")
    segment_id: Optional[int] = Field(description="种植ID")
    filename: Optional[str] = Field(description="文件名称")
    type: Optional[str] = Field(description="文件类型")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class SegmentFileSchema(SegmentFileBaseSchema):
    segment: Optional[SegmentBaseSchema] = Field(description="种植信息", default={})

    model_config = ConfigDict(from_attributes=True)


class ProcessingSegmentBaseSchema(BaseModel):
    id: int = Field(description="加工环节ID")
    warehouse_id: Optional[int] = Field(description="仓储加工计划ID")
    type: Optional[str] = Field(description="加工环节类型")
    completed: Optional[bool] = Field(description="是否完成")
    operator: Optional[str] = Field(description="操作人")
    operate_time: Optional[datetime] = Field(description="操作时间")
    video_filename: Optional[str] = Field(description="视频文件名")
    image_filename: Optional[str] = Field(description="图片文件名")
    remarks: Optional[str] = Field(description="备注")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "operate_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class ProcessingSegmentSchema(ProcessingSegmentBaseSchema):
    warehouse: Optional[WarehouseBaseSchema] = Field(description="仓储加工信息", default={})


class TodoListBaseSchema(BaseModel):
    id: int = Field(description="待办事项ID")
    title: Optional[str] = Field(description="待办事项标题")
    content: Optional[str] = Field(description="待办事项内容")
    status: Optional[bool] = Field(description="是否已完成")
    complete_time: Optional[datetime] = Field(description="完成时间")
    sender_id: Optional[int] = Field(description="发送者(客户)ID")
    read: Optional[bool] = Field(description="是否已读")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time", "complete_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class TodoListSchema(TodoListBaseSchema):
    sender: Optional[ClientBaseSchema] = Field(description="发送者信息", default={})


class ClientUserBaseSchema(BaseModel):
    id: int = Field(description="用户ID")
    client_id: Optional[int] = Field(description="客户ID")
    name: Optional[str] = Field(description="用户名")
    hashed_passwd: Optional[str] = Field(description="密码")
    phone_number: Optional[str] = Field(description="手机号")
    avatar: Optional[str] = Field(description="头像")
    type: Optional[str] = Field(description="用户类型")
    create_time: Optional[datetime] = Field(description="创建时间")
    update_time: Optional[datetime] = Field(description="更新时间")

    @field_serializer("create_time", "update_time")
    def format_time(self, v: Any) -> Any:
        return v.strftime("%Y-%m-%d %H:%M:%S") if v else ""

    model_config = ConfigDict(from_attributes=True)


class ClientUserSchema(ClientUserBaseSchema):
    client: Optional[ClientBaseSchema] = Field(description="客户信息", default={})
