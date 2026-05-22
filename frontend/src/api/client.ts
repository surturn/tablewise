import axios from 'axios';
import { useAuthStore } from '../store/authStore';

/**
 * Base URL of the FastAPI backend (no trailing slash, no /api/v1).
 * Set VITE_API_BASE_URL in the Vercel Dashboard for production,
 * e.g. "https://tablewise-api.onrender.com".
 * Falls back to localhost for local development.
 */
const API_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/+$/, '');

// Create a configured Axios instance
export const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Auto-inject JWT token if it exists
apiClient.interceptors.request.use(
  (config) => {
    // Read directly from Zustand state
    const token = useAuthStore.getState().token;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Handle global 401 Unauthorized
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config.url?.includes('/auth/login') && !error.config.url?.includes('/auth/customer/login')) {
      // Token expired or invalid -> force logout
      const role = useAuthStore.getState().user?.role;
      useAuthStore.getState().logout();
      window.location.href = role && role !== 'customer' ? '/staff/login' : '/login';
    }
    return Promise.reject(error);
  }
);