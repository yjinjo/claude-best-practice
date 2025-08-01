import axios from 'axios';
import { PersonaType } from '../context/AppContext';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ValidationResponse {
  valid: boolean;
  title?: string;
  message?: string;
}

export interface SummaryResponse {
  summary: string;
  title: string;
  url: string;
  persona: string;
}

export interface FeedbackResponse {
  message: string;
  id: string;
}

export const apiService = {
  validateUrl: async (url: string): Promise<ValidationResponse> => {
    try {
      console.log('API 요청 시작:', { url, endpoint: '/validate-url' });
      const response = await api.post('/validate-url', { url });
      console.log('API 응답 성공:', response.data);
      return response.data;
    } catch (error) {
      console.error('API 요청 실패:', error);
      throw error;
    }
  },

  generateSummary: async (url: string, persona: PersonaType): Promise<SummaryResponse> => {
    const response = await api.post('/summarize', { url, persona });
    return response.data;
  },

  submitFeedback: async (
    url: string,
    persona: PersonaType,
    feedback: 'positive' | 'negative'
  ): Promise<FeedbackResponse> => {
    const response = await api.post('/feedback', { url, persona, feedback });
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/stats');
    return response.data;
  },
};

export default apiService;