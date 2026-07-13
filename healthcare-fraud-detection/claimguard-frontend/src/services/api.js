import axios from 'axios';

// Base URL points at the Flask/FastAPI backend. Override with a .env file:
// VITE_API_BASE_URL=http://localhost:8000/api
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Set to "false" in .env once the backend endpoints below are live.
// While true, every service function returns realistic mock data instead
// of calling the network, so the UI can be built/reviewed independently.
export const USE_MOCK = (import.meta.env.VITE_USE_MOCK ?? 'true') === 'true';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('cg_access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refreshToken = localStorage.getItem('cg_refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, { refreshToken });
          localStorage.setItem('cg_access_token', data.accessToken);
          original.headers.Authorization = `Bearer ${data.accessToken}`;
          return api(original);
        } catch (refreshError) {
          localStorage.removeItem('cg_access_token');
          localStorage.removeItem('cg_refresh_token');
          window.location.href = '/login';
        }
      } else {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Small helper so mocked service calls still feel like network calls (loading states work).
export const mockDelay = (data, ms = 500) =>
  new Promise((resolve) => setTimeout(() => resolve(data), ms));

export default api;
