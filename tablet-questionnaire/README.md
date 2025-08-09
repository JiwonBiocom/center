# AIBIO 태블릿 문진 시스템

## 개요
안드로이드 태블릿용 인터랙티브 문진 애플리케이션

## 기술 스택
- **Frontend**: React Native + TypeScript
- **State Management**: Redux Toolkit + RTK Query
- **UI Components**: React Native Paper (Material Design)
- **Navigation**: React Navigation v6
- **Storage**: AsyncStorage + SQLite (오프라인)
- **Backend**: FastAPI (기존 시스템 활용)

## 프로젝트 구조
```
tablet-questionnaire/
├── src/
│   ├── components/     # 재사용 가능한 UI 컴포넌트
│   ├── screens/       # 화면 컴포넌트
│   ├── navigation/    # 네비게이션 설정
│   ├── store/         # Redux 스토어
│   ├── services/      # API 서비스
│   ├── types/         # TypeScript 타입 정의
│   ├── utils/         # 유틸리티 함수
│   └── assets/        # 이미지, 폰트 등
├── android/           # 안드로이드 네이티브 코드
└── ios/              # iOS 네이티브 코드 (옵션)
```

## 주요 기능
1. **필수 문진 (5-7분)**
   - 기본 정보 수집
   - 핵심 건강 평가
   - 목표 설정

2. **선택적 심화 문진**
   - 조건부 활성화
   - 스트레스/정신건강
   - 소화기 건강
   - 호르몬/대사
   - 근골격계

3. **오프라인 지원**
   - 로컬 데이터 저장
   - 자동 동기화
   - 중단 후 이어하기

4. **UI/UX 특징**
   - 진행률 표시
   - 시각적 피드백
   - 태블릿 최적화 레이아웃