import axios, { AxiosInstance, AxiosResponse } from 'axios';
import toast from 'react-hot-toast';
import {
  User,
  Challenge,
  ChallengeAttempt,
  Category,
  UserAnalytics,
  LearningProgress,
  LeaderboardEntry,
} from '../types';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    // Get JWT token from localStorage
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
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/auth/login';
    } else if (error.response?.status === 403) {
      toast.error('Access denied');
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Request timeout. Please try again.');
    }

    return Promise.reject(error);
  }
);

// Token response type
interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Auth Service
export const authService = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (userData: {
    email: string;
    username: string;
    password: string;
    display_name?: string;
    skill_level?: string;
  }): Promise<TokenResponse> => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  verifyToken: async (token: string): Promise<{ valid: boolean; user_id: number }> => {
    const response = await api.post('/auth/verify-token', {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  getCurrentUser: async (token: string): Promise<User> => {
    const response = await api.get('/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  updateProfile: async (userData: Partial<User>, token: string): Promise<User> => {
    const response = await api.put('/auth/me', userData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  }
};

// Challenge Service
export const challengeService = {
  getChallenges: async (params?: {
    skip?: number;
    limit?: number;
    category_id?: number;
    difficulty?: string;
    status?: string;
  }): Promise<Challenge[]> => {
    const response = await api.get('/challenges/', { params });
    return response.data;
  },

  getChallenge: async (id: number): Promise<Challenge> => {
    const response = await api.get(`/challenges/${id}`);
    return response.data;
  },

  submitAttempt: async (challengeId: number, flag: string): Promise<ChallengeAttempt> => {
    const response = await api.post(`/challenges/${challengeId}/attempts`, {
      challenge_id: challengeId,
      flag_submitted: flag
    });
    return response.data;
  },

  getAttempts: async (challengeId: number): Promise<ChallengeAttempt[]> => {
    const response = await api.get(`/challenges/${challengeId}/attempts`);
    return response.data;
  },

  startChallenge: async (challengeId: number): Promise<any> => {
    const response = await api.get(`/challenges/${challengeId}/start`);
    return response.data;
  },

  getHint: async (challengeId: number, hintLevel: number = 1): Promise<{ hint: string }> => {
    const response = await api.post(`/challenges/${challengeId}/hint`, {
      hint_level: hintLevel
    });
    return response.data;
  },

  rateChallenge: async (challengeId: number, rating: {
    difficulty_rating?: number;
    quality_rating?: number;
    enjoyment_rating?: number;
    feedback?: string;
  }): Promise<void> => {
    await api.post(`/challenges/${challengeId}/rating`, {
      challenge_id: challengeId,
      ...rating
    });
  },

  getRecommended: async (limit: number = 10): Promise<Challenge[]> => {
    const response = await api.get('/challenges/recommended/', {
      params: { limit }
    });
    return response.data;
  }
};

// Category Service
export const categoryService = {
  getCategories: async (): Promise<Category[]> => {
    const response = await api.get('/categories/');
    return response.data;
  }
};

// User Service
export const userService = {
  getUser: async (id: number): Promise<User> => {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },

  getUserProgress: async (id: number): Promise<LearningProgress> => {
    const response = await api.get(`/users/${id}/progress`);
    return response.data;
  },

  getLeaderboard: async (params?: {
    limit?: number;
    timeframe?: string;
    category_id?: number;
  }): Promise<LeaderboardEntry[]> => {
    const response = await api.get('/users/leaderboard/', { params });
    return response.data;
  }
};

// Analytics Service
export const analyticsService = {
  getUserAnalytics: async (userId: number): Promise<UserAnalytics> => {
    const response = await api.get(`/analytics/user/${userId}`);
    return response.data;
  },

  createSession: async (sessionData: {
    session_id: string;
    user_agent?: string;
    device_type?: string;
  }): Promise<any> => {
    const response = await api.post('/analytics/session', sessionData);
    return response.data;
  },

  updateSession: async (sessionId: string, sessionData: any): Promise<void> => {
    await api.put(`/analytics/session/${sessionId}`, sessionData);
  },

  getDashboardData: async (timeframe: string = '7d'): Promise<any> => {
    const response = await api.get('/analytics/dashboard', {
      params: { timeframe }
    });
    return response.data;
  },

  getSkillProgression: async (userId?: number): Promise<any> => {
    const response = await api.get('/analytics/insights/skill-progression', {
      params: userId ? { user_id: userId } : {}
    });
    return response.data;
  },

  getPersonalizedRecommendations: async (limit: number = 10): Promise<any> => {
    const response = await api.get('/analytics/recommendations/personalized', {
      params: { limit }
    });
    return response.data;
  }
};

// AI Service
export const aiService = {
  // Admin background task (existing)
  generateChallenge: async (request: {
    category: string;
    difficulty: string;
    topic: string;
    learning_objectives: string[];
    user_skill_level: string;
  }): Promise<{ task_id: string; message: string; estimated_time: string }> => {
    const response = await api.post('/ai/admin/generate-challenge-task', request);
    return response.data;
  },

  // New: personalized generator for current user (used by sidebar page)
  generatePersonalizedChallenge: async (request: {
    category: string;
    difficulty: string;
    learning_goal: string;
  }): Promise<Challenge> => {
    const response = await api.post('/ai/generate-challenge', request);
    return response.data;
  },

  getGeneratedChallenges: async (): Promise<Challenge[]> => {
    const response = await api.get('/ai/generated-challenges');
    return response.data;
  },

  getGenerationStatus: async (taskId: string): Promise<any> => {
    const response = await api.get(`/ai/generation-status/${taskId}`);
    return response.data;
  },

  getHint: async (challengeId: number, userProgress: any, hintLevel: number = 1): Promise<{ hint: string; level: number }> => {
    const response = await api.post('/ai/hint', {
      challenge_id: challengeId,
      user_progress: userProgress,
      hint_level: hintLevel
    });
    return response.data;
  },

  getFeedback: async (challengeId: number, userAttempt: string, isCorrect: boolean): Promise<{ feedback: string }> => {
    const response = await api.post('/ai/feedback', {
      challenge_id: challengeId,
      user_attempt: userAttempt,
      is_correct: isCorrect
    });
    return response.data;
  },

  getSkillAssessment: async (): Promise<any> => {
    const response = await api.get('/ai/skill-assessment');
    return response.data;
  },

  getLearningPath: async (targetSkill: string = 'intermediate'): Promise<any> => {
    const response = await api.get('/ai/learning-path', {
      params: { target_skill: targetSkill }
    });
    return response.data;
  },

  getModelsStatus: async (): Promise<any> => {
    const response = await api.get('/ai/models/status');
    return response.data;
  }
};

// Export api instance for direct use
export { api as apiClient };

export default api;
