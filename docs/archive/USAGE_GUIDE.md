# AIBIO 센터 관리 시스템 - 사용 가이드

## 🚀 시스템 실행 방법

### 1. 백엔드 서버 실행

터미널을 열고 다음 명령어를 실행하세요:

```bash
cd /Users/vibetj/coding/center/backend
source venv/bin/activate
uvicorn main:app --reload
```

백엔드 서버가 http://localhost:8000 에서 실행됩니다.

### 2. 프론트엔드 서버 실행

새 터미널을 열고 다음 명령어를 실행하세요:

```bash
cd /Users/vibetj/coding/center/frontend
npm run dev
```

프론트엔드가 http://localhost:5173 에서 실행됩니다.

## 🌐 접속 URL

- **프론트엔드 (관리자 페이지)**: http://localhost:5173
- **백엔드 API 문서**: http://localhost:8000/docs
- **백엔드 ReDoc**: http://localhost:8000/redoc

## 🔐 테스트 계정

로그인 페이지에서 다음 계정을 사용하세요:
- **이메일**: admin@aibio.com
- **비밀번호**: admin123

## 📋 주요 기능

### 1. 대시보드 (/)
- 전체 고객 수
- 오늘 매출
- 월 매출
- 활성 패키지 수

### 2. 고객 관리 (/customers)
- 고객 목록 조회
- 고객 검색 및 필터링
- 멤버십 상태 표시 (신규/활성/휴면/VIP)
- 개별 SMS 발송 기능
- 고객 등록 (개발 예정)
- 고객 상세보기 (개발 예정)

### 3. 유입고객 관리 (/leads)
- 잠재 고객 관리
- 상담 이력 관리
- 캠페인 관리

### 4. SMS 발송 기능
- 개별 고객 SMS 발송
- 템플릿 메시지 (생일 축하, 휴면 재활성화)
- SMS/LMS 자동 구분

## 🛠 개발 상태

### ✅ 완료된 기능
- 데이터베이스 스키마 구축
- 기본 백엔드 API 구조
- 프론트엔드 기본 구조
- 고객 관리 CRUD API
- 로그인 페이지
- 대시보드 페이지
- 고객 목록 페이지
- SMS 발송 기능 (Aligo API 연동)
- 멤버십 시스템
- 유입고객 관리
- 캠페인 관리 기능

### 🚧 개발 예정
- 실제 인증 시스템
- 서비스 이용 관리
- 결제 관리
- 패키지 관리
- 마케팅 리드 관리
- 보고서 기능
- 데이터 마이그레이션

## 🔧 문제 해결

### 서버가 실행되지 않을 때
1. Python 가상환경이 활성화되었는지 확인
2. 필요한 패키지가 설치되었는지 확인:
   ```bash
   pip install -r requirements.txt
   ```

### 프론트엔드 에러 발생 시
1. node_modules 재설치:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

### 데이터베이스 초기화
```bash
cd backend
source venv/bin/activate
python core/init_db.py
```

## 📝 개발 환경

- **Python**: 3.12+
- **Node.js**: 20 LTS
- **데이터베이스**: SQLite (개발용) / PostgreSQL (프로덕션)
- **백엔드**: FastAPI
- **프론트엔드**: React 19 + TypeScript + Vite

## 🎯 다음 단계

1. Supabase 연동 설정
2. 실제 인증 시스템 구현
3. 나머지 CRUD API 개발
4. 엑셀 데이터 마이그레이션
5. 프로덕션 배포 준비