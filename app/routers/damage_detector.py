from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.damage_check.damage_checker import check_damage
import os
import traceback

router = APIRouter()

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "static", "references")

@router.post("/damage-detection")
async def detect_damage(
    ref_filename: str = Form(...),  # 기존 이미지 파일 이름
    cur_image: UploadFile = File(...),  # 사용자가 업로드한 현재 이미지
):
    try:
        ref_path = os.path.join(STATIC_DIR, ref_filename)

        if not os.path.exists(ref_path):
            raise HTTPException(status_code=400, detail="지정된 레퍼런스 이미지가 존재하지 않습니다.")

        verdict, blur_score, area_pct = await check_damage(ref_path, cur_image)

        return {
            "verdict": verdict,
            "blur_score": blur_score,
            "damaged_area_percent": area_pct
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="서버 내부 오류")
