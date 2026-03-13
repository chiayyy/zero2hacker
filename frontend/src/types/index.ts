// User Types
export interface User {
  id: number;
  firebase_uid: string;
  email: string;
  username: string;
  display_name?: string;
  role: 'student' | 'educator' | 'admin';
  skill_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  experience_months: number;
  bio?: string;
  avatar_url?: string;
  total_points: number;
  level: number;
  badges?: string[];
  streak_days: number;
  last_activity?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  preferred_categories?: string[];
  learning_style?: string;
}

// Challenge Types
export interface Challenge {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description?: string;
  category_id: number;
  category?: Category;
  difficulty: 'beginner' | 'easy' | 'medium' | 'hard' | 'expert';
  points: number;
  estimated_time?: number;
  flag?: string;
  hints?: string[];
  solution?: string;
  writeup?: string;
  files_url?: string;
  docker_image?: string;
  docker_port?: number;
  container_config?: any;
  tags?: string[];
  learning_objectives?: string[];
  status: 'draft' | 'active' | 'retired' | 'maintenance';
  solve_count: number;
  attempt_count: number;
  average_rating?: number;
  average_solve_time?: number;
  generated_by_ai: boolean;
  ai_model_used?: string;
  quality_score?: number;
  prerequisite_challenges?: number[];
  created_at: string;
  updated_at?: string;
  published_at?: string;
}

export interface ChallengeAttempt {
  id: number;
  user_id: number;
  challenge_id: number;
  status: 'in_progress' | 'solved' | 'failed' | 'timeout';
  flag_submitted?: string;
  is_correct: boolean;
  points_earned: number;
  started_at: string;
  completed_at?: string;
  time_spent?: number;
  hints_used: number;
}

// Category Types
export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  icon?: string;
  color?: string;
  is_active: boolean;
  sort_order: number;
  created_at: string;
}

// Analytics Types
export interface UserAnalytics {
  id: number;
  user_id: number;
  current_skill_level: string;
  preferred_difficulty?: string;
  avg_session_duration?: number;
  learning_velocity?: number;
  total_challenges_attempted: number;
  total_challenges_solved: number;
  solve_rate: number;
  avg_solve_time?: number;
  fastest_solve_time?: number;
  total_login_days: number;
  consecutive_days: number;
  last_login?: string;
  total_time_spent: number;
  strengths?: string[];
  weaknesses?: string[];
  category_performance?: Record<string, any>;
  favorite_categories?: string[];
  recommended_challenges?: number[];
  recommended_topics?: string[];
  created_at: string;
  updated_at?: string;
}

export interface LearningProgress {
  total_challenges: number;
  solved_challenges: number;
  current_streak: number;
  points_earned: number;
  skill_progression: Record<string, any>;
  recent_activity: Array<{
    challenge_title: string;
    status: string;
    points_earned: number;
    timestamp: string;
    time_spent?: number;
  }>;
  category_breakdown: Record<string, {
    solved: number;
    total: number;
  }>;
}

export interface LeaderboardEntry {
  user_id: number;
  username: string;
  display_name?: string;
  total_points: number;
  level: number;
  solve_count: number;
  rank: number;
  avatar_url?: string;
}

// API Response Types
export interface ApiResponse<T> {
  data?: T;
  message?: string;
  error?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Form Types
export interface LoginForm {
  email: string;
  password: string;
}

export interface RegisterForm {
  email: string;
  password: string;
  username: string;
  display_name?: string;
  skill_level: string;
  experience_months: number;
}

export interface ChallengeSubmission {
  flag: string;
}

// Theme Types
export interface Theme {
  darkMode: boolean;
  primaryColor: string;
  accentColor: string;
}

// Notification Types
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

// AI Types
export interface AIHint {
  hint: string;
  level: number;
}

export interface AIFeedback {
  feedback: string;
  suggestions?: string[];
}

export interface SkillAssessment {
  overall_skill_level: string;
  strengths: string[];
  weaknesses: string[];
  recommended_focus: string[];
  confidence_score: number;
}

// Container Types
export interface ChallengeContainer {
  container_id: string;
  port: number;
  url: string;
  status: 'starting' | 'running' | 'stopped' | 'error';
}
