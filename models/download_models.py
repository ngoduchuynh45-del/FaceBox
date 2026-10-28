"""
FaceBox - Tải mô hình AI (YuNet + SFace)
Chạy: python models/download_models.py

Nguồn: OpenCV Model Zoo (https://github.com/opencv/opencv_zoo)
License: Apache 2.0
"""
import os
import urllib.request

MODELS_DIR = os.path.dirname(os.path.abspath(__file__))

MODELS = [
    {
        "filename": "face_detection_yunet_2023mar.onnx",
        "url": "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
        "description": "YuNet - Phát hiện khuôn mặt"
    },
    {
        "filename": "face_recognition_sface_2021dec.onnx",
        "url": "https://github.com/opencv/opencv_zoo/raw/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx",
        "description": "SFace - Nhận diện khuôn mặt (embedding 128 chiều)"
    }
]

for model in MODELS:
    path = os.path.join(MODELS_DIR, model["filename"])
    if os.path.exists(path):
        print(f"OK (da co): {model['description']}")
        continue
    print(f"Dang tai: {model['description']}...")
    try:
        urllib.request.urlretrieve(model["url"], path)
        print(f"Thanh cong: {model['filename']}")
    except Exception as e:
        print(f"LOI: {e}")
        print(f"URL: {model['url']}")
