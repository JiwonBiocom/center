/**
 * 폼 관련 타입 정의
 */

// 폼 필드 에러
export interface FieldError {
  field: string;
  message: string;
}

// 폼 제출 상태
export interface FormSubmitState {
  isSubmitting: boolean;
  error: string | null;
  fieldErrors: FieldError[];
}

// 검색 폼 타입
export interface SearchFormData {
  query: string;
  filters: Record<string, any>;
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
}

// 날짜 범위 필터
export interface DateRangeFilter {
  startDate: Date | null;
  endDate: Date | null;
}

// 가격 범위 필터
export interface PriceRangeFilter {
  min: number | null;
  max: number | null;
}

// 페이지네이션 상태
export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}

// 파일 업로드 상태
export interface FileUploadState {
  file: File | null;
  progress: number;
  error: string | null;
  url?: string;
}

// 폼 검증 규칙
export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => string | null;
}

// 폼 필드 설정
export interface FormFieldConfig {
  name: string;
  label: string;
  type: 'text' | 'number' | 'email' | 'tel' | 'date' | 'select' | 'textarea' | 'checkbox' | 'radio';
  placeholder?: string;
  options?: Array<{ value: string; label: string }>;
  validation?: ValidationRule;
  defaultValue?: any;
  disabled?: boolean;
  hidden?: boolean;
}