# Exhibit Guide Backend

전시 가이드 백엔드 API 서버입니다. Gemini API를 활용하여 사용자의 손그림을 전시 작품에 합성하는 기능을 제공합니다.

## 주요 기능

- 전시회, 갤러리, 작품 관리
- 사용자 작품 생성 및 QR 코드 생성
- **Gemini API를 활용한 손그림-작품 합성**
- 이미지 업로드 및 처리

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# Google Gemini API 설정
GOOGLE_API_KEY=your_google_api_key_here

# 데이터베이스 설정
DATABASE_URL=postgresql://username:password@localhost:5432/exhibit_guide

# 서버 설정
HOST=0.0.0.0
PORT=8000
```

### 3. 서버 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API 엔드포인트

### 작품 생성 및 손그림 합성

#### 1. 손그림 업로드
```
POST /api/users/{user_id}/artwork-generation/upload-drawing
```
- `drawing_file`: 손그림 이미지 파일
- `artifact_id`: 작품 ID

#### 2. 작품 생성 (손그림 합성)
```
POST /api/users/{user_id}/artwork-generation
```
- `artifact_id`: 작품 ID
- `user_drawing_url`: 업로드된 손그림 URL
- `style_description`: 스타일 설명 (선택사항)
- `blend_mode`: 블렌드 모드 (overlay, multiply, screen)

#### 3. 생성된 작품 조회
```
GET /api/users/{user_id}/artwork-generation/{artwork_id}
```

#### 4. 업로드된 손그림 조회
```
GET /api/users/{user_id}/artwork-generation/upload-drawing/{filename}
```

## 사용 예시

### 프론트엔드에서 작품 생성하기

```javascript
// 1. 손그림 업로드
const formData = new FormData();
formData.append('drawing_file', drawingFile);
formData.append('artifact_id', artifactId);

const uploadResponse = await fetch(`/api/users/${userId}/artwork-generation/upload-drawing`, {
  method: 'POST',
  body: formData
});

const uploadResult = await uploadResponse.json();

// 2. 작품 생성 (손그림 합성)
const generationRequest = {
  artifact_id: artifactId,
  user_drawing_url: uploadResult.upload_url,
  style_description: "전통적인 한국 전통 무늬 스타일로 작품에 자연스럽게 어우러지도록",
  blend_mode: "overlay"
};

const generationResponse = await fetch(`/api/users/${userId}/artwork-generation`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(generationRequest)
});

const generationResult = await generationResponse.json();
console.log('생성된 작품:', generationResult.generated_artwork_url);
```

## 기술 스택

- **FastAPI**: 고성능 Python 웹 프레임워크
- **Google Generative AI**: Gemini API를 통한 이미지 분석 및 스타일 가이드
- **Pillow (PIL)**: 이미지 처리 및 합성
- **PostgreSQL**: 데이터베이스
- **Alembic**: 데이터베이스 마이그레이션

## 이미지 합성 방식

### 블렌드 모드

1. **Overlay**: 가장 자연스러운 합성 효과
2. **Multiply**: 어두운 톤 강조
3. **Screen**: 밝은 톤 강조

### Gemini API 활용

- 사용자 손그림의 색상, 선, 형태 분석
- 작품과의 조화를 위한 스타일 가이드 제공
- 최적의 블렌드 모드 추천

## 주의사항

- Google API 키가 필요합니다
- 이미지 파일은 PNG, JPG 등 이미지 형식만 지원
- 파일 크기는 10MB 이하 권장
- 실제 운영 환경에서는 S3 등 클라우드 스토리지 사용 권장

## 라이선스

MIT License


