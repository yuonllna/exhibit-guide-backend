import cv2
import numpy as np

def detect_motion_blur(image, threshold=100.0):
    # 그레이스케일 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 라플라시안 연산자로 블러 감지
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # 값이 낮을수록 흐림
    is_blurry = laplacian_var < threshold
    return is_blurry, laplacian_var
