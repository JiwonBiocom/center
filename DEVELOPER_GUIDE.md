# 개발자 가이드 - AIBIO 센터 관리 시스템

## 🚀 시작하기

### 1. 필수 문서 읽기 순서
1. **[README.md](./README.md)** - 프로젝트 개요
2. **[CLAUDE.md](./CLAUDE.md)** - 핵심 개발 원칙 (Claude Code 참조용) ⭐
3. **[CLAUDE_EXTENDED.md](./CLAUDE_EXTENDED.md)** - 상세 개발 가이드
4. **[docs/system-overview.md](./docs/system-overview.md)** - 시스템 구조
5. **[docs/database-schema.md](./docs/database-schema.md)** - 데이터베이스 종합 가이드

### 2. 개발 환경 설정
```bash
# 백엔드
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 프론트엔드
cd frontend
npm install
```

### 3. 서버 실행
```bash
# 백엔드 (터미널 1)
cd backend
python main.py

# 프론트엔드 (터미널 2)
cd frontend
npm run dev
```

## 📋 개발 프로세스

### 1. 새 기능 개발 시
1. **DB 스키마 확인**
   ```bash
   python scripts/check_schema.py --table [테이블명]
   ```
2. **기존 코드 검토**
3. **구현**
4. **테스트**
5. **문서 업데이트**

### 2. 문제 발생 시
[CLAUDE.md](./CLAUDE.md)의 "문제 발생 시 대응 프로세스" 참조

### 3. 데이터베이스 작업 시
- ⚠️ **[데이터베이스 종합 가이드](./docs/database-schema.md)** 필독
- 절대 `init_db.py` 실행 금지
- 스키마 변경 시 문서 즉시 업데이트

## 🛠 주요 기능별 문서

### 고객 관리
- [고객 관리 기능 명세](./docs/features.md#고객-관리)
- [고객 확장 기능 PRD](./docs/prd-customer-enhanced.md)

### 패키지/결제
- [결제 통합 가이드](./backend/PAYMENT_INTEGRATION_GUIDE.md)
- [가격표](./docs/PRICING_TABLE.md)

### 메시징
- [카카오 알림톡 가이드](./docs/kakao-integration-guide.md)
- [SMS 연동 가이드](./docs/sms-integration-guide.md)

### API
- [API 문서](./docs/API_DOCUMENTATION.md)
- [API 설계 가이드](./docs/customer-enhanced-api-design.md)

## 🔍 유용한 도구

### 데이터베이스 스키마 확인
```bash
# 모든 테이블 목록
python scripts/check_schema.py --list

# 특정 테이블 구조
python scripts/check_schema.py --table payments

# 특정 컬럼 존재 확인
python scripts/check_schema.py --column payments.payment_status
```

### 로그 확인
```bash
# 백엔드 로그
tail -f backend/logs/app.log

# 서버 로그
tail -f backend/server.log
```

## 📚 추가 참고 자료

### 개발 기록
- [개발 로그](./DEVELOPMENT_LOG.md)
- [에러 해결 기록](./docs/development-errors.md)
- [주차별 완료 보고서](./backend/WEEK2_COMPLETION_REPORT.md)

### 아키텍처
- [기술 스택 선택](./docs/tech-stack.md)
- [데이터 플로우](./docs/data-flow.md)
- [아키텍처 결정 기록](./docs/adr/)

## 🚨 주의사항

1. **데이터베이스**
   - `drop_all()`, `TRUNCATE`, `DROP TABLE` 사용 금지
   - 실제 데이터가 있는 경우 샘플 데이터 생성 금지
   - 스키마 변경 시 반드시 문서 업데이트

2. **코드 작성**
   - 기존 코드 스타일 따르기
   - 테스트 코드 작성
   - 주석 최소화 (코드로 설명)

3. **Git 사용**
   - 의미 있는 커밋 메시지 작성
   - `--no-verify` 사용 금지

## 💬 도움이 필요하다면

- 프로젝트 관련 문의: [README.md](./README.md) 참조
- 기술적 문제: [CLAUDE_EXTENDED.md](./CLAUDE_EXTENDED.md)의 "디버깅 및 문제 해결" 섹션
- 개발 원칙: [CLAUDE.md](./CLAUDE.md)

---

*이 가이드는 새로운 개발자가 프로젝트에 빠르게 적응할 수 있도록 작성되었습니다.*
*문서에 오류나 개선사항이 있다면 업데이트해주세요.*