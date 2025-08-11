import re

def detect_language_by_charset(text: str) -> str:
    counts = {
        "ko": len(re.findall(r"[가-힣]", text)),
        "ja": len(re.findall(r"[ぁ-ゔァ-ヴーｦ-ﾟ]", text)),  # 히라가나+가타카나
        "zh": len(re.findall(r"[一-龯]", text)),  # 한자만
        "en": len(re.findall(r"[a-zA-Z]", text)),
    }

    if all(count == 0 for count in counts.values()):
        return "unknown"

    return max(counts, key=counts.get)