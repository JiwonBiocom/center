/**
 * API 클라이언트 - 표준 응답 구조 지원
 */
import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios';

// API 응답 타입 정의
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    details?: any;
  };
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<T = any> {
  success: boolean;
  data: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
  message?: string;
  timestamp: string;
}

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    details?: any;
  };
  message: string;
  timestamp: string;
  request_id?: string;
}

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = '') {
    // API URL 설정 - api.ts와 동일한 로직 적용
    let apiUrl = baseURL || import.meta.env.VITE_API_URL;
    
    // 브라우저 환경에서 프로덕션 도메인 감지
    const isProductionDomain = typeof window !== 'undefined' && 
      (window.location.hostname.includes('railway.app') || 
       window.location.hostname.includes('vercel.app') ||
       window.location.hostname.includes('netlify.app'));
    
    if (import.meta.env.MODE === 'production' || isProductionDomain) {
      if (!apiUrl) {
        apiUrl = 'https://center-production-1421.up.railway.app';
      } else if (apiUrl.startsWith('http://') && !apiUrl.includes('localhost')) {
        apiUrl = apiUrl.replace('http://', 'https://');
      }
    } else {
      apiUrl = apiUrl || 'http://localhost:8000';
    }
    
    this.client = axios.create({
      baseURL: apiUrl,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        // 표준 응답 구조 처리
        if (this.isStandardResponse(response.data)) {
          if (response.data.success) {
            // 성공 응답인 경우 data만 반환
            return response;
          } else {
            // 실패 응답인 경우 에러로 처리
            return Promise.reject(response.data);
          }
        }
        // 기존 응답 구조 그대로 반환
        return response;
      },
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  private isStandardResponse(data: any): data is APIResponse {
    return data && typeof data === 'object' && 'success' in data;
  }

  // 표준 API 메서드들
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<APIResponse<T>>(url, config);
    if (this.isStandardResponse(response.data)) {
      return response.data.data as T;
    }
    return response.data as T;
  }

  async getPaginated<T>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<PaginatedResponse<T>> {
    const response = await this.client.get<PaginatedResponse<T>>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<APIResponse<T>>(url, data, config);
    if (this.isStandardResponse(response.data)) {
      return response.data.data as T;
    }
    return response.data as T;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<APIResponse<T>>(url, data, config);
    if (this.isStandardResponse(response.data)) {
      return response.data.data as T;
    }
    return response.data as T;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<APIResponse<T>>(url, config);
    if (this.isStandardResponse(response.data)) {
      return response.data.data as T;
    }
    return response.data as T;
  }

  // 기존 api 객체와의 호환성을 위한 래퍼
  request(config: AxiosRequestConfig) {
    return this.client.request(config);
  }
}

// 싱글톤 인스턴스
export const apiClient = new APIClient();

// 기존 api 객체와의 호환성 유지
export const api = (function() {
  const client = (apiClient as any).client as AxiosInstance;
  return {
    get: <T = any>(url: string, config?: AxiosRequestConfig) => 
      client.get<T>(url, config),
    
    post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
      client.post<T>(url, data, config),
    
    put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
      client.put<T>(url, data, config),
    
    delete: <T = any>(url: string, config?: AxiosRequestConfig) => 
      client.delete<T>(url, config),
    
    request: (config: AxiosRequestConfig) => 
      client.request(config),
  };
})();

// 내보내기
export default apiClient;