import os

PRODUCT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "upload", "product_image"
)
VIDEOS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "upload", "videos"
)
if not os.path.exists(PRODUCT_DIR):
    os.makedirs(PRODUCT_DIR)
if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = r"upload/product_image"
