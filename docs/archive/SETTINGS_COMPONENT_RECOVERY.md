# 설정 컴포넌트 복구 가이드

## 즉시 해결 방법

### 1. 브라우저에서 진단 실행
```javascript
// 개발자 도구 콘솔(F12)에서 실행
diagnoseSettings()
```

### 2. 빠른 복구 명령어
```bash
# 프론트엔드 디렉토리로 이동
cd /Users/vibetj/coding/center/frontend

# 1. 캐시 클리어 및 재설치
rm -rf node_modules/.vite
rm -rf dist
npm install

# 2. 개발 서버 재시작
npm run dev

# 3. 브라우저 캐시 클리어
# Chrome: Cmd+Shift+R (Mac) / Ctrl+Shift+R (Windows)
```

### 3. 로그인 상태 확인
```javascript
// 콘솔에서 실행
localStorage.clear()
// 그 후 다시 로그인
```

## 문제별 해결 방법

### 케이스 1: "컴포넌트가 전혀 보이지 않음"
**증상**: 설정 페이지에 아무것도 표시되지 않음

**해결**:
1. 브라우저 콘솔 확인
2. 네트워크 탭에서 401 에러 확인
3. 다시 로그인

### 케이스 2: "관리자 메뉴가 보이지 않음"
**증상**: 일반 설정만 보이고 관리자 설정이 없음

**해결**:
```sql
-- 데이터베이스에서 사용자 권한 확인
SELECT username, role FROM users WHERE username = 'admin';

-- 권한 업데이트 (필요시)
UPDATE users SET role = 'admin' WHERE username = 'admin';
```

### 케이스 3: "특정 컴포넌트만 로드 실패"
**증상**: 일부 탭을 클릭하면 에러 발생

**해결**:
```bash
# 특정 컴포넌트 확인
ls -la frontend/src/components/settings/

# Git에서 복원
git status frontend/src/components/settings/
git checkout HEAD -- frontend/src/components/settings/[문제파일명].tsx
```

## 예방 조치

### 1. 자동 상태 체크 추가
```typescript
// frontend/src/pages/Settings.tsx 상단에 추가
useEffect(() => {
  const checkInterval = setInterval(() => {
    if (!user) {
      console.warn('User data lost, attempting to reload...');
      window.location.reload();
    }
  }, 5000); // 5초마다 체크
  
  return () => clearInterval(checkInterval);
}, [user]);
```

### 2. 에러 바운더리 추가
```typescript
// frontend/src/components/ErrorBoundary.tsx
import React from 'react';

class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Settings Error:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded">
          <h3 className="text-red-800 font-semibold">컴포넌트 로드 오류</h3>
          <p className="text-red-600 text-sm mt-2">{this.state.error?.message}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded"
          >
            페이지 새로고침
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}
```

### 3. 백업 스크립트 자동화
```bash
# crontab -e 에 추가
0 */6 * * * /Users/vibetj/coding/center/backup_settings.sh
```

## 긴급 연락처 및 리소스

- Git 히스토리: `git log --oneline -- frontend/src/components/settings/`
- 마지막 정상 커밋: `git reflog | grep settings`
- 백업 위치: `/Users/vibetj/coding/center/backups/`

## 체크리스트

- [ ] 브라우저 콘솔에 에러 확인
- [ ] diagnoseSettings() 실행
- [ ] 로그인 상태 확인
- [ ] 네트워크 탭에서 API 응답 확인
- [ ] 사용자 권한(role) 확인
- [ ] 컴포넌트 파일 존재 확인
- [ ] Git 상태 확인
- [ ] 캐시 클리어 시도
- [ ] 서버 재시작 시도

이 가이드를 따라도 문제가 해결되지 않으면, 
`TROUBLESHOOTING_SETTINGS_COMPONENTS.md` 문서를 참조하세요.