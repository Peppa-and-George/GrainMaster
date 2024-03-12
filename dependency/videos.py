import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException

from config import VIDEOS_DIR


def save_video(video: UploadFile) -> str:
    """
    保存视频， 返回视频名称
    :param video: 视频对象
    :return:
    """
    # 判断文件类型
    assert video.content_type in [
        "video/mp4",
        "video/H264",
        "video/H265",
        "video/JPEG",
        "video/AV1",
    ], HTTPException(status_code=400, detail="视频格式错误, 仅支持mp4, H264, H265, JPEG, AV1")
    video_name = uuid.uuid4().hex + Path(video.filename).suffix
    with open(f"{VIDEOS_DIR}/{video_name}", "wb") as f:
        f.write(video.file.read())
    return video_name


def delete_video(video_name: str) -> None:
    """
    删除视频
    :param video_name: 视频名称
    """
    if Path(f"{VIDEOS_DIR}/{video_name}").exists():
        Path(f"{VIDEOS_DIR}/{video_name}").unlink()
