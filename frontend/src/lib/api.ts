import axios from 'axios'
import { tokenManager } from './tokenManager'

// API URL 설정
let API_URL = import.meta.env.VITE_API_URL

// 브라우저 환경에서 프로덕션 도메인 감지
const isProductionDomain = typeof window !== 'undefined' &&
  (window.location.hostname.includes('railway.app') ||
   window.location.hostname.includes('vercel.app') ||
   window.location.hostname.includes('netlify.app'))

// 프로덕션 환경에서는 반드시 HTTPS 사용
if (import.meta.env.MODE === 'production' || isProductionDomain) {
  if (!API_URL) {
    // 프로덕션에서 환경변수가 없으면 Railway HTTPS URL 사용
    API_URL = 'https://center-production-1421.up.railway.app'
    console.warn('⚠️ VITE_API_URL not set, using default HTTPS URL')
  } else if (API_URL.startsWith('http://') && !API_URL.includes('localhost')) {
    console.error('🚨 CRITICAL: Production API URL must use HTTPS!')
    // HTTP를 HTTPS로 강제 변환
    API_URL = API_URL.replace('http://', 'https://')
    console.warn(`🔄 Forcing HTTPS: ${API_URL}`)
  }

  // 추가 안전장치: 프로덕션 도메인에서는 항상 HTTPS 강제
  if (API_URL.includes('railway.app') && API_URL.startsWith('http://')) {
    API_URL = API_URL.replace('http://', 'https://')
    console.warn(`🔒 Enforcing HTTPS for Railway domain: ${API_URL}`)
  }
} else {
  // 개발 환경 기본값
  API_URL = API_URL || 'http://localhost:8000'
}

// 개발 환경 로그
console.log('🔧 API URL:', API_URL)
console.log('🔧 Environment:', import.meta.env.MODE)
console.log('🔧 Build Time:', new Date().toISOString())

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // CORS credentials 지원
})

// Request interceptor for auth token and URL normalization
api.interceptors.request.use(
  async (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url)
    // console.log('API Request Data:', config.data)

    // 토큰 자동 갱신 처리
    const token = await tokenManager.getValidToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // Ensure API prefix is correct
    if (config.url && !config.url.startsWith('http')) {
      // Prepend /api/v1 if not already present
      if (!config.url.startsWith('/api/v1')) {
        config.url = `/api/v1${config.url.startsWith('/') ? config.url : '/' + config.url}`
      }

      // Remove any double slashes except after protocol
      config.url = config.url.replace(/([^:]\/)\/+/g, '$1')

      // FastAPI requires trailing slash for POST/PUT/PATCH requests
      // Exception: InBody endpoints don't need trailing slash
      if (['post', 'put', 'patch'].includes(config.method?.toLowerCase() || '')) {
        if (!config.url.includes('/inbody') && !config.url.endsWith('/') && !config.url.includes('?')) {
          config.url += '/'
        }
      }
    }

    // console.log('API Request Final URL:', config.url)

    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url)
    console.log('API Response Data:', response.data)
    return response
  },
  async (error) => {
    console.error('API Response Error:', error.response?.status, error.config?.url)
    console.error('API Response Error Data:', error.response?.data)
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const newToken = await tokenManager.refreshToken();
        if (newToken) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - tokenManager will handle logout
        return Promise.reject(refreshError);
      }
    }

    if (error.response?.status === 401) {
      // 로그인 페이지나 로그인 API 호출 시에는 자동 로그아웃하지 않음
      const isLoginPage = window.location.pathname === '/login';
      const isLoginAPI = error.config?.url?.includes('/auth/login');

      if (!isLoginPage && !isLoginAPI) {
        // No refresh token or refresh failed
        tokenManager.handleLogout();
      }
    }

    return Promise.reject(error);
  }
)

export default api
