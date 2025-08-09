# 설정 컴포넌트 사라짐 문제 해결 가이드

## 문제 설명
설정 페이지의 컴포넌트들이 화면에 표시되지 않는 문제가 반복적으로 발생하고 있습니다.

## 가능한 원인들

### 1. **인증/권한 문제**
- **증상**: 로그인은 되었지만 user 객체가 null이거나 role이 올바르지 않음
- **확인 방법**:
  ```javascript
  // 브라우저 콘솔에서 실행
  console.log(localStorage.getItem('access_token'))
  console.log(localStorage.getItem('user'))
  ```
- **해결 방법**:
  - 로그아웃 후 다시 로그인
  - 토큰이 만료되었다면 새로 로그인
  - user 정보가 없다면 AuthContext의 loadUser 함수 확인

### 2. **컴포넌트 파일 내용 문제**
- **증상**: 파일은 존재하지만 내용이 비어있거나 export가 잘못됨
- **확인 방법**:
  ```bash
  # 각 컴포넌트 파일의 크기 확인
  ls -la frontend/src/components/settings/
  
  # 파일 내용 확인
  head -20 frontend/src/components/settings/ProfileSettings.tsx
  ```
- **해결 방법**:
  - 백업에서 복원
  - Git 히스토리에서 복원: `git checkout HEAD -- frontend/src/components/settings/`

### 3. **빌드/번들링 문제**
- **증상**: 개발 서버는 정상이지만 프로덕션 빌드에서 문제 발생
- **확인 방법**:
  ```bash
  # 빌드 에러 확인
  cd frontend && npm run build
  
  # 개발 서버 재시작
  npm run dev
  ```
- **해결 방법**:
  - node_modules 삭제 후 재설치: `rm -rf node_modules && npm install`
  - 캐시 클리어: `npm cache clean --force`

### 4. **API 응답 문제**
- **증상**: API가 에러를 반환하거나 응답이 없음
- **확인 방법**:
  - 브라우저 개발자 도구 > Network 탭에서 API 호출 확인
  - 특히 `/api/v1/users/me`, `/api/v1/settings/` 등의 응답 확인
- **해결 방법**:
  - 백엔드 서버 재시작
  - 데이터베이스 연결 확인
  - API 엔드포인트 디버깅

### 5. **React 렌더링 문제**
- **증상**: 컴포넌트가 조건부 렌더링에서 제외됨
- **확인 방법**:
  - React Developer Tools 설치 후 컴포넌트 트리 확인
  - Settings 페이지의 activeTab 상태 확인
- **해결 방법**:
  - 컴포넌트의 조건부 렌더링 로직 검토
  - isAdmin 변수가 올바른지 확인

## 예방 방법

### 1. **Git 관리 강화**
```bash
# 작업 전 상태 확인
git status

# 변경사항 확인
git diff frontend/src/components/settings/

# 안전한 커밋
git add -p  # 변경사항을 하나씩 확인하며 추가
```

### 2. **자동 백업 설정**
```bash
# 일일 백업 스크립트 생성
cat > backup_settings.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/settings_$DATE"
mkdir -p $BACKUP_DIR
cp -r frontend/src/components/settings/ $BACKUP_DIR/
echo "Settings components backed up to $BACKUP_DIR"
EOF

chmod +x backup_settings.sh
```

### 3. **컴포넌트 상태 검증 스크립트**
```javascript
// frontend/src/utils/validateSettings.js
export function validateSettingsComponents() {
  const requiredComponents = [
    'ProfileSettings',
    'PasswordSettings',
    'UserManagement',
    'SystemSettings',
    'ServiceTypeManagement',
    'NotificationSettings',
    'BackupSettings',
    'ReportSettings',
    'KakaoSettings'
  ];
  
  const missingComponents = [];
  
  requiredComponents.forEach(comp => {
    try {
      const module = require(`../components/settings/${comp}`);
      if (!module.default) {
        missingComponents.push(comp);
      }
    } catch (error) {
      missingComponents.push(comp);
    }
  });
  
  if (missingComponents.length > 0) {
    console.error('Missing components:', missingComponents);
    return false;
  }
  
  return true;
}
```

### 4. **모니터링 설정**
```javascript
// Settings.tsx에 추가
import { useEffect } from 'react';

useEffect(() => {
  // 컴포넌트 로딩 상태 모니터링
  console.log('Settings page loaded', {
    user,
    isAdmin,
    activeTab,
    tabsCount: tabs.length
  });
  
  // 렌더링된 컨텐츠 확인
  const content = renderContent();
  if (!content) {
    console.error('No content rendered for tab:', activeTab);
  }
}, [activeTab, user, isAdmin]);
```

## 즉시 복구 방법

### 1. **빠른 복구 명령어**
```bash
# Git에서 설정 컴포넌트 복원
cd /Users/vibetj/coding/center
git checkout HEAD -- frontend/src/components/settings/

# 또는 특정 커밋에서 복원
git log --oneline -- frontend/src/components/settings/
git checkout <commit-hash> -- frontend/src/components/settings/
```

### 2. **컴포넌트 재생성**
만약 파일이 완전히 손실되었다면, 이 문서의 하단에 있는 백업 코드를 사용하여 복원할 수 있습니다.

## 디버깅 체크리스트

- [ ] 브라우저 콘솔에 에러가 있는가?
- [ ] 네트워크 탭에서 401/403 에러가 발생하는가?
- [ ] localStorage에 user 정보가 있는가?
- [ ] 컴포넌트 파일들이 실제로 존재하는가?
- [ ] 파일 크기가 0이 아닌가?
- [ ] React Developer Tools에서 컴포넌트가 보이는가?
- [ ] activeTab 상태가 올바른가?
- [ ] isAdmin 값이 올바른가?

## 로그 수집
문제가 발생하면 다음 정보를 수집하세요:

```javascript
// 브라우저 콘솔에서 실행
const debugInfo = {
  user: JSON.parse(localStorage.getItem('user')),
  token: localStorage.getItem('access_token'),
  url: window.location.href,
  userAgent: navigator.userAgent,
  timestamp: new Date().toISOString()
};
console.log('Debug Info:', debugInfo);
```

## 문제 재발 방지

1. **정기적인 백업**: 매일 설정 컴포넌트 백업
2. **Git 커밋 전 확인**: 설정 관련 파일 변경 시 신중히 검토
3. **테스트 자동화**: 설정 페이지 접근 테스트 추가
4. **모니터링**: 설정 페이지 로딩 실패 시 알림

이 문서를 참고하여 문제를 해결하고, 재발을 방지하시기 바랍니다.