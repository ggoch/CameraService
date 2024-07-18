import numpy as np
import cv2
from ultralytics import YOLO
import json
import torch

from setting.config import get_settings
from utils.process_box import box_is_inside

settings = get_settings()

class PredictThing():
    def __init__(self):
        cuda_available = torch.cuda.is_available()
        print("CUDA available:", cuda_available)
        self.model = YOLO(settings.thing_predict_model_path)

    def detect(self, image: np.ndarray):
        crop_image = self.crop_lane_area(image)
        
        return self.predict_thing_img(crop_image,0.85)
    
    def predict_thing_img(self,img,conf=0.25,imgsz=640,e006_need_count=2):
        """
        預測指定影像中的物件，並判斷是否有指定數量的E006
        """

        try:
            results = self.model.predict(img,conf=conf,imgsz=imgsz)

            result = results[0]

            if result.masks is None:
                print(f"Not find any thing in image")
                return False,img

            area = None
            label_datas = []
            find_e006_count = 0

            for i, mask in enumerate(result.masks):
                yolojson_str = result.tojson()
                yolojson = json.loads(yolojson_str)
                yolojson = yolojson[i]

                boxs = yolojson["box"]
                label = yolojson["name"]
                conf = yolojson["confidence"]

                if label == "garbage area":
                    if area is not None and area["conf"] < conf:
                        area = {
                            "label": label,
                            "boxs":boxs,
                            "conf":conf
                        }
                        return False
                    else:
                        area = {
                            "label": label,
                            "boxs":boxs,
                            "conf":conf
                        }
                    continue



                label_datas.append({
                    "label": label,
                    "boxs":boxs
                })

            if len(label_datas) == 0 or area is None:
                print(f"Not find any thing in image")
                return False,img

            for label_data in label_datas:
                if box_is_inside(label_data["boxs"],area["boxs"]):
                    print(f"Find {label_data['label']} in image")
                    find_e006_count += 1

                if find_e006_count >= e006_need_count:
                    print(f"Find {e006_need_count} e006 in image")

                    return True,img

            print(f"Not find any thing in image")
            return False,img   
        except Exception as e:
            print(f"Error processing image {img}: {e}")
            return None,img
    
    def crop_lane_area(self,image):
        """
        裁切車道圖片中間區域。

        讓左右兩邊的車道不會影響模型的預測結果。
        """

        # 取得影像尺寸
        height, width, _ = image.shape

        # 定义中间区域的宽度比例，例如保留中间 50% 的区域
        crop_width_ratio = 0.6

        # 計算中間區域的起始和結束位置
        start_x = int((width * (1 - crop_width_ratio)) / 2)
        end_x = int(start_x + (width * crop_width_ratio))

        # 裁剪中間區域
        cropped_image = image[:, start_x:end_x]

        return cropped_image