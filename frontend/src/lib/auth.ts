import { api } from './api';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  user_id: number;
  email: string;
  name: string;
  role: 'admin' | 'manager' | 'staff' | 'master';
  is_active: boolean;
  created_at: string;
}

const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export const auth = {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await api.post<AuthTokens>('/auth/login', {
      email: credentials.email,
      password: credentials.password
    });

    const tokens = response.data;
    this.setTokens(tokens);
    return tokens;
  },

  async refresh(): Promise<AuthTokens> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('리프레시 토큰이 없습니다');
    }

    const response = await api.post<AuthTokens>('/auth/refresh', {
      refresh_token: refreshToken,
    });

    this.setTokens(response.data);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    return await api.get('/auth/me');
  },

  setTokens(tokens: AuthTokens) {
    localStorage.setItem(TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
  },

  getAccessToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  },

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  logout() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    window.location.href = '/login';
  },

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  },
};
