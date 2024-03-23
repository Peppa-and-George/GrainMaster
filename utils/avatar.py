from pathlib import Path
import shutil
import base64

from config import IMAGES_DER, DEFAULT_AVATAR, PROJECT_DIR, DEFAULT_AVATAR_BYTES


def write_avatar() -> bool:
    file_path = Path(PROJECT_DIR) / DEFAULT_AVATAR
    if not file_path.exists():
        with open(file_path, "wb") as f:
            content = base64.b64decode(DEFAULT_AVATAR_BYTES)
            f.write(content)
    save_path = Path(IMAGES_DER)
    if not save_path.exists():
        save_path.mkdir(parents=True)
    shutil.copy(file_path, save_path)
    return True


def exists_avatar() -> bool:
    file_path = Path(IMAGES_DER) / DEFAULT_AVATAR
    return file_path.exists()
