// HealthFit AI - Axios API Service Base
// Configures axios with auth headers and error interceptors

import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Request interceptor: attach JWT token ──────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('healthfit_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor: handle auth errors ───────────────
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid — clear local storage and redirect
      localStorage.removeItem('healthfit_token');
      localStorage.removeItem('healthfit_user');
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;
