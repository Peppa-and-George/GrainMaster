import os

PRODUCT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "upload", "images"
)
VIDEOS_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "upload", "videos"
)
REPORT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "upload", "reports"
)
FILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upload", "files")
if not os.path.exists(PRODUCT_DIR):
    os.makedirs(PRODUCT_DIR)
if not os.path.exists(VIDEOS_DIR):
    os.makedirs(VIDEOS_DIR)
if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)
if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = r"upload/images"

BASE_URL = "http://13.215.201.101:8080"
