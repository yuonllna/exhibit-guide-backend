import cv2
import numpy as np

def align_images(ref_img, tgt_img, max_features=5000, good_match_percent=0.15):
    # ORB 기반 특징점 추출
    orb = cv2.ORB_create(max_features)
    keypoints1, descriptors1 = orb.detectAndCompute(ref_img, None)
    keypoints2, descriptors2 = orb.detectAndCompute(tgt_img, None)

    # 브루트포스 매칭 (Hamming 거리)
    matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = matcher.match(descriptors1, descriptors2)

    # 좋은 매칭 필터링
    matches = sorted(matches, key=lambda x: x.distance)
    num_good_matches = int(len(matches) * good_match_percent)
    matches = matches[:num_good_matches]

    if len(matches) < 4:
        return None  # 정합 실패

    # 매칭된 점 추출
    points1 = np.float32([keypoints1[m.queryIdx].pt for m in matches])
    points2 = np.float32([keypoints2[m.trainIdx].pt for m in matches])

    # 호모그래피 계산
    h, mask = cv2.findHomography(points2, points1, cv2.RANSAC)

    if h is None:
        return None

    # 변환 적용
    height, width = ref_img.shape[:2]
    aligned_img = cv2.warpPerspective(tgt_img, h, (width, height))
    return aligned_img
