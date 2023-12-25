import os
import uuid
from base64 import b64decode
from typing import List

from models.product_model import AddProductModel, UpdateProductModel
from fastapi import HTTPException

from config import PRODUCT_DIR
from schema.product import query_product_by_id


def save_image(params: AddProductModel) -> AddProductModel:
    image = params.icon
    # 获取图片格式
    image_type = image.split(";")[0].split("/")[-1]
    assert image_type in ["png", "jpeg"], HTTPException(
        status_code=400, detail="图片格式错误, 仅支持png和jpeg"
    )
    # 获取图片base64编码
    image_base64 = image.split(",")[-1]
    # 解码
    image_data = b64decode(image_base64)
    # 获取图片hash
    image_hash = uuid.uuid4().hex

    if image_type == "png":
        filename = f"{image_hash}.png"
    else:
        filename = f"{image_hash}.jpeg"
    # 保存图片
    with open(f"{PRODUCT_DIR}/{filename}", "wb") as f:
        f.write(image_data)
    params.icon = filename
    return params


def save_images(products: List[AddProductModel]) -> List[AddProductModel]:
    results = []
    for product in products:
        results.append(save_image(product))
    return results


def update_image(query: UpdateProductModel) -> UpdateProductModel:
    """
    删除图片
    :param query: 请求参数
    """
    # 查询商品图片
    product = query_product_by_id(query.product_id)
    if not product:
        raise HTTPException(status_code=400, detail="商品不存在")
    # 删除商品图片
    if product.icon:
        try:
            os.remove(f"{PRODUCT_DIR}/{product.icon}")
        except Exception as e:
            raise HTTPException(status_code=500, detail="更新图片失败")
    # 保存图片
    query.product = save_image(query.product)
    return query


def delete_image(product_id: int) -> int:
    """
    删除图片
    :param product_id: 商品id
    """
    # 查询商品图片
    product = query_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=400, detail="商品不存在")
    # 删除商品图片
    if product.icon:
        try:
            os.remove(f"{PRODUCT_DIR}/{product.icon}")
        except Exception as e:
            raise HTTPException(status_code=500, detail="删除产品图片失败")
    return product_id
