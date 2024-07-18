import numpy as np
import cv2
from ultralytics import YOLO
import json
import torch

from setting.config import get_settings
from utils.process_box import remove_duplicate_boxes, remove_close_boxes, splice_by_label

settings = get_settings()

class PredictCarNo():
    def __init__(self):
        cuda_available = torch.cuda.is_available()
        print("CUDA available:", cuda_available)
        self.model = YOLO(settings.car_no_predict_model_path)

    def detect(self, image: np.ndarray):
        return self.predict_car_no_img(image,0.25)
    
    def predict_car_no_img(self,img,conf=0.25,imgsz=1024):
        """
        預測指定影像中的車牌號碼，如成功偵測則返回車牌號碼
        """

        try:
            results = self.model.predict(img,conf=conf,imgsz=imgsz)  # Run inference

            result_boxes = self.get_car_no_and_license_plates_by_result(results[0],self.model.names)  # Get license plates

            license_plates = []
            texts = []


            # 遍歷檢測結果，分類車牌和文字
            for box in result_boxes['detections']:
                x1, y1, x2, y2 = box['bbox']  # 獲取邊界框座標
                cls = box['class_name']  # 獲取類別

                if cls == 'license plate':  # 假設車牌類別標籤是'license_plate'
                    license_plates.append(box)
                else:  # 假設文字類別標籤是'text'
                    texts.append(box)

            # 過濾掉沒有文字的車牌
            convert_result = []

            for lp in license_plates:
                inner_texts = []
                lp_x1, lp_y1, lp_x2, lp_y2 = lp['bbox']
                has_text = False
                for txt in texts:
                    txt_x1, txt_y1, txt_x2, txt_y2 = txt['bbox']
                    # 檢查文字框是否在車牌框內
                    if txt_x1 >= lp_x1 and txt_y1 >= lp_y1 and txt_x2 <= lp_x2 and txt_y2 <= lp_y2:
                        has_text = True
                        inner_texts.append(txt)

                if has_text:
                    car_no,filtered_boxes,license_plate = self.process_result_result_car_no(inner_texts,self.model.names)
                    convert_result.append({
                    'plate': {
                        'label': lp['class_name'],
                        'confidence': lp['confidence'],
                        'bounding_box': lp['bbox']
                    },
                    'text': car_no,
                    'text_labels': list(map(lambda x: {
                        'value': x[4],
                        'top_left': ((x[0], x[1]), (x[2], x[1])),
                        'bottom_right': ((x[0], x[3]), (x[2], x[3]))
                    }, filtered_boxes))
                })

            convert_result.sort(key=lambda x: x['plate']['confidence'],reverse=True)

            for result in convert_result:
                if len(result['text']) >= 5:
                    print(f"Predict car no success: {result['text']}")
                    return True,img,result['text']
                
            print(f"Not find any car no in image")
            return False,img,None

        except Exception as e:
            print(f"Predict car no error: {e}")
            return False,img,None
        
    def get_car_no_and_license_plates_by_result(self,results,names):
        # 準備存儲檢測結果的字典
        detection_results = {
            # 'image_path': image_path,
            'detections': []
        }

        for plate_result in results:
            plate_boxes = plate_result.boxes.xyxy
            plate_class_ids = plate_result.boxes.cls
            plate_scores = plate_result.boxes.conf
            for plate_box, plate_class_id, plate_score in zip(plate_boxes, plate_class_ids, plate_scores):
                px1, py1, px2, py2 = plate_box.int().tolist()
                plate_class_id = plate_class_id.int().item()
                plate_score = plate_score.item()
                detection_results['detections'].append({
                    'bbox': [px1, py1, px2, py2],
                    'class_id': plate_class_id,
                    'class_name': names[plate_class_id],
                    'confidence': plate_score
                })

        return detection_results
    
    def process_result_result_car_no(self,results,names):
        """
        分析車牌檢測結果，去除重複文字，並返回檢測到的車牌號碼
        results: 檢測結果
        names: 模型類別名稱
        """
        detected_boxes = []
        for result in results:
            x1, y1, x2, y2 = result['bbox']
            class_id = result['class_id']
            detected_char = result['class_name']
            confidence = result['confidence']
            # if detected_char != 'license plate':
            detected_boxes.append((x1, y1, x2, y2, detected_char, confidence))

        detected_boxes = remove_duplicate_boxes(detected_boxes)

        filtered_boxes = remove_close_boxes(detected_boxes, 10)

        license_plate = splice_by_label(filtered_boxes, 'license plate')


        # 根據x1座標排序檢測到的字符
        filtered_boxes.sort(key=lambda x: x[0])

        # 拼接檢測到的字符
        detected_label = ''.join([box[4] for box in filtered_boxes])

        return detected_label,filtered_boxes,license_plate