from config import IMAGES_DER, VIDEOS_DIR, REPORT_DIR, FILE_DIR
from pathlib import Path

from utils.avatar import write_avatar, exists_avatar


def init():
    """
    初始化设置
    """
    # 创建目录
    if not Path(IMAGES_DER).exists():
        Path(IMAGES_DER).mkdir(parents=True)
    if not Path(VIDEOS_DIR).exists():
        Path(VIDEOS_DIR).mkdir(parents=True)
    if not Path(REPORT_DIR).exists():
        Path(REPORT_DIR).mkdir(parents=True)
    if not Path(FILE_DIR).exists():
        Path(FILE_DIR).mkdir(parents=True)

    # 创建默认头像
    if not exists_avatar():
        write_avatar()
