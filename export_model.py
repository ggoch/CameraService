from ultralytics import YOLO
import torch

if not torch.cuda.is_available():
    raise EnvironmentError("CUDA is not available. Please check your CUDA installation.")

model = YOLO('./models/thing_model.pt')  # Load model

model.export(format="engine")

# test model 
# model = YOLO('./models/thing_model.engine', task='segment')  # Load model
# model('test_img.jpg')

# print("Model exported successfully!")

# def detect_image(image_path):
#     results = model(image_path)  # Inference

# for i in range(100):
#     # results = model('test_img.jpg')  # Inference
#     detect_image('test_img.jpg')  # Inference

