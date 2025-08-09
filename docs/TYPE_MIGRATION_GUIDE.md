# 타입 마이그레이션 가이드

> 작성일: 2025-06-10
> 목적: 자동 생성된 TypeScript 타입 사용 가이드

## 개요

백엔드 OpenAPI 스키마에서 자동으로 생성된 TypeScript 타입을 사용하여 프론트엔드와 백엔드 간의 타입 동기화를 보장합니다.

## 타입 생성 방법

### 1. 백엔드에서 OpenAPI 스키마 생성
```bash
cd backend
python scripts/generate_openapi.py
```

### 2. 프론트엔드에서 TypeScript 타입 생성
```bash
cd frontend
npm run generate:types
```

### 3. 한 번에 모두 업데이트
```bash
cd frontend
npm run update:types
```

## 타입 사용 방법

### 1. 기본 import
```typescript
// 자동 생성된 타입
import type { Customer, Payment, Service } from '../types';

// API 응답 타입
import type { APIResponse, PaginatedResponse } from '../types';
```

### 2. API 클라이언트 사용

#### 기존 방식 (타입 안정성 낮음)
```typescript
const response = await api.get('/api/v1/customers');
const customers = response.data; // any 타입
```

#### 새로운 방식 (완전한 타입 안정성)
```typescript
import { customerAPI } from '../lib/api-typed';

// 자동 완성과 타입 체크 지원
const customers = await customerAPI.list({
  search: '김',
  region: '서울',
  page: 1,
  page_size: 20
});

// customers는 자동으로 Customer[] 타입
customers.forEach(customer => {
  console.log(customer.name); // 타입 체크됨
});
```

### 3. 컴포넌트에서 사용

```typescript
import { useState } from 'react';
import type { Customer, APIResponse } from '../types';
import { customerAPI } from '../lib/api-typed';

interface CustomerListProps {
  region?: string;
}

export function CustomerList({ region }: CustomerListProps) {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  
  const loadCustomers = async () => {
    setLoading(true);
    try {
      const data = await customerAPI.list({ region });
      setCustomers(data);
    } catch (error) {
      console.error('Failed to load customers:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // ...
}
```

### 4. React Query와 함께 사용

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import type { Customer, CustomerCreate } from '../types';
import { customerAPI } from '../lib/api-typed';

// 고객 목록 조회
export function useCustomers(params?: any) {
  return useQuery({
    queryKey: ['customers', params],
    queryFn: () => customerAPI.list(params),
  });
}

// 고객 생성
export function useCreateCustomer() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CustomerCreate) => customerAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customers'] });
    },
  });
}
```

## 마이그레이션 체크리스트

### Phase 1: 타입 Import 변경
- [ ] 기존 수동 타입 정의를 자동 생성 타입으로 교체
- [ ] import 경로를 `../types`로 통일

### Phase 2: API 호출 변경
- [ ] `api.get/post/put/delete`를 타입이 있는 API 헬퍼로 교체
- [ ] 응답 타입 명시 제거 (자동 추론됨)

### Phase 3: 컴포넌트 타입 강화
- [ ] Props 인터페이스에서 자동 생성 타입 사용
- [ ] State 타입에서 자동 생성 타입 사용

### Phase 4: 검증
- [ ] TypeScript 컴파일 에러 해결
- [ ] 런타임 테스트
- [ ] 타입 자동 완성 확인

## 주의사항

1. **타입 수정 금지**: `api-generated.ts` 파일은 자동 생성되므로 직접 수정하지 마세요.

2. **백엔드 변경 시**: 백엔드 API가 변경되면 반드시 타입을 재생성하세요.
   ```bash
   npm run update:types
   ```

3. **타입 확장**: 자동 생성 타입을 확장해야 할 경우 별도 파일에서 확장하세요.
   ```typescript
   // types/extended.ts
   import type { Customer } from './api-generated';
   
   export interface CustomerWithStats extends Customer {
     totalPurchases: number;
     lastPurchaseDate: string;
   }
   ```

4. **null/undefined 처리**: API 응답이 null일 수 있는 경우 명시적으로 처리하세요.
   ```typescript
   const customer = await customerAPI.get(id);
   if (!customer) {
     throw new Error('Customer not found');
   }
   ```

## 트러블슈팅

### 타입 생성 실패
- Python 환경 확인: `python --version` (3.12 이상)
- Node.js 환경 확인: `node --version` (20 이상)
- 의존성 설치 확인: `npm install`

### 타입 불일치
- 백엔드와 프론트엔드 브랜치가 같은지 확인
- 타입 재생성: `npm run update:types`
- 캐시 클리어: `rm -rf node_modules/.cache`

### IDE 자동 완성 안됨
- TypeScript 서비스 재시작
- VSCode: Cmd/Ctrl + Shift + P → "TypeScript: Restart TS Server"
- 프로젝트 재로드

## 다음 단계

1. 모든 API 호출을 타입이 있는 버전으로 마이그레이션
2. 컴포넌트 props와 state 타입 강화
3. 폼 검증에 타입 정보 활용
4. API 문서와 타입 동기화 자동화