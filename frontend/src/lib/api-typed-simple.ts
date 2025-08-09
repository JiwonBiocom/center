/**
 * 간단한 타입이 강화된 API 클라이언트
 * 
 * 기존 API 클라이언트를 래핑하여 타입 안정성을 제공합니다.
 */
import { apiClient } from './api-client';
import type { Customer, CustomerCreate, CustomerUpdate, Service, Payment, User } from '../types';

// 자주 사용하는 API 호출을 위한 헬퍼 함수들
export const customerAPI = {
  // 고객 목록 조회
  list: (params?: any) => 
    apiClient.get<Customer[]>('/api/v1/customers', { params }),
  
  // 고객 상세 조회
  get: (customerId: number) => 
    apiClient.get<Customer>(`/api/v1/customers/${customerId}`),
  
  // 고객 생성
  create: (data: CustomerCreate) => 
    apiClient.post<Customer>('/api/v1/customers', data),
  
  // 고객 수정
  update: (customerId: number, data: CustomerUpdate) => 
    apiClient.put<Customer>(`/api/v1/customers/${customerId}`, data),
  
  // 고객 삭제
  delete: (customerId: number) => 
    apiClient.delete(`/api/v1/customers/${customerId}`),
};

export const serviceAPI = {
  // 서비스 목록 조회
  list: (params?: any) => 
    apiClient.get<Service[]>('/api/v1/services', { params }),
  
  // 서비스 생성
  create: (data: any) => 
    apiClient.post<Service>('/api/v1/services', data),
  
  // 서비스 상세 조회
  get: (serviceId: number) => 
    apiClient.get<Service>(`/api/v1/services/${serviceId}`),
};

export const paymentAPI = {
  // 결제 목록 조회
  list: (params?: any) => 
    apiClient.get<Payment[]>('/api/v1/payments', { params }),
  
  // 결제 생성
  create: (data: any) => 
    apiClient.post<Payment>('/api/v1/payments', data),
  
  // 결제 상세 조회
  get: (paymentId: number) => 
    apiClient.get<Payment>(`/api/v1/payments/${paymentId}`),
  
  // 결제 취소
  cancel: (paymentId: number) => 
    apiClient.post(`/api/v1/payments/${paymentId}/cancel`),
};

export const authAPI = {
  // 로그인
  login: (data: { email: string; password: string }) => 
    apiClient.post<{ access_token: string; refresh_token: string; user: User }>('/api/v1/auth/login', data),
  
  // 회원가입
  register: (data: any) => 
    apiClient.post<User>('/api/v1/auth/register', data),
  
  // 현재 사용자 정보
  me: () => 
    apiClient.get<User>('/api/v1/auth/me'),
  
  // 토큰 갱신
  refresh: (refreshToken: string) => 
    apiClient.post<{ access_token: string }>('/api/v1/auth/refresh', { refresh_token: refreshToken }),
};