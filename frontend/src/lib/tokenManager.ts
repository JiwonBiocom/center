import { jwtDecode } from 'jwt-decode';
import axios from 'axios';

let API_URL = import.meta.env.VITE_API_URL;

// 브라우저 환경에서 프로덕션 도메인 감지
const isProductionDomain = typeof window !== 'undefined' && 
  (window.location.hostname.includes('railway.app') || 
   window.location.hostname.includes('vercel.app') ||
   window.location.hostname.includes('netlify.app'))

// 프로덕션 환경에서는 반드시 HTTPS 사용
if (import.meta.env.MODE === 'production' || isProductionDomain) {
  if (!API_URL) {
    API_URL = 'https://center-production-1421.up.railway.app';
  } else if (API_URL.startsWith('http://') && !API_URL.includes('localhost')) {
    API_URL = API_URL.replace('http://', 'https://');
  }
  
  // 추가 안전장치: 프로덕션 도메인에서는 항상 HTTPS 강제
  if (API_URL.includes('railway.app') && API_URL.startsWith('http://')) {
    API_URL = API_URL.replace('http://', 'https://');
  }
} else {
  API_URL = API_URL || 'http://localhost:8000';
}

interface TokenPayload {
  sub: string;
  exp: number;
  type: string;
}

class TokenManager {
  private refreshTimer: NodeJS.Timeout | null = null;
  private isRefreshing = false;
  private refreshSubscribers: ((token: string) => void)[] = [];

  // 토큰 디코드
  private decodeToken(token: string): TokenPayload | null {
    try {
      return jwtDecode<TokenPayload>(token);
    } catch {
      return null;
    }
  }

  // 토큰 만료 여부 확인
  isTokenExpired(token: string): boolean {
    const decoded = this.decodeToken(token);
    if (!decoded) return true;
    
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  }

  // 토큰 만료까지 남은 시간 (밀리초)
  getTimeUntilExpiry(token: string): number {
    const decoded = this.decodeToken(token);
    if (!decoded) return 0;
    
    const currentTime = Date.now() / 1000;
    const timeUntilExpiry = (decoded.exp - currentTime) * 1000;
    return Math.max(0, timeUntilExpiry);
  }

  // 토큰 자동 갱신 설정
  setupAutoRefresh() {
    this.clearAutoRefresh();
    
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) return;
    
    const timeUntilExpiry = this.getTimeUntilExpiry(accessToken);
    
    // 만료 5분 전에 갱신 (최소 10초)
    const refreshTime = Math.max(timeUntilExpiry - 5 * 60 * 1000, 10 * 1000);
    
    if (refreshTime > 0) {
      console.log(`토큰 자동 갱신 예약: ${Math.round(refreshTime / 1000)}초 후`);
      
      this.refreshTimer = setTimeout(() => {
        this.refreshToken();
      }, refreshTime);
    }
  }

  // 자동 갱신 타이머 제거
  clearAutoRefresh() {
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  // 토큰 갱신
  async refreshToken(): Promise<string | null> {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken || this.isTokenExpired(refreshToken)) {
      this.handleLogout();
      return null;
    }

    // 이미 갱신 중이면 대기
    if (this.isRefreshing) {
      return new Promise((resolve) => {
        this.refreshSubscribers.push((token: string) => {
          resolve(token);
        });
      });
    }

    this.isRefreshing = true;

    try {
      const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
        refresh_token: refreshToken
      });

      const { access_token, refresh_token: newRefreshToken } = response.data;
      
      // 토큰 저장
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', newRefreshToken);
      
      // 대기 중인 요청들에게 새 토큰 전달
      this.refreshSubscribers.forEach(callback => callback(access_token));
      this.refreshSubscribers = [];
      
      // 자동 갱신 재설정
      this.setupAutoRefresh();
      
      console.log('토큰 갱신 성공');
      return access_token;
      
    } catch (error) {
      console.error('토큰 갱신 실패:', error);
      this.handleLogout();
      return null;
    } finally {
      this.isRefreshing = false;
    }
  }

  // 로그인 처리
  handleLogin(accessToken: string, refreshToken: string) {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
    this.setupAutoRefresh();
  }

  // 로그아웃 처리
  handleLogout() {
    this.clearAutoRefresh();
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }

  // 토큰 가져오기 (만료 확인 및 갱신)
  async getValidToken(): Promise<string | null> {
    const accessToken = localStorage.getItem('access_token');
    
    if (!accessToken) {
      return null;
    }

    // 토큰이 만료되었거나 5분 이내 만료 예정이면 갱신
    const timeUntilExpiry = this.getTimeUntilExpiry(accessToken);
    if (timeUntilExpiry < 5 * 60 * 1000) {
      const newToken = await this.refreshToken();
      return newToken;
    }

    return accessToken;
  }

  // 다중 탭 동기화
  setupTabSync() {
    window.addEventListener('storage', (e) => {
      if (e.key === 'access_token' && !e.newValue) {
        // 다른 탭에서 로그아웃
        this.clearAutoRefresh();
        window.location.href = '/login';
      } else if (e.key === 'access_token' && e.newValue) {
        // 다른 탭에서 토큰 갱신
        this.setupAutoRefresh();
      }
    });
  }
}

export const tokenManager = new TokenManager();