# Frontend 개발 가이드

> 📌 이 문서는 프론트엔드 특화 규칙입니다.
> 글로벌 개발 원칙은 [글로벌 CLAUDE.md](../../CLAUDE.md)를 먼저 참조하세요.
> 프로젝트 원칙은 [루트 CLAUDE.md](../CLAUDE.md)를 참조하세요.
> 적용 우선순위: 글로벌 → 프로젝트 → 프론트엔드 규칙

## 프론트엔드 핵심 규칙

### 1. React/TypeScript 규칙
- 함수형 컴포넌트 사용 (클래스 컴포넌트 금지)
- TypeScript strict mode 활성화
- any 타입 사용 금지

### 2. 컴포넌트 구조
```tsx
// ✅ 좋은 예
interface CustomerModalProps {
  customerId: number;
  isOpen: boolean;
  onClose: () => void;
}

export default function CustomerModal({
  customerId,
  isOpen,
  onClose
}: CustomerModalProps) {
  // hooks는 최상단에
  const [loading, setLoading] = useState(false);
  const queryClient = useQueryClient();

  // 조건부 렌더링은 early return
  if (!isOpen) return null;

  return (
    // JSX
  );
}
```

### 3. 상태 관리
- React Query로 서버 상태 관리
- useState로 로컬 상태 관리
- 전역 상태는 Context API 사용

### 4. API 호출
```typescript
// lib/api.ts 사용
const response = await api.get(`/customers/${customerId}`);

// 절대 직접 fetch 사용 금지
// ❌ fetch('http://localhost:8000/api/v1/...')
```

### 5. 스타일링
- Tailwind CSS 우선
- 복잡한 스타일만 CSS-in-JS
- 인라인 스타일 최소화

### 6. 파일 구조
```
frontend/src/
├── components/      # 재사용 가능한 컴포넌트
├── pages/          # 페이지 컴포넌트
├── hooks/          # 커스텀 훅
├── lib/            # 유틸리티, API 클라이언트
├── types/          # TypeScript 타입 정의
└── contexts/       # Context providers
```

### 7. 성능 최적화
- React.memo는 필요한 경우만
- useMemo, useCallback 과도한 사용 금지
- 큰 리스트는 페이지네이션 우선 고려

### 8. 테스트 전 체크리스트
- [ ] TypeScript 에러가 없는가?
- [ ] props 타입이 정의되어 있는가?
- [ ] 불필요한 console.log가 없는가?
- [ ] 에러 상태가 처리되어 있는가?
- [ ] 로딩 상태가 표시되는가?

### 9. 자주 사용하는 Import
```typescript
import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import type { Customer } from '../types';
```

### 10. 아이콘 사용
```typescript
// Lucide React 사용
import { User, Calendar, Package } from 'lucide-react';

// 크기는 className으로
<User className="h-5 w-5" />
```

---

*프론트엔드 작업 시 이 문서와 루트 CLAUDE.md를 함께 참조하세요.*
