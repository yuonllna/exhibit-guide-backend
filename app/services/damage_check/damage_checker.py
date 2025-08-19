import numpy as np
import torch
import cv2
from app.utils.blur import detect_motion_blur
from app.utils.align import align_images
from app.utils.lpips_map import compute_lpips_mask
from PIL import Image
import io

AREA_THRESHOLD = 0.10
BLUR_THRESHOLD = 100.0
SCORE_THRESHOLD = 0.60
SCORE_THRESHOLD_BLURRY = 0.85

async def check_damage(ref_path, cur_file):
    import numpy as np
    import cv2
    from PIL import Image
    import io
    from app.utils.blur import detect_motion_blur
    from app.utils.align import align_images
    from app.utils.lpips_map import compute_lpips_mask

    AREA_THRESHOLD = 0.10
    BLUR_THRESHOLD = 100.0
    SCORE_THRESHOLD = 0.60
    SCORE_THRESHOLD_BLURRY = 0.85

    # ref_path: 서버에 존재하는 정적 이미지 파일 경로
    with open(ref_path, "rb") as f:
        ref_bytes = f.read()

    cur_bytes = await cur_file.read()

    ref = Image.open(io.BytesIO(ref_bytes)).convert('RGB').resize((256, 256))
    cur = Image.open(io.BytesIO(cur_bytes)).convert('RGB').resize((256, 256))

    ref_bgr = cv2.cvtColor(np.array(ref), cv2.COLOR_RGB2BGR)
    cur_bgr = cv2.cvtColor(np.array(cur), cv2.COLOR_RGB2BGR)

    is_blurry, blur_score = detect_motion_blur(cur_bgr, threshold=BLUR_THRESHOLD)
    score_thr = SCORE_THRESHOLD_BLURRY if is_blurry else SCORE_THRESHOLD

    aligned = align_images(ref_bgr, cur_bgr)
    if aligned is None:
        raise ValueError("이미지 정합 실패")

    score_map, mask = compute_lpips_mask(ref_bgr, aligned, score_thr)
    area_pct = 100.0 * np.sum(mask > 0) / (mask.shape[0] * mask.shape[1])
    verdict = "DAMAGED" if area_pct >= AREA_THRESHOLD else "NOT DAMAGED"

    return verdict, blur_score, area_pct
