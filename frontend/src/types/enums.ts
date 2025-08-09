/**
 * 데이터베이스와 동기화된 Enum 타입 정의
 *
 * ⚠️ 주의: 이 값들은 데이터베이스의 enum 타입과 정확히 일치해야 합니다.
 * 변경 시 반드시 DB 스키마와 백엔드 코드도 함께 변경해야 합니다.
 */

// 회원 등급
export enum MembershipLevel {
  BASIC = 'basic',
  SILVER = 'silver',
  GOLD = 'gold',
  PLATINUM = 'platinum',
  VIP = 'vip'
}

// 고객 상태
export enum CustomerStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  DORMANT = 'dormant'
}

// 결제 상태
export enum PaymentStatus {
  PENDING = 'pending',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  REFUNDED = 'refunded'
}

// 결제 수단
export enum PaymentMethod {
  CASH = 'cash',
  CARD = 'card',
  TRANSFER = 'transfer',
  OTHER = 'other'
}

// 결제 유형
export enum PaymentType {
  PACKAGE = 'package',
  SINGLE = 'single',
  ADDITIONAL = 'additional',
  REFUND = 'refund'
}

// 사용자 역할
export enum UserRole {
  ADMIN = 'admin',
  MANAGER = 'manager',
  STAFF = 'staff',
  MASTER = 'master'
}

// 예약 상태
export enum ReservationStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  CANCELLED = 'cancelled',
  COMPLETED = 'completed',
  NO_SHOW = 'no_show'
}

// 알림 타입
export enum NotificationType {
  SMS = 'sms',
  EMAIL = 'email',
  KAKAO = 'kakao',
  PUSH = 'push',
  SYSTEM = 'system'
}

// 캠페인 상태
export enum CampaignStatus {
  DRAFT = 'draft',
  SCHEDULED = 'scheduled',
  SENT = 'sent',
  CANCELLED = 'cancelled'
}

// 캠페인 타입
export enum CampaignType {
  SMS = 'sms',
  EMAIL = 'email',
  KAKAO = 'kakao',
  PUSH = 'push'
}

// 타입 가드 함수들
export const isMembershipLevel = (value: string): value is MembershipLevel => {
  return Object.values(MembershipLevel).includes(value as MembershipLevel);
};

export const isCustomerStatus = (value: string): value is CustomerStatus => {
  return Object.values(CustomerStatus).includes(value as CustomerStatus);
};

export const isPaymentStatus = (value: string): value is PaymentStatus => {
  return Object.values(PaymentStatus).includes(value as PaymentStatus);
};

export const isPaymentMethod = (value: string): value is PaymentMethod => {
  return Object.values(PaymentMethod).includes(value as PaymentMethod);
};

export const isUserRole = (value: string): value is UserRole => {
  return Object.values(UserRole).includes(value as UserRole);
};

// 한글 라벨 매핑
export const MembershipLevelLabel: Record<MembershipLevel, string> = {
  [MembershipLevel.BASIC]: '일반',
  [MembershipLevel.SILVER]: '실버',
  [MembershipLevel.GOLD]: '골드',
  [MembershipLevel.PLATINUM]: '플래티넘',
  [MembershipLevel.VIP]: 'VIP'
};

export const CustomerStatusLabel: Record<CustomerStatus, string> = {
  [CustomerStatus.ACTIVE]: '활성',
  [CustomerStatus.INACTIVE]: '비활성',
  [CustomerStatus.DORMANT]: '휴면'
};

export const PaymentStatusLabel: Record<PaymentStatus, string> = {
  [PaymentStatus.PENDING]: '대기중',
  [PaymentStatus.COMPLETED]: '완료',
  [PaymentStatus.CANCELLED]: '취소',
  [PaymentStatus.REFUNDED]: '환불'
};

export const PaymentMethodLabel: Record<PaymentMethod, string> = {
  [PaymentMethod.CASH]: '현금',
  [PaymentMethod.CARD]: '카드',
  [PaymentMethod.TRANSFER]: '계좌이체',
  [PaymentMethod.OTHER]: '기타'
};

export const UserRoleLabel: Record<UserRole, string> = {
  [UserRole.ADMIN]: '관리자',
  [UserRole.MANAGER]: '매니저',
  [UserRole.STAFF]: '직원',
  [UserRole.MASTER]: '마스터'
};

export const ReservationStatusLabel: Record<ReservationStatus, string> = {
  [ReservationStatus.PENDING]: '대기중',
  [ReservationStatus.CONFIRMED]: '확정',
  [ReservationStatus.CANCELLED]: '취소',
  [ReservationStatus.COMPLETED]: '완료',
  [ReservationStatus.NO_SHOW]: '노쇼'
};
