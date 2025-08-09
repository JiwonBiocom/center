# Railway에서 Vercel + Supabase로 마이그레이션 가능성 분석

> 작성일: 2025-06-09  
> 작성자: Claude Code  
> 프로젝트: AIBIO 센터 관리 시스템

## 📋 개요

이 문서는 현재 Railway에서 호스팅 중인 FastAPI 백엔드를 Vercel과 Supabase만으로 마이그레이션할 수 있는지에 대한 기술적 검토 결과입니다.

## 🏗️ 현재 아키텍처

### 프로젝트 구성
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Database   │
│   (React)   │     │  (FastAPI)  │     │ (PostgreSQL)│
│   Vercel    │     │   Railway   │     │  Supabase   │
└─────────────┘     └─────────────┘     └─────────────┘
```

### 기술 스택 상세
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS
- **Backend**: FastAPI (Python 3.12), SQLAlchemy, Pydantic
- **Database**: PostgreSQL 17 (Supabase 제공)
- **배포**: Frontend (Vercel), Backend (Railway)

## 🔍 상세 분석

### 1. Backend 요구사항 분석

#### 핵심 기능
- **API 엔드포인트**: 35개 이상의 RESTful API
- **인증 시스템**: JWT 기반 토큰 관리
- **백그라운드 작업**:
  - 회원 등급 자동 업데이트 (24시간 주기)
  - 패키지 만료 알림
  - 서비스 이용 통계 집계
- **외부 연동**:
  - Kakao 알림톡 API
  - Aligo SMS API
- **파일 처리**: Excel 파일 가져오기/내보내기

#### 기술적 요구사항
- ASGI 서버 (uvicorn) 필요
- 장기 실행 프로세스
- 상태 유지 (세션, 캐시)
- 스케줄러 실행 환경

### 2. Vercel 제한사항

| 항목 | 제한사항 | 영향도 |
|------|----------|--------|
| **런타임** | Node.js 우선 지원 | Python 지원 제한적 |
| **실행 시간** | 10초 (무료), 60초 (Pro) | 대용량 처리 불가 |
| **메모리** | 1024MB (무료), 3008MB (Pro) | 복잡한 연산 제한 |
| **파일 시스템** | 읽기 전용 | 임시 파일 처리 어려움 |
| **백그라운드 작업** | 지원 안 함 | 스케줄러 사용 불가 |
| **WebSocket** | 지원 안 함 | 실시간 기능 제한 |

### 3. Supabase Edge Functions 검토

#### 장점
- PostgreSQL과 직접 통합
- 자동 스케일링
- 글로벌 배포

#### 단점
- **TypeScript/JavaScript만 지원** (Python 불가)
- Deno 런타임 사용
- 실행 시간 제한 (최대 150초)
- 전체 코드베이스 재작성 필요

## ❌ 마이그레이션 불가 판정

### 주요 불가 사유

1. **언어 호환성 문제**
   - FastAPI는 Python 전용 프레임워크
   - Vercel Serverless Functions는 Python 지원 미흡
   - Supabase Edge Functions는 TypeScript만 지원

2. **아키텍처 불일치**
   - FastAPI는 장기 실행 서버 모델
   - Vercel/Supabase는 Serverless 모델
   - 백그라운드 작업 실행 환경 부재

3. **기능적 제약**
   - 복잡한 비즈니스 로직 처리 어려움
   - 스케줄러 기능 구현 불가
   - 대용량 파일 처리 제한

## 🎯 권장 솔루션

### 1. 현재 구조 유지 (단기 권장) ✅
```yaml
Frontend: Vercel (현행 유지)
Backend: Railway/Render/Fly.io
Database: Supabase PostgreSQL
```

**장점**:
- 즉시 적용 가능
- 추가 개발 불필요
- 안정적인 운영 가능

### 2. 점진적 마이그레이션 (장기 검토)
```yaml
Phase 1: 간단한 CRUD → Supabase Edge Functions
Phase 2: 인증 시스템 → Supabase Auth
Phase 3: 복잡한 로직 → 별도 마이크로서비스
```

**예상 작업량**: 3-6개월

### 3. 대체 호스팅 서비스 비교

| 서비스 | 장점 | 단점 | 월 비용 |
|--------|------|------|---------|
| **Railway** | 간편한 배포, Python 완벽 지원 | 비용 상승 가능성 | $5-20 |
| **Render** | 무료 플랜, 자동 배포 | 무료 플랜 느림 | $0-7 |
| **Fly.io** | 글로벌 배포, 빠른 속도 | 설정 복잡 | $5-15 |
| **DigitalOcean** | 안정적, 다양한 옵션 | 관리 필요 | $5-20 |

## 📊 비용 분석

### 현재 구조 (Railway + Vercel + Supabase)
- Railway: ~$10/월
- Vercel: 무료 (Frontend만)
- Supabase: 무료 (소규모)
- **총: ~$10/월**

### Vercel + Supabase만 사용 시
- 전체 재개발 비용: 500+ 시간
- Vercel Pro 필요: $20/월
- Supabase 추가 기능: $25/월
- **총: ~$45/월 + 개발 비용**

## 🔄 마이그레이션 로드맵 (필요 시)

### Phase 1: 준비 (1개월)
- [ ] 현재 API 문서화 완료
- [ ] 테스트 커버리지 확보
- [ ] 비즈니스 로직 분리

### Phase 2: 부분 마이그레이션 (2-3개월)
- [ ] 간단한 CRUD API 이전
- [ ] Supabase Auth 통합
- [ ] RLS (Row Level Security) 설정

### Phase 3: 완전 마이그레이션 (2-3개월)
- [ ] 복잡한 로직 재구현
- [ ] 스케줄러 대체 구현
- [ ] 성능 최적화

## 📌 결론

**Railway 없이 Vercel + Supabase만으로는 현재 시스템을 배포할 수 없습니다.**

### 핵심 이유
1. FastAPI (Python)와 Serverless 환경의 근본적인 불일치
2. 백그라운드 작업과 스케줄러 실행 불가
3. 전체 백엔드를 TypeScript로 재작성해야 하는 막대한 작업량

### 최종 권장사항
- **즉시**: 현재 구조 유지 (Railway 계속 사용)
- **중기**: Railway 대안 검토 (Render, Fly.io)
- **장기**: 필요시 아키텍처 재설계 고려

---

*이 문서는 2025년 6월 9일 기준으로 작성되었습니다.*
*기술 스택이나 서비스 정책 변경 시 재검토가 필요합니다.*