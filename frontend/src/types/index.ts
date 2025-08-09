/**
 * 타입 정의 인덱스 파일
 */

// 자동 생성된 API 타입
export * from './api-generated';

// 수동으로 정의한 타입들
export * from './models';
export * from './forms';
export * from './common';
export * from './enums';

// API 응답 타입 alias
import { paths, components } from './api-generated';

export type APIComponents = components;
export type APIPaths = paths;

// 자주 사용하는 타입 alias (안전하게 처리)
export type Customer = components['schemas'] extends { 'Customer': infer T } ? T : any;
export type CustomerCreate = components['schemas'] extends { 'CustomerCreate': infer T } ? T : any;
export type CustomerUpdate = components['schemas'] extends { 'CustomerUpdate': infer T } ? T : any;

export type Service = components['schemas'] extends { 'ServiceUsage': infer T } ? T : any;
export type ServiceCreate = components['schemas'] extends { 'ServiceUsageCreate': infer T } ? T : any;
export type ServiceType = components['schemas'] extends { 'ServiceType': infer T } ? T : any;

export type Payment = components['schemas'] extends { 'Payment': infer T } ? T : any;
export type PaymentCreate = components['schemas'] extends { 'PaymentCreate': infer T } ? T : any;

export type Package = components['schemas'] extends { 'Package': infer T } ? T : any;
export type PackageCreate = components['schemas'] extends { 'PackageCreate': infer T } ? T : any;

export type User = components['schemas'] extends { 'User': infer T } ? T : any;
export type UserLogin = components['schemas'] extends { 'UserLogin': infer T } ? T : any;

export type Reservation = components['schemas'] extends { 'Reservation': infer T } ? T : any;
export type ReservationCreate = components['schemas'] extends { 'ReservationCreate': infer T } ? T : any;

// API 응답 타입
export type APIResponse<T = any> = components['schemas'] extends { 'APIResponse': infer R } ? R : { success: boolean; data?: T; error?: any; message?: string };
export type PaginatedResponse<T = any> = components['schemas'] extends { 'PaginatedResponse': infer R } ? R : { success: boolean; data: T[]; total: number; page: number; page_size: number };
export type ErrorResponse = components['schemas'] extends { 'ErrorResponse': infer T } ? T : { success: false; error: any; message: string };
