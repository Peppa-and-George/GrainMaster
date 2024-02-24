import os
import uuid

from fastapi import UploadFile, HTTPException

from config import FILE_DIR


def save_upload_file(file: UploadFile) -> str:
    image_hash = uuid.uuid4().hex
    filename = f"{image_hash}{os.path.splitext(file.filename)[-1]}"
    with open(f"{FILE_DIR}/{filename}", "wb") as f:
        f.write(file.file.read())
    return filename


def delete_file(file: str) -> None:
    """
    删除图片
    :param file: 文件名称
    """
    if os.path.exists(f"{FILE_DIR}/{file}"):
        os.remove(f"{FILE_DIR}/{file}")
