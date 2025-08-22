import numpy as np
import cv2
from PIL import Image
import io
import traceback

from app.utils.blur import detect_motion_blur
from app.utils.align import align_images
from app.utils.lpips_map import compute_lpips_mask

AREA_THRESHOLD = 0.10          # LPIPS 마스크 기준 비율(0~1)
BLUR_THRESHOLD = 100.0
SCORE_THRESHOLD = 0.60
SCORE_THRESHOLD_BLURRY = 0.85

def _resize_keep_ar(pil_img: Image.Image, max_side: int) -> Image.Image:
    w, h = pil_img.size
    side = max(w, h)
    if side <= max_side:
        return pil_img
    scale = max_side / side
    return pil_img.resize((int(w * scale), int(h * scale)), Image.BILINEAR)

async def check_damage(ref_path, cur_file):
    # 1) 원본 바이트 로드
    with open(ref_path, "rb") as f:
        ref_bytes = f.read()
    cur_bytes = await cur_file.read()
    print(f"[START] ref={ref_path} cur_bytes={len(cur_bytes)}", flush=True)

    # 2) 원본 해상도에서 디코딩
    ref_full_bgr = cv2.imdecode(np.frombuffer(ref_bytes, np.uint8), cv2.IMREAD_COLOR)
    cur_full_bgr = cv2.imdecode(np.frombuffer(cur_bytes, np.uint8), cv2.IMREAD_COLOR)
    ref_shape = None if ref_full_bgr is None else ref_full_bgr.shape
    cur_shape = None if cur_full_bgr is None else cur_full_bgr.shape
    print(f"[DECODED] ref_shape={ref_shape} cur_shape={cur_shape}", flush=True)

    # 디코딩 실패 → DAMAGED 100
    if ref_full_bgr is None or cur_full_bgr is None:
        print(f"[WARN] decode_fail ref_ok={ref_full_bgr is not None} cur_ok={cur_full_bgr is not None} -> DAMAGED 100", flush=True)
        return "DAMAGED", 0.0, 100.0

    # 3) 블러 측정(원본 해상도)
    is_blurry, blur_score = detect_motion_blur(cur_full_bgr, threshold=BLUR_THRESHOLD)
    print(f"[BLUR] blur_score={blur_score:.2f} threshold={BLUR_THRESHOLD:.2f} is_blurry={is_blurry}", flush=True)
    if is_blurry:
        print("[POLICY] blurry -> DAMAGED 100", flush=True)
        return "DAMAGED", float(blur_score), 100.0

    # 4) 정합(최대 변 640)
    ref_rgb = Image.open(io.BytesIO(ref_bytes)).convert("RGB")
    cur_rgb = Image.open(io.BytesIO(cur_bytes)).convert("RGB")
    ref_big = _resize_keep_ar(ref_rgb, 640)
    cur_big = _resize_keep_ar(cur_rgb, 640)
    ref_big_bgr = cv2.cvtColor(np.array(ref_big), cv2.COLOR_RGB2BGR)
    cur_big_bgr = cv2.cvtColor(np.array(cur_big), cv2.COLOR_RGB2BGR)

    aligned_big = align_images(ref_big_bgr, cur_big_bgr)
    if aligned_big is None:
        print(f"[ALIGN] fail -> DAMAGED 100 (blur={blur_score:.2f})", flush=True)
        return "DAMAGED", float(blur_score), 100.0

    # 5) LPIPS(256)
    ref_256_bgr = cv2.resize(ref_full_bgr, (256, 256))
    aligned_256_bgr = cv2.resize(aligned_big, (256, 256))
    score_thr = SCORE_THRESHOLD_BLURRY if is_blurry else SCORE_THRESHOLD

    try:
        score_map, mask = compute_lpips_mask(ref_256_bgr, aligned_256_bgr, score_thr)
        area_pct = 100.0 * float(np.sum(mask > 0)) / float(mask.shape[0] * mask.shape[1])
        verdict = "DAMAGED" if (area_pct / 100.0) >= AREA_THRESHOLD else "NOT DAMAGED"
        print(f"[DONE] verdict={verdict} area={area_pct:.2f}% blur={blur_score:.2f} thr={score_thr:.2f}", flush=True)
        return verdict, float(blur_score), float(area_pct)
    except Exception as e:
        print(f"[LPIPS] error -> DAMAGED 100 ({e})", flush=True)
        traceback.print_exc()
        return "DAMAGED", float(blur_score), 100.0
