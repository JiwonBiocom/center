/**
 * 공통 타입 정의
 */

// 기본 엔티티 타입
export interface BaseEntity {
  id: number;
  created_at: string;
  updated_at?: string;
}

// 선택 가능한 아이템
export interface SelectableItem<T = any> extends BaseEntity {
  selected?: boolean;
  data: T;
}

// 트리 구조 아이템
export interface TreeItem<T = any> {
  id: string | number;
  label: string;
  children?: TreeItem<T>[];
  expanded?: boolean;
  data?: T;
}

// 액션 타입
export interface Action<T = any> {
  type: string;
  payload?: T;
  meta?: Record<string, any>;
}

// 비동기 상태
export interface AsyncState<T = any> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

// 키-값 쌍
export interface KeyValue<T = any> {
  key: string;
  value: T;
}

// 상태 코드
export type StatusCode = 'active' | 'inactive' | 'pending' | 'completed' | 'cancelled' | 'failed';

// 우선순위
export type Priority = 'low' | 'medium' | 'high' | 'urgent';

// 권한 레벨
export type PermissionLevel = 'read' | 'write' | 'delete' | 'admin';

// 주소 타입
export interface Address {
  street: string;
  city: string;
  state: string;
  zipCode: string;
  country?: string;
}

// 연락처 타입
export interface Contact {
  phone?: string;
  email?: string;
  kakao?: string;
  instagram?: string;
}

// 시간 슬롯
export interface TimeSlot {
  start: string; // HH:mm
  end: string;   // HH:mm
  available: boolean;
}

// 업무 시간
export interface BusinessHours {
  [key: string]: {  // monday, tuesday, etc.
    open: string;   // HH:mm
    close: string;  // HH:mm
    closed?: boolean;
  };
}

// 통화 단위
export interface Currency {
  amount: number;
  currency: 'KRW' | 'USD' | 'EUR';
  formatted?: string;
}