import uuid
from pathlib import Path
from fastapi import UploadFile

from config import REPORT_DIR


def save_report(file: UploadFile):
    file_name = uuid.uuid4().hex + str(Path(file.filename).suffix)
    with open(Path(REPORT_DIR) / file_name, "wb") as f:
        f.write(file.file.read())
    return file_name


def delete_report(file_name: str):
    file = Path(REPORT_DIR) / file_name
    if file.exists():
        file.unlink()
