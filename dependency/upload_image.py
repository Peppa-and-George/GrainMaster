import os
import uuid
from base64 import b64decode

from fastapi import HTTPException, UploadFile

from config import PRODUCT_DIR


def save_image(icon: str) -> str:
    image = icon
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
    return filename


def delete_image(icon: str) -> None:
    """
    删除图片
    :param icon: 图片名称
    """
    # 查询商品图片
    if not os.path.exists(f"{PRODUCT_DIR}/{icon}"):
        raise HTTPException(status_code=400, detail="图片不存在")
    try:
        os.remove(f"{PRODUCT_DIR}/{icon}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="删除产品图片失败, 错误信息: " + str(e))


def save_upload_image(image: UploadFile):
    """
    保存上传的图片
    :param image: 上传的图片
    :return:
    """
    image_hash = uuid.uuid4().hex
    filename = f"{image_hash}{os.path.splitext(image.filename)[-1]}"
    with open(f"{PRODUCT_DIR}/{filename}", "wb") as f:
        f.write(image.file.read())
    return filename
