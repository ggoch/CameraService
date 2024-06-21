

from fastapi import APIRouter, HTTPException, Request, Response, WebSocket

import datetime
import cv2
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse 

import os

from services.camera_html import html, hls_html
from services.camera_service import get_camera_services, frame_rate, process_frame

router = APIRouter(
    tags=["cameras"],
    prefix="/api",
    # dependencies=[Depends(test_verify_token)]
)

live_router = APIRouter(
    tags=["cameras"],
    prefix="/live",
)

@live_router.get("/1")
async def get():
    return HTMLResponse(hls_html)

@live_router.get("/2")
async def get():
    return HTMLResponse(html)

@live_router.websocket("/ws/{camera_index}")
async def websocket_endpoint(websocket: WebSocket, camera_index: int):
    await websocket.accept()
    async for frame in process_frame(camera_index):
        await websocket.send_text(frame)

@live_router.get("/hls/{camera_index}/{file_path:path}")
async def hls_stream(camera_index:int,file_path: str, request: Request,response: Response):
    file_path = f"./camera_caches/hls/{camera_index}/{file_path}"
    if not os.path.exists(file_path):
        return Response(status_code=404)
    response.headers["Content-Type"] = "application/x-mpegURL"
    return FileResponse(file_path)

# @live_router.get("/hls/{camera_index}/{file_path:path}")
# async def hls_stream(camera_index: int, file_path: str, request: Request):
#     file_path = f"./camera_caches/hls/{camera_index}/{file_path}"
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not found")

#     return StreamingResponse(
#         iter_file(file_path),
#         media_type='application/vnd.apple.mpegurl' if file_path.endswith(".m3u8") else 'video/MP2T'
#     )

# async def iter_file(file_path: str):
#     with open(file_path, mode="rb") as file_like:
#         while True:
#             chunk = file_like.read(1024*1024)  # 每次读取 1MB
#             if not chunk:
#                 break
#             yield chunk

@router.post("/save_video/{camera_index}")
async def save_video(camera_index: int):
    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"video_{camera_index}_{now}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(filename, fourcc, frame_rate, (640, 480))

    frames = get_camera_services()[camera_index].get_frames()
    for frame in frames:
        out.write(frame)

    out.release()
    return {"message": "Video saved", "filename": filename}

@router.get("/camera_status")
async def camera_status():
    statuses = {f"camera_{i}": service.get_status() for i, service in enumerate(get_camera_services())}
    return statuses