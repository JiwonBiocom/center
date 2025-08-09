/**
 * 추가 모델 타입 정의
 * 
 * API에서 자동 생성되지 않는 추가 타입들을 정의합니다.
 */

// 대시보드 통계 타입
export interface DashboardStats {
  totalCustomers: number;
  newCustomersThisMonth: number;
  activeCustomers: number;
  totalRevenue: number;
  revenueThisMonth: number;
  unpaidAmount: number;
  todayReservations: number;
  upcomingReservations: number;
}

// 차트 데이터 타입
export interface ChartDataPoint {
  name: string;
  value: number;
  label?: string;
}

// 필터 옵션 타입
export interface FilterOption {
  value: string;
  label: string;
  count?: number;
}

// 테이블 정렬 타입
export interface SortConfig {
  key: string;
  direction: 'asc' | 'desc';
}

// 모달 상태 타입
export interface ModalState<T = any> {
  isOpen: boolean;
  mode: 'create' | 'edit' | 'view';
  data?: T;
}

// 알림 타입
export interface NotificationItem {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
}

// 메뉴 아이템 타입
export interface MenuItem {
  path: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  children?: MenuItem[];
  permission?: string;
}

// 테이블 컬럼 타입
export interface TableColumn<T = any> {
  key: keyof T | string;
  label: string;
  width?: string;
  align?: 'left' | 'center' | 'right';
  sortable?: boolean;
  render?: (value: any, item: T) => React.ReactNode;
}