import cv2
import numpy as np

def align_images(ref_bgr: np.ndarray, cur_bgr: np.ndarray, min_inliers: int = 12):
    # 1) 그레이 통일 + 가벼운 대비 보정
    ref_gray = cv2.cvtColor(ref_bgr, cv2.COLOR_BGR2GRAY)
    cur_gray = cv2.cvtColor(cur_bgr, cv2.COLOR_BGR2GRAY)
    ref_gray = cv2.equalizeHist(ref_gray)
    cur_gray = cv2.equalizeHist(cur_gray)

    # 2) ORB 특징 추출(동일 알고리즘)
    orb = cv2.ORB_create(nfeatures=4000, scaleFactor=1.2, edgeThreshold=31)
    k1, d1 = orb.detectAndCompute(ref_gray, None)
    k2, d2 = orb.detectAndCompute(cur_gray, None)

    # 3) 방탄 체크
    if d1 is None or d2 is None or len(d1) == 0 or len(d2) == 0:
        return None
    if d1.dtype != d2.dtype or d1.shape[1] != d2.shape[1]:
        return None  # 규격 불일치 차단(배치 디스턴스 에러 예방)

    # 4) KNN + Lowe ratio
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    knn = bf.knnMatch(d1, d2, k=2)
    good = [m for m, n in knn if m.distance < 0.75 * n.distance]
    if len(good) < min_inliers:
        return None

    # 5) 호모그래피(RANSAC) 추정
    pts1 = np.float32([k1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    pts2 = np.float32([k2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    H, inliers = cv2.findHomography(pts2, pts1, cv2.RANSAC, 4.0)
    if H is None:
        return None
    if inliers is not None and inliers.sum() < min_inliers:
        return None

    h, w = ref_bgr.shape[:2]
    aligned = cv2.warpPerspective(cur_bgr, H, (w, h))
    return aligned
