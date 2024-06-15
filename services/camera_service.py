import cv2
import threading
import time
import redis
import base64
import numpy as np

class CameraService:
    def __init__(self, camera_url, redis_client, camera_id, frame_rate=10):
        self.camera_url = camera_url
        self.cap = None
        self.is_running = False
        self.thread = None
        self.status = "Disconnected"
        self.redis_client = redis_client
        self.camera_id = camera_id
        self.frame_rate = frame_rate  # 每秒缓存的帧数

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

    def _monitor_camera(self):
        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.camera_url)
                if self.cap.isOpened():
                    self.status = "Connected"
                else:
                    self.status = "Disconnected"
                    self._retry_connect()
            else:
                self._capture_frames()
            time.sleep(1 / self.frame_rate)  # 根据帧率间隔时间

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

    def _capture_frames(self):
        ret, frame = self.cap.read()
        if ret:
            _, buffer = cv2.imencode('.jpg', frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            timestamp = int(time.time() * 1000)  # 毫秒级时间戳
            frame_key = f"camera:{self.camera_id}:frame:{timestamp}"
            self.redis_client.setex(frame_key, 600, frame_base64)  # 设置10分钟过期时间

    def get_status(self):
        return self.status

    def get_frames(self):
        frame_keys = self.redis_client.keys(f"camera:{self.camera_id}:frame:*")
        frame_keys.sort()  # 按时间排序
        frames = []
        for key in frame_keys:
            frame_base64 = self.redis_client.get(key)
            if frame_base64:
                frame_data = base64.b64decode(frame_base64)
                np_frame = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
                frames.append(frame)
        return frames