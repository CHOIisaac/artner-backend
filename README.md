# Artner

아트너(Artner)는 미술 작품과 전시회 정보를 제공하고, 사용자가 자신만의 컬렉션을 만들고 도슨트 투어를 공유할 수 있는 플랫폼입니다.

## 기능

- 전시회 정보 조회
- 작품 정보 조회
- 사용자 컬렉션 생성 및 관리
- 도슨트 투어 생성 및 공유
- 작품 및 전시회 리뷰

## 설치 방법

1. 저장소 클론
   ```
   git clone https://github.com/yourusername/artner.git
   cd artner
   ```

2. 가상환경 생성 및 활성화
   ```
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 의존성 설치
   ```
   pip install -r requirements.txt
   ```

4. 환경 변수 설정
   `.env.example` 파일을 복사하여 `.env` 파일을 생성하고 필요한 값을 설정합니다.

5. 데이터베이스 마이그레이션
   ```
   python manage.py migrate
   ```

6. 개발 서버 실행
   ```
   python manage.py runserver
   ```

## API 문서

API 문서는 다음 URL에서 확인할 수 있습니다:
- OpenAPI 스키마: `/api/schema/`
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/` 