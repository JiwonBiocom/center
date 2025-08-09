# 🚀 계층적 개발 모드 가이드

## 📊 WebSocket HMR 문제 현상
```
WebSocket connection to 'ws://localhost:5173/?token=...' failed
[vite] failed to connect to websocket
```

## 🎯 계층적 해결 전략

### 🛡️ 안정 모드 (팀 기본값)
```bash
npm run dev          # 기본값
npm run dev:stable   # 명시적
```
- ✅ **장점**: WebSocket 오류 완전 제거, 100% 안정적
- ⚠️ **단점**: 코드 변경마다 수동 새로고침 (`Ctrl+R`)
- 🎯 **용도**: 팀 전체 기본값, 안정적 개발 필요 시

### ⚡ 고속 모드 (UI/스타일 개발용)
```bash
npm run dev:fast          # 추천
npm run dev:experimental  # 동일
```
- ✅ **장점**: HMR 자동 새로고침, 높은 생산성
- ⚠️ **단점**: 일부 WebSocket 에러 가능성
- 🎯 **용도**: UI/스타일 집중 개발, 빠른 피드백 필요 시

### 🚫 WebSocket 완전 차단 모드
```bash
npm run dev:no-ws
```
- ✅ **장점**: WebSocket 기능 완전 제거, 브라우저 호환성 100%
- ⚠️ **단점**: HMR 없음, 폴링 방식으로 파일 변경 감지
- 🎯 **용도**: 브라우저나 네트워크에서 WebSocket을 차단하는 환경

## 🔍 자동 모니터링 도구

### 설정 변경 후 콘솔 확인
```bash
npm run dev:monitor
```
자동으로 서버 시작 + 콘솔 모니터링

### 수동 콘솔 확인
```bash
# 서버 실행 중일 때
python ../scripts/auto_console_monitor.py
python ../scripts/check_console.py http://localhost:5173
```

## 🔧 문제별 해결 가이드

### 1️⃣ React 에러: "useViewMode must be used within a ViewModeProvider"
- ✅ **해결됨**: App.tsx에 ViewModeProvider 추가 완료
- 🔄 **확인**: 브라우저 새로고침 후 에러 사라짐

### 2️⃣ WebSocket 연결 실패
```bash
# 시도 순서
npm run dev          # 기본 (HMR 비활성화)
npm run dev:fast     # HMR 활성화 시도  
npm run dev:no-ws    # 극단적 해결책
```

## 🛠️ 고급 설정

### 3. 수동 새로고침 방법
HMR이 비활성화되어 있을 때:
- **Ctrl+R** (Windows/Linux) 또는 **Cmd+R** (Mac): 일반 새로고침
- **Ctrl+Shift+R** (Windows/Linux) 또는 **Cmd+Shift+R** (Mac): 강력 새로고침

## 설정 파일 설명

### vite.config.ts (기본 - HMR 비활성화)
```typescript
hmr: false  // WebSocket HMR 완전 비활성화
```

### vite.config.alternative.ts (대안 - HMR 활성화)
```typescript
hmr: {
  port: 24678,           // 별도 포트 사용
  host: '127.0.0.1',     // IP 주소 사용
  clientPort: 24678,     // 클라이언트 포트 명시
  overlay: false         // 에러 오버레이 비활성화
}
```

## 개발 권장사항

1. **일반 개발**: `npm run dev` (HMR 비활성화) 사용
2. **빠른 개발**: `npm run dev:with-hmr` 시도
3. **WebSocket 에러 발생 시**: `npm run dev` 로 돌아가기

## 추가 정보

- WebSocket HMR 에러는 개발 환경에서만 발생하며 프로덕션에는 영향 없음
- 브라우저 확장 프로그램이나 네트워크 설정이 WebSocket을 차단할 수 있음
- 필요시 브라우저 개발자 도구에서 Network 탭을 확인하여 WebSocket 연결 상태 모니터링 가능