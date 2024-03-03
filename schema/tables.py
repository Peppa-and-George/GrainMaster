from datetime import datetime
from typing import List

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    Float,
    PrimaryKeyConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, Mapped

from schema.database import Base


class User(Base):
    __tablename__ = "users"  # noqa

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False, comment="用户名", name="name")
    phone_number = Column(String, nullable=False, comment="手机号", name="phone_number")
    hashed_passwd = Column(String, nullable=False, comment="密码", name="hashed_passwd")

    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, onupdate=datetime.now, default=datetime.now)


class Product(Base):
    __tablename__ = "product"  # noqa

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False, comment="产品名称", name="name")
    introduction = Column(String, comment="产品介绍", name="introduction")
    price = Column(Float, comment="价格", name="price")
    unit = Column(Float, comment="规格(L)", name="unit")
    amount = Column(Integer, comment="库存", name="amount", default=0)
    icon = Column(String, comment="产品图片路径", name="icon")
    synchronize = Column(
        Boolean,
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

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="product")
    warehouses: Mapped[List["Warehouse"]] = relationship(
        "Warehouse", back_populates="product"
    )


class Camera(Base):
    __tablename__ = "camera"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), index=True, name="name", comment="摄像头名称")
    alise_name = Column(String(128), name="alise_name", comment="设备别名")
    sn = Column(String(128), nullable=True, name="sn", comment="摄像头序列号")
    status = Column(Integer, nullable=True, name="status", comment="摄像头状态")  # 0 离线 1在线
    address = Column(String(128), name="address", comment="摄像头地址")
    location = Column(String(128), name="location", comment="摄像头位置")
    stream_url = Column(String(255), name="stream_url", comment="m3u8流地址")
    expire_time = Column(DateTime, name="expire_time", comment="过期时间")
    token = Column(Text, nullable=True, name="token", comment="access_token")

    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )

    orders: Mapped[List["Order"]] = relationship("Order", back_populates="camera")


class Privilege(Base):
    __tablename__ = "privilege"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False, comment="权益名称", name="name", unique=True)
    privilege_number = Column(
        String(32), comment="权益编号", name="privilege_number", unique=True
    )
    privilege_type = Column(String(32), comment="权益类型", name="type")
    description = Column(String(250), comment="权益描述", name="description")
    deleted = Column(Boolean, default=False, comment="权益是否删除")
    effective_time = Column(DateTime, comment="生效时间", name="effective_time")
    expired_time = Column(DateTime, comment="过期时间", name="expired_date")

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    clients: Mapped[List["ClientPrivilege"]] = relationship(
        "ClientPrivilege", back_populates="privilege"
    )

    usage: Mapped[List["PrivilegeUsage"]] = relationship(
        "PrivilegeUsage", back_populates="privilege"
    )


class Client(Base):
    __tablename__ = "client"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(32), nullable=False, comment="客户类型", name="type")

    account = Column(
        String(32), nullable=True, comment="账号", name="account", unique=True
    )
    name = Column(String(32), nullable=False, comment="账号名", name="name", unique=True)
    phone_number = Column(
        String(32), nullable=True, comment="绑定手机号", name="phone_number"
    )
    signing_people = Column(
        String(32), nullable=True, comment="签约人", name="signing_people"
    )
    signing_phone = Column(
        String(32), nullable=True, comment="签约人电话", name="signing_phone"
    )
    region = Column(String(64), nullable=True, comment="所在地区", name="region")
    address = Column(String(642), nullable=True, comment="详细地址", name="address")
    activate = Column(
        Boolean, nullable=False, default=False, comment="激活状态", name="activate"
    )
    category = Column(String(32), comment="客户类型", name="category")

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )
    delete_time = Column(DateTime, comment="删除时间", name="delete_time")
    is_deleted = Column(Boolean, comment="是否已删除", name="is_deleted")

    privileges: Mapped[List["ClientPrivilege"]] = relationship(
        "ClientPrivilege", back_populates="client"
    )
    addresses: Mapped[List["Address"]] = relationship(
        "Address",
        lazy="dynamic",
        back_populates="client",
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        lazy="dynamic",
        back_populates="client",
    )
    privilege_usages: Mapped[List["PrivilegeUsage"]] = relationship(
        "PrivilegeUsage", back_populates="client"
    )


class ClientPrivilege(Base):
    __tablename__ = "client_privilege"
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(ForeignKey("client.id", ondelete="CASCADE"), comment="客户")
    privilege_id = Column(ForeignKey("privilege.id", ondelete="CASCADE"), comment="权益")

    amount = Column(Integer, comment="权益数量", name="amount")
    used_amount = Column(Integer, comment="已使用数量", name="used_amount")
    unused_amount = Column(Integer, comment="未使用数量", name="unused_amount")

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        comment="更新时间",
        name="update_time",
        onupdate=datetime.now,
    )

    client: Mapped["Client"] = relationship(
        "Client", back_populates="privileges", foreign_keys=[client_id]
    )
    privilege: Mapped["Privilege"] = relationship(
        "Privilege", back_populates="clients", foreign_keys=[privilege_id]
    )
    usage: Mapped[List["PrivilegeUsage"]] = relationship(
        "PrivilegeUsage", back_populates="client_privilege"
    )


class PrivilegeUsage(Base):
    __tablename__ = "privilege_usage"
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(ForeignKey("client.id", ondelete="CASCADE"), comment="客户")
    privilege_id = Column(ForeignKey("privilege.id", ondelete="CASCADE"), comment="权益")
    client_privilege_id = Column(
        ForeignKey("client_privilege.id", ondelete="CASCADE"), comment="客户权益"
    )

    used_time = Column(DateTime, comment="使用时间", name="used_time", nullable=False)
    used_amount = Column(Integer, comment="使用数量", name="used_amount")

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        comment="更新时间",
        name="update_time",
        onupdate=datetime.now,
    )
    privilege: Mapped["Privilege"] = relationship(
        "Privilege", back_populates="usage", foreign_keys=[privilege_id]
    )
    client_privilege: Mapped["ClientPrivilege"] = relationship(
        "ClientPrivilege", back_populates="usage", foreign_keys=[client_privilege_id]
    )
    client: Mapped["Client"] = relationship(
        "Client", back_populates="privilege_usages", foreign_keys=[client_id]
    )


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(ForeignKey("client.id", ondelete="CASCADE"), comment="客户")

    name = Column(Text, nullable=False, comment="收货人", name="name")
    phone_num = Column(String(32), nullable=False, comment="手机号", name="phone_num")
    region = Column(Text, nullable=False, comment="地区", name="region")
    detail_address = Column(Text, nullable=False, comment="地址", name="detail_address")

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    client: Mapped["Client"] = relationship(
        "Client", back_populates="addresses", foreign_keys=[client_id]
    )
    express: Mapped["Express"] = relationship("Express", back_populates="address")
    logistics_plans: Mapped[List["LogisticsPlan"]] = relationship(
        "LogisticsPlan", back_populates="address"
    )


class Location(Base):
    __tablename__ = "location"  # noqa

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(
        String(128),
        index=True,
        unique=True,
        nullable=False,
        comment="位置名称",
        name="name",
    )
    type: str = Column(String(16), nullable=False, comment="位置类型", name="type")
    detail = Column(String(128), nullable=False, comment="位置详情", name="detail")
    longitude = Column(Float, nullable=False, comment="经度", name="longitude")
    latitude = Column(Float, nullable=False, comment="纬度", name="latitude")
    area = Column(Float, comment="面积", name="area")
    customized: str = Column(String(16), comment="是否定制", name="customized")
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    plans: Mapped[List["Plan"]] = relationship("Plan", back_populates="location")


class Plan(Base):
    __tablename__ = "plan"
    id = Column(Integer, primary_key=True, autoincrement=True)
    location_id = Column(
        ForeignKey("location.id", ondelete="CASCADE"),
        comment="基地",
        name="location_id",
    )

    create_people = Column(String(50), comment="创建人", name="create_people")
    year = Column(Integer, nullable=False, comment="年份", name="year")
    batch = Column(Integer, nullable=True, comment="批次", name="batch")
    total_material = Column(Integer, comment="总加工原料(KG)", name="total_material")
    total_product = Column(Integer, comment="成品总量(L)", name="total_product")
    surplus_product = Column(Integer, comment="剩余发货量(L)", name="surplus_product")
    notices = Column(Text, comment="备注", name="notices")

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    location: Mapped["Location"] = relationship(
        "Location",
        foreign_keys=[location_id],
        back_populates="plans",
    )
    segments: Mapped[List["PlanSegmentRelationship"]] = relationship(
        "PlanSegmentRelationship", back_populates="plan"
    )
    transports: Mapped[List["Transport"]] = relationship(
        "Transport", back_populates="plan"
    )
    warehouses: Mapped[List["Warehouse"]] = relationship(
        "Warehouse", back_populates="plan"
    )
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="plan")
    logistics_plans: Mapped[List["LogisticsPlan"]] = relationship(
        "LogisticsPlan", back_populates="plan"
    )
    qualities: Mapped[List["Quality"]] = relationship("Quality", back_populates="plan")
    traceability: Mapped["Traceability"] = relationship(
        "Traceability", back_populates="plan"
    )

    __table_args__ = (
        UniqueConstraint("year", "batch", "location_id", name="unique_plan"),
        {},
    )


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(ForeignKey("plan.id"))
    client_id = Column(ForeignKey("client.id"))
    product_id = Column(ForeignKey("product.id"))
    camera_id = Column(ForeignKey("camera.id"))
    order_number = Column(
        String(64), nullable=False, comment="订单编号", name="order_number", unique=True
    )
    customized_area = Column(Float, comment="定制面积", name="customized_area")
    total_amount = Column(Integer, comment="总数量", name="total_amount")
    status = Column(
        String(100), nullable=False, comment="状态", name="status", default="进行中"
    )
    complete_time = Column(DateTime, comment="完成时间", name="complete_time")
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    client: Mapped["Client"] = relationship(
        "Client", back_populates="orders", foreign_keys=[client_id]
    )
    plan: Mapped["Plan"] = relationship(
        "Plan", back_populates="orders", foreign_keys=[plan_id]
    )
    product: Mapped["Product"] = relationship(
        "Product", foreign_keys=[product_id], back_populates="orders"
    )
    logistics_plans: Mapped[List["LogisticsPlan"]] = relationship(
        "LogisticsPlan", back_populates="order"
    )
    camera: Mapped["Camera"] = relationship(
        "Camera", foreign_keys=[camera_id], back_populates="orders"
    )
    warehouse: Mapped["Warehouse"] = relationship("Warehouse", back_populates="order")


class Express(Base):
    __tablename__ = "express"
    number = Column(
        String(100),
        unique=True,
        nullable=False,
        comment="物流单号",
        name="number",
        primary_key=True,
    )
    address_id = Column(ForeignKey("address.id"))

    status = Column(String(100), nullable=False, comment="发货状态", name="status")
    express_num = Column(
        String(200), nullable=False, comment="物流单号", name="express_num"
    )

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    address: Mapped["Address"] = relationship(
        "Address", back_populates="express", foreign_keys=[address_id]
    )


class PlanSegmentRelationship(Base):
    __tablename__ = "plan_segment"
    plan_id = Column(
        ForeignKey("plan.id", ondelete="CASCADE"), comment="计划", primary_key=True
    )
    segment_id = Column(
        ForeignKey("segment.id", ondelete="CASCADE"), comment="种植环节", primary_key=True
    )
    operator = Column(String(50), comment="操作人员", name="operator")
    operation_date = Column(DateTime, comment="计划操作日期", name="operation_date")
    remarks = Column(Text, comment="备注", name="remarks")
    image_uri = Column(Text, comment="图片", name="image_uri")
    video_uri = Column(Text, comment="视频", name="video_uri")
    status = Column(String(50), comment="状态", name="status", default="未开始")
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )
    plan: Mapped["Plan"] = relationship(
        "Plan", back_populates="segments", foreign_keys=[plan_id]
    )
    segment: Mapped["Segment"] = relationship(
        "Segment", back_populates="plans", foreign_keys=[segment_id]
    )

    __table_args__ = (
        UniqueConstraint("plan_id", "segment_id", name="unique_plan"),
        {},
    )


class Segment(Base):
    __tablename__ = "segment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="种植环节", name="name", unique=True)

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    operations: Mapped[List["PlantOperate"]] = relationship(
        "PlantOperate", back_populates="segment"
    )
    plans: Mapped[List["PlanSegmentRelationship"]] = relationship(
        "PlanSegmentRelationship", back_populates="segment"
    )


class PlantOperate(Base):
    __tablename__ = "operate"
    id = Column(Integer, primary_key=True, autoincrement=True)
    segment_id = Column(ForeignKey("segment.id", ondelete="CASCADE"))

    name = Column(String(50), nullable=False)
    index = Column(Integer, nullable=False, comment="操作顺序", name="index")
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    segment: Mapped["Segment"] = relationship(
        "Segment", back_populates="operations", foreign_keys=[segment_id]
    )


class Transport(Base):
    __tablename__ = "transport"  # noqa 原料运输
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(ForeignKey("plan.id"))

    operate_date = Column(
        DateTime, default=datetime.now, comment="计划操作日期", name="operate_date"
    )
    loading_place = Column(String(50), comment="装车地点", name="loading_place")
    unloading_place = Column(String(50), comment="卸车地点", name="unloading_place")
    driver = Column(String(50), comment="运输人员", name="driver", default=None)
    remark = Column(Text, comment="备注", name="remark")
    status = Column(String(50), comment="状态", name="status", default="准备运输")

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    plan: Mapped["Plan"] = relationship(
        "Plan", back_populates="transports", foreign_keys=[plan_id]
    )


class Warehouse(Base):
    __tablename__ = "warehouse"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(ForeignKey("plan.id"))
    product_id = Column(ForeignKey("product.id"))
    order_id = Column(ForeignKey("order.id"))
    amount = Column(Integer, comment="数量", name="amount")
    status = Column(String(50), comment="状态", name="status", default="准备加工")

    operate_date = Column(
        DateTime, default=datetime.now, comment="计划操作日期", name="operate_date"
    )
    feeding_place = Column(String(50), comment="投料口转运", name="feeding_place")
    feeding_warehouse = Column(String(50), comment="投料仓转运地点", name="feeding_warehouse")
    feeding = Column(String(50), comment="投料", name="feeding")
    press = Column(String(50), comment="压榨", name="press")
    refine = Column(String(50), comment="精炼", name="refine")
    sorting = Column(String(50), comment="分装", name="sorting")
    warehousing = Column(String(50), comment="入库", name="Warehousing")
    product_warehousing = Column(
        String(50), comment="成品入库地点", name="product_warehousing"
    )
    notices = Column(Text, comment="备注", name="notices")

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    plan: Mapped["Plan"] = relationship(
        "Plan", back_populates="warehouses", foreign_keys=[plan_id]
    )
    order: Mapped["Order"] = relationship(
        "Order", back_populates="warehouse", foreign_keys=[order_id]
    )
    product: Mapped["Product"] = relationship(
        "Product", back_populates="warehouses", foreign_keys=[product_id]
    )
    qualities: Mapped[List["Quality"]] = relationship(
        "Quality", back_populates="warehouse"
    )


class LogisticsPlan(Base):
    __tablename__ = "logistics_plan"  # noqa 物流运输计划
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(ForeignKey("plan.id"))
    order_id = Column(ForeignKey("order.id"))
    order_number = Column(String(64), comment="订单编号", name="order_number")
    address_id = Column(ForeignKey("address.id"))
    status = Column(String(50), comment="状态", name="status", default="未开始")
    operate_date = Column(
        DateTime, default=datetime.now, comment="计划操作日期", name="operate_date"
    )
    operate_people = Column(String(50), comment="操作人员", name="operate_people")
    notices = Column(Text, comment="备注", name="notices")

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )
    plan: Mapped["Plan"] = relationship(
        "Plan", back_populates="logistics_plans", foreign_keys=[plan_id]
    )
    order: Mapped["Order"] = relationship(
        "Order", back_populates="logistics_plans", foreign_keys=[order_id]
    )
    address: Mapped["Address"] = relationship(
        "Address", back_populates="logistics_plans", foreign_keys=[address_id]
    )


class Quality(Base):
    __tablename__ = "quality"  # noqa
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(ForeignKey("plan.id", ondelete="CASCADE"), comment="计划")
    warehouse_id = Column(ForeignKey("warehouse.id", ondelete=""), comment="仓库")
    name = Column(String(50), comment="报告名称", name="name")
    people = Column(String(50), comment="上传人", name="people")
    status = Column(String(50), default="未上传", comment="上传状态", name="status")
    report = Column(Text, comment="文件路径", name="report")
    upload_time = Column(DateTime, comment="上传时间", name="upload_time")

    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    plan: Mapped["Plan"] = relationship(
        "Plan", back_populates="qualities", foreign_keys=[plan_id]
    )
    warehouse: Mapped["Warehouse"] = relationship(
        "Warehouse", back_populates="qualities", foreign_keys=[warehouse_id]
    )


class CompanyInfo(Base):
    # 公司信息
    __tablename__ = "company_info"  # noqa
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64), comment="公司名称", name="name")
    address = Column(String(256), comment="公司地址", name="address")
    phone = Column(String(64), comment="公司电话", name="phone")
    email = Column(String(64), comment="公司邮箱", name="email")
    logo = Column(String(64), comment="公司logo", name="logo")
    introduction = Column(Text, comment="公司介绍", name="introduction")
    process_flow = Column(Text, comment="工艺流程", name="process_flow")
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )


class CustomizedInformation(Base):
    # 定制信息
    __tablename__ = "customized_information"  # noqa
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    icon = Column(String(64), comment="定制图片", name="icon")
    introduction = Column(Text, comment="定制介绍", name="introduction")
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )


class Banner(Base):
    __tablename__ = "banner"  # noqa
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64), comment="名称", name="name")
    icon = Column(String(64), comment="图片", name="icon")
    introduction = Column(String(64), comment="Banner详情", name="introduction")
    status = Column(Boolean, comment="是否上架", name="status")
    synchronize = Column(
        Boolean,
        nullable=False,
        comment="是否同步",
        default=False,
        name="synchronize",
    )
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )


class Video(Base):
    __tablename__ = "video"  # noqa
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(64), comment="视频标题", name="title")
    icon = Column(String(64), comment="图片", name="icon")
    video = Column(String(64), comment="视频地址", name="video")
    introduction = Column(String(64), comment="视频详情", name="introduction")
    synchronize = Column(
        Boolean,
        nullable=False,
        comment="是否同步",
        default=False,
        name="synchronize",
    )
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )


class Traceability(Base):
    __tablename__ = "traceability"  # noqa
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    plan_id = Column(ForeignKey("plan.id", ondelete="CASCADE"), comment="计划")
    traceability_code = Column(
        String(64), comment="溯源码", name="traceability_code", unique=True
    )
    used = Column(Boolean, comment="是否使用", name="used", default=False)
    used_time = Column(DateTime, comment="使用时间", name="used_time")
    print_status = Column(Boolean, comment="打印状态", name="print_status", default=False)
    create_time = Column(
        DateTime, default=datetime.now, comment="创建时间", name="create_time"
    )
    update_time = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
        name="update_time",
    )

    plan: Mapped["Plan"] = relationship(
        "Plan", back_populates="traceability", foreign_keys=[plan_id]
    )
