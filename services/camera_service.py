import cv2
import threading
import time
import redis
import base64
import numpy as np
import asyncio
import os
import subprocess

class CameraService:
    def __init__(self, camera_url, redis_client, camera_id, frame_rate=1,max_frames=500,storage_path='./camera_caches/storage',hls_path='./camera_caches/hls'):
        self.camera_url = camera_url
        self.cap = None
        self.is_running = False
        self.thread = None
        self.status = "Disconnected"
        self.redis_client = redis_client
        self.camera_id = camera_id
        self.frame_rate = frame_rate  # 每秒快取的幀數
        self.storage_path = os.path.join(storage_path, str(camera_id))
        self.max_frames = max_frames  # 最大快取幀數
        self.hls_path = os.path.join(hls_path,str(camera_id))
        self._check_and_create_storage_path()

        self.ffmpeg_process = None

    def _check_and_create_storage_path(self):
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
            print(f"Created storage directory at: {self.storage_path}")
        else:
            print(f"Storage directory already exists at: {self.storage_path}")

        if not os.path.exists(self.hls_path):
            os.makedirs(self.hls_path)
            print(f"Created HLS directory at: {self.hls_path}")
        else:
            print(f"HLS directory already exists at: {self.hls_path}")

    def start(self):
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor_camera)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread is not None:
            self.thread.join()
        if self.cap is not None:
            self.cap.release()

        self.ffmpeg_process.stdin.close()
        self.ffmpeg_process.wait()

    def _monitor_camera(self):
        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.camera_url)
                if self.cap.isOpened():
                    self.status = "Connected"
                    # FFmpeg 指令，用於將視訊串流轉換為 HLS
                    ffmpeg_path = r"C:\Program Files\FFMPEG\bin\ffmpeg.exe"
                    ffmpeg_command = [
                        ffmpeg_path,
                        # 'ffmpeg',
                        '-y',  # 覆盖输出文件
                        '-f', 'rawvideo',
                        '-vcodec', 'rawvideo',
                        '-pix_fmt', 'bgr24',
                        '-s', f'{int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}',  # 视频帧尺寸
                        '-r', str(self.cap.get(cv2.CAP_PROP_FPS)),  # 帧率
                        '-i', '-',  # 从管道输入
                        '-c:v', 'libx264',
                        '-tune', 'zerolatency',  # 低延迟模式
                        '-preset', 'ultrafast',
                        '-vsync', '1',
                        '-hls_time', '1',
                        '-hls_list_size', '20',
                        '-hls_flags', 'delete_segments+append_list',
                        '-hls_delete_threshold', '2',
                        '-f', 'hls',
                        '-force_key_frames', 'expr:gte(t,n_forced*1)',  # 强制每秒创建一个关键帧
                        os.path.join(self.hls_path, f'camera_{self.camera_id}.m3u8')  # 输出 HLS 文件路径
                    ]
                    self.ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
                else:
                    self.status = "Disconnected"
                    self._retry_connect()
            else:
                self._capture_frames()
            # time.sleep(1 / self.frame_rate)  # 根据帧率间隔时间

    def _retry_connect(self):
        """尝试重连摄像机"""
        retry_delay = 2  # 重连间隔时间
        max_retries = 5  # 最大重连次数
        retries = 0
        while retries < max_retries and not self.cap.isOpened():
            time.sleep(retry_delay)
            self.cap = cv2.VideoCapture(self.camera_url)
            retries += 1
        if self.cap.isOpened():
            self.status = "Connected"
        else:
            self.status = "Disconnected"

    def write_time_text(self,frame):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        
        return frame

    # def _capture_frames(self):
    #     ret, frame = self.cap.read()
    #     if ret:
    #         _, buffer = cv2.imencode('.jpg', frame)
    #         frame_base64 = base64.b64encode(buffer).decode('utf-8')
    #         timestamp = int(time.time() * 1000)  # 毫秒级时间戳
    #         frame_key = f"camera:{self.camera_id}:frame:{timestamp}"
    #         self.redis_client.setex(frame_key, 600, frame_base64)  # 设置10分钟过期时间

    def _capture_frames(self):
        ret, frame = self.cap.read()
        if ret:
            frame = self.write_time_text(frame)
            _, buffer = cv2.imencode('.jpg', frame)
            timestamp = int(time.time() * 1000)  # 毫秒级时间戳
            # frame_key = f"camera:{self.camera_id}:frame:{timestamp}"
            frame_key = f"camera:{self.camera_id}:frames"
            # self.redis_client.setex(frame_key, 600, buffer.tobytes())  # 设置10分钟过期时间
            self.redis_client.zadd(frame_key, {buffer.tobytes(): timestamp})
            # 删除有序集合中除了最新的 max_frames 个元素之外的所有元素
            self.redis_client.zremrangebyrank(frame_key, 0, -(self.max_frames + 1))

            try:
                self.ffmpeg_process.stdin.write(frame.tobytes())
            except Exception as e:
                print(f"Error writing to ffmpeg stdin: {e}")

    # def _capture_frames(self):
    #     ret, frame = self.cap.read()
    #     if ret:
    #         timestamp = int(time.time() * 1000)  # 毫秒级时间戳
    #         frame_filename = f"camera_{self.camera_id}_{timestamp}.jpg"
    #         frame_path = os.path.join(self.storage_path, frame_filename)
    #         cv2.imwrite(frame_path, frame)
    #         frame_key = f"camera:{self.camera_id}:frame:{timestamp}"
    #         self.redis_client.setex(frame_key, 600, frame_path)  # 设置10分钟过期时间

    def get_status(self):
        return self.status

    # def get_frames(self):
    #     frame_keys = self.redis_client.keys(f"camera:{self.camera_id}:frame:*")
    #     frame_keys.sort()  # 按时间排序
    #     frames = []
    #     for key in frame_keys:
    #         frame_base64 = self.redis_client.get(key)
    #         if frame_base64:
    #             frame_data = base64.b64decode(frame_base64)
    #             np_frame = np.frombuffer(frame_data, np.uint8)
    #             frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
    #             frames.append(frame)
    #     return frames

    def get_frames(self):
        frame_keys = self.redis_client.keys(f"camera:{self.camera_id}:frame:*")
        frame_keys.sort()
        frames = []
        for key in frame_keys:
            frame_data = self.redis_client.get(key)
            if frame_data:
                np_frame = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
                frames.append(frame)
        return frames
    
    def get_latest_frame(self):
        frame_key = f"camera:{self.camera_id}:frames"
        latest_frame = self.redis_client.zrange(frame_key, -1, -1,withscores=False)  # 获取最新的帧
        if latest_frame:
            frame_data = latest_frame[0]
            np_frame = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
            return frame
        return None

    # def get_frames(self):
    #     frame_keys = self.redis_client.keys(f"camera:{self.camera_id}:frame:*")
    #     frame_keys.sort()
    #     frames = []
    #     for key in frame_keys:
    #         frame_path = self.redis_client.get(key)
    #         if frame_path:
    #             frame = cv2.imread(frame_path)
    #             frames.append(frame)
    #     return frames


camera_urls = [f'rtsp://admin:dh123456@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0' for i in range(5)]  # 使用模拟的 RTSP 流
frame_rate = 10  # 每秒10幀
_camera_services:list[CameraService] = None

async def init_camera_service(redis_client):
    global _camera_services
    # storage_path = "./camera_caches"
    _camera_services = [CameraService(url, redis_client, i, frame_rate) for i, url in enumerate(camera_urls)]
    
    for service in _camera_services:
        service.start()


async def process_frame(camera_index):
        global _camera_services
        while True:
            frame = _camera_services[camera_index].get_latest_frame()
            # if frames:
            #     frame = frames[0]

            if frame is not None:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ret, buffer = cv2.imencode('.jpg', gray)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                yield frame_base64
            await asyncio.sleep(1 / frame_rate)  # 每秒傳輸frame_rate幀

def get_camera_services():
    global _camera_services    
    return _camera_services
