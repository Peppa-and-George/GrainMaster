from typing import Optional

from fastapi.routing import APIRouter

from fastapi import Form, UploadFile, File, status
from fastapi.responses import JSONResponse

from dependency.image import save_upload_image, delete_image
from dependency.videos import save_video, delete_video
from schema.common import transform_schema
from schema.tables import Video
from schema.database import SessionLocal

video_router = APIRouter()


@video_router.get("/get_videos", summary="获取视频信息")
def get_videos_api():
    with SessionLocal() as db:
        videos = db.query(Video).all()
        data = []
        for video in videos:
            data.append(
                {
                    "id": video.id,
                    "title": video.title,
                    "icon": video.icon,
                    "introduction": video.introduction,
                    "synchronize": video.synchronize,
                    "create_time": video.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "update_time": video.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"code": 0, "message": "success", "data": data, "total": len(data)},
        )


@video_router.post("/add_video", summary="添加视频信息")
def add_video_api(
    title: str = Form(..., title="视频标题", description="视频标题"),
    icon: UploadFile = File(..., description="封面"),
    video: UploadFile = File(..., description="视频"),
    introduction: Optional[str] = Form(None, description="简介"),
    synchronized: bool = Form(False, description="是否同步"),
):
    """
    添加视频信息
    # Form参数
    """
    icon_filename = save_upload_image(icon)
    video_filename = save_video(video)
    with SessionLocal() as session:
        video = Video(
            title=title,
            icon=icon_filename,
            video=video_filename,
            introduction=introduction,
            synchronize=synchronized,
        )
        session.add(video)
        session.flush()
        session.refresh(video)
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "code": 0,
                "message": "创建成功",
                "data": [
                    {
                        "id": video.id,
                        "title": video.title,
                        "icon": video.icon,
                        "introduction": video.introduction,
                        "synchronize": video.synchronize,
                        "create_time": video.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "update_time": video.update_time.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                ],
            },
        )


@video_router.put("/update_video", summary="更新视频信息")
def update_video_info_api(
    video_id: int = Form(..., title="视频id", description="视频id"),
    title: Optional[str] = Form(None, title="视频标题", description="视频标题"),
    icon: Optional[UploadFile] = File(None, description="封面"),
    video: Optional[UploadFile] = File(None, description="视频"),
    introduction: Optional[str] = Form(None, description="简介"),
    synchronized: Optional[bool] = Form(None, description="是否同步"),
):
    with SessionLocal() as session:
        old_video = session.query(Video).filter(Video.id == video_id).first()
        if not old_video:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"code": 1, "message": "视频不存在"},
            )
        if icon:
            delete_image(old_video.icon)
            icon_filename = save_upload_image(icon)
            old_video.icon = icon_filename
        if video:
            delete_video(old_video.video)
            video_filename = save_video(video)
            old_video.video = video_filename
        if title:
            old_video.title = title
        if introduction:
            old_video.introduction = introduction
        if synchronized is not None:
            old_video.synchronize = synchronized
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 0, "message": "更新成功"}
        )


@video_router.delete("/delete_video", summary="删除视频信息")
def delete_video_info_api(id: int = Form(..., title="视频id", description="视频id")):
    with SessionLocal() as session:
        video = session.query(Video).filter(Video.id == id).first()
        if not video:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"code": 1, "message": "视频不存在"},
            )
        delete_image(video.icon)
        delete_video(video.video)
        session.delete(video)
        session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"code": 0, "message": "删除成功"}
        )
