// HealthFit AI - Authentication Service
import api from './api';
import { User } from '../types';

export interface LoginPayload { email: string; password: string; }
export interface RegisterPayload {
  email: string; password: string;
  first_name: string; last_name: string;
  role?: string; gender?: string; phone?: string;
  date_of_birth?: string; height_cm?: number; weight_kg?: number;
}
export interface AuthResponse {
  user: User; access_token: string; refresh_token?: string; message: string;
}

interface ProfileUpdatePayload {
  height_cm?: number;
  weight_kg?: number;
  fitness_goal?: string;
  activity_level?: string;
}

const AuthService = {
  async login(payload: LoginPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/login', payload);
    localStorage.setItem('healthfit_token', data.access_token);
    localStorage.setItem('healthfit_user', JSON.stringify(data.user));
    return data;
  },

  async register(payload: RegisterPayload): Promise<AuthResponse> {
    const { data } = await api.post<AuthResponse>('/auth/register', payload);
    localStorage.setItem('healthfit_token', data.access_token);
    localStorage.setItem('healthfit_user', JSON.stringify(data.user));
    return data;
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } catch {}
    localStorage.removeItem('healthfit_token');
    localStorage.removeItem('healthfit_user');
  },

  async getCurrentUser(): Promise<User> {
    const { data } = await api.get<{ user: User }>('/auth/me');
    return data.user;
  },

  async updateProfile(payload: Partial<User> & ProfileUpdatePayload): Promise<User> {
    const { data } = await api.put<{ user: User }>('/auth/me', payload);
    localStorage.setItem('healthfit_user', JSON.stringify(data.user));
    return data.user;
  },

  async changePassword(current_password: string, new_password: string): Promise<void> {
    await api.post('/auth/change-password', { current_password, new_password });
  },

  getStoredUser(): User | null {
    const raw = localStorage.getItem('healthfit_user');
    if (!raw) return null;
    try {
      return JSON.parse(raw) as User;
    } catch {
      return null;
    }
  },

  getToken(): string | null {
    return localStorage.getItem('healthfit_token');
  },

  isAuthenticated(): boolean {
    return !!this.getToken();
  }
};

export default AuthService;

