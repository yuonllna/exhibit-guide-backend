import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.embedding.indexer import build_index

documents = [
    {"id": "art_001", "text": "모나리자는 다빈치가 그린 초상화로, 미소가 특징이다."},
    {"id": "art_002", "text": "별이 빛나는 밤은 고흐의 대표작이다. 소용돌이치는 하늘이 인상적이다."},
    {"id": "art_003", "text": "최후의 만찬은 예수와 제자들이 함께 식사하는 장면을 담고 있다."}
]
# 이 부분 나중에 수정....

if __name__ == "__main__":
    build_index(documents)