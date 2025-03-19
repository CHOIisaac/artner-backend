# 아트너 (Artner)

미술관, 박물관을 좋아하는 아트 러버를 위한 도슨트 서비스 앱

## 주요 기능

- 전시 및 작품 검색
- 개인화된 도슨트 생성 및 공유
- 작품 하이라이트 저장
- 컬렉션 관리
- 사용자 취향 분석

## 기술 스택

- Backend: Django, Django REST Framework, PostgreSQL
- Frontend: (별도 리포지토리)

## 설치 및 실행 방법

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
   `.env` 파일을 생성하고 다음 변수 설정:
   ```
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_NAME=artner
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. 데이터베이스 마이그레이션
   ```
   python manage.py migrate
   ```

6. 개발 서버 실행
   ```
   python manage.py runserver
   ```

## API 문서

API 문서는 `/api/docs/` 에서 확인할 수 있습니다. 