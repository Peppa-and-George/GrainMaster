import uuid
from pathlib import Path
from fastapi import UploadFile

from config import VIDEOS_DIR


def save_video(video: UploadFile) -> str:
    """
    保存视频， 返回视频名称
    :param video: 视频对象
    :return:
    """
    video_name = uuid.uuid4().hex + Path(video.filename).suffix
    with open(f"{VIDEOS_DIR}/{video_name}", "wb") as f:
        f.write(video.file.read())
    return video_name


def delete_video(video_name: str) -> None:
    """
    删除视频
    :param video_name: 视频名称
    """
    if not Path(f"{VIDEOS_DIR}/{video_name}").exists():
        return
    try:
        Path(f"{VIDEOS_DIR}/{video_name}").unlink()
    except Exception as e:
        raise Exception("删除视频失败, 错误信息: " + str(e))
