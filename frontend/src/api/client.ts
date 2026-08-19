import axios, { AxiosError } from 'axios';
import {
  PredictionResponse,
  BatchPredictionResponse,
  EmployeeProfileData,
  AnalyticsSummary,
  EmployeePredictionInput
} from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

export const api = {
  health: async () => {
    const res = await client.get('/health');
    return res.data;
  },

  predict: async (data: EmployeePredictionInput): Promise<PredictionResponse> => {
    const res = await client.post('/api/predict', data);
    return res.data;
  },

  batchPreview: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    // Setting header for HTMX emulation because batch-preview endpoint returns HTMLResponse
    // Wait, batch-preview only returns HTMLResponse. We might need to handle this differently.
    // For now, let's request it and see if backend can be tricked or if we need to parse HTML.
    // The instruction says: Do NOT change FastAPI backend.
    const res = await client.post('/api/batch-preview', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  batchPredict: async (file: File): Promise<BatchPredictionResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await client.post('/api/batch-predict', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  getBatchDownloadUrl: (batchId: string) => {
    return `${API_BASE}/api/batch-results/${batchId}/download`;
  },

  getEmployeeProfile: async (id: string): Promise<EmployeeProfileData> => {
    const res = await client.get(`/api/employee/${id}`);
    return res.data;
  },

  // Note: this endpoint returns HTML in FastAPI currently. We might have to parse it or simulate the notes state locally.
  addEmployeeNote: async (id: string, note: string, author: string = 'HR Partner'): Promise<any> => {
    const formData = new FormData();
    formData.append('note', note);
    formData.append('author', author);
    const res = await client.post(`/api/employee/${id}/notes`, formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return res.data;
  },

  getAnalyticsSummary: async (): Promise<AnalyticsSummary> => {
    const res = await client.get('/api/analytics/summary');
    return res.data;
  },

  getAnalyticsDepartment: async (): Promise<any> => {
    const res = await client.get('/api/analytics/department');
    return res.data;
  },

  getAnalyticsTrends: async (): Promise<any> => {
    const res = await client.get('/api/analytics/trends');
    return res.data;
  },

  getAnalyticsTopFeatures: async (): Promise<any> => {
    const res = await client.get('/api/analytics/top-features');
    return res.data;
  },

  getAnalyticsAgeGroups: async (): Promise<any> => {
    const res = await client.get('/api/analytics/age-groups');
    return res.data;
  },

  getAnalyticsIncomeScatter: async (): Promise<any> => {
    const res = await client.get('/api/analytics/income-scatter');
    return res.data;
  },
};

export const extractErrorMessage = (error: unknown): string => {
  if (error instanceof AxiosError) {
    if (error.response?.data?.detail) {
      return typeof error.response.data.detail === 'string'
        ? error.response.data.detail
        : JSON.stringify(error.response.data.detail);
    }
    return error.message;
  }
  return error instanceof Error ? error.message : String(error);
};
