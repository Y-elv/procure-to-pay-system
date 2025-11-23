/**
 * API client configuration and utilities.
 */
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// Auth API
export const authAPI = {
  login: (username: string, password: string) =>
    apiClient.post('/auth/login/', { username, password }),
  register: (data: any) => apiClient.post('/auth/register/', data),
  logout: (refresh: string) => apiClient.post('/auth/logout/', { refresh }),
  me: () => apiClient.get('/auth/me/'),
};

// Requests API
export const requestsAPI = {
  list: (params?: any) => apiClient.get('/requests/', { params }),
  get: (id: number) => apiClient.get(`/requests/${id}/`),
  create: (data: any) => {
    const formData = new FormData();
    Object.keys(data).forEach((key) => {
      if (key === 'items' && Array.isArray(data[key])) {
        // Send items as JSON string
        formData.append('items', JSON.stringify(data[key]));
      } else if (data[key] instanceof File) {
        formData.append(key, data[key]);
      } else if (data[key] !== null && data[key] !== undefined && key !== 'items') {
        formData.append(key, String(data[key]));
      }
    });
    return apiClient.post('/requests/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  update: (id: number, data: any) => apiClient.put(`/requests/${id}/`, data),
  approve: (id: number, comment?: string) =>
    apiClient.patch(`/requests/${id}/approve/`, { comment }),
  reject: (id: number, comment: string) =>
    apiClient.patch(`/requests/${id}/reject/`, { comment }),
  submitReceipt: (id: number, file: File) => {
    const formData = new FormData();
    formData.append('receipt_file', file);
    return apiClient.post(`/requests/${id}/submit-receipt/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  validateReceipt: (id: number) =>
    apiClient.post(`/requests/${id}/validate-receipt/`),
};

