// ============================================
// Lab Types — Progressive Lab System
// ============================================

export type Difficulty = 'easy' | 'medium' | 'hard';

export type MissionCategory = 'phishing' | 'crypto' | 'web' | 'logic';

export interface PerformanceMetrics {
  completionTime: number;
  wrongAttempts: number;
  hintsUsed: boolean;
  difficulty: Difficulty;
}

export interface AdaptiveConfig {
  timeWeight: number;
  accuracyWeight: number;
  hintPenalty: number;
  difficultyThresholds: {
    increase: number;
    decrease: number;
  };
}

export interface AdaptiveResult {
  performanceScore: number;
  recommendedDifficulty: Difficulty;
  recommendedCategory?: MissionCategory;
  feedback: string;
}

export interface PerformanceStats {
  avgCompletionTime: number;
  avgAccuracy: number;
  totalMissionsCompleted: number;
  categoryScores: Record<MissionCategory, number>;
  currentDifficulty: Difficulty;
  weakestCategory?: MissionCategory;
  strongestCategory?: MissionCategory;
}

export interface TestCase {
  input: string;
  expectedOutput: string;
  description: string;
}

export interface CodeExecutionResult {
  output: string;
  passed: boolean;
  error?: string;
  executionTime: number;
}

export type LabLevel = 1 | 2 | 3 | 4;

export interface LabLevelConfig {
  level: LabLevel;
  name: string;
  description: string;
  icon: string;
  unlockThreshold: number;
}

export interface BlockField {
  name: string;
  type: 'number' | 'text' | 'dropdown';
  default?: string | number;
  options?: [string, string][];
}

export interface BlockDefinition {
  id: string;
  type: string;
  label: string;
  color: string;
  fields?: BlockField[];
  output?: string;
  previousStatement?: boolean;
  nextStatement?: boolean;
}

export interface BlankDefinition {
  id: number;
  answer: string;
  hint?: string;
  caseSensitive?: boolean;
}

export interface LabExercise {
  id: string;
  labId: string;
  level: LabLevel;
  title: string;
  description: string;
  narrative: string;
  category: MissionCategory;
  rewardXP: number;
  blocks?: BlockDefinition[];
  correctBlockOrder?: string[];
  blankTemplate?: string;
  blanks?: BlankDefinition[];
  starterCode?: string;
  solution?: string;
  testCases?: TestCase[];
  hints: string[];
}

export interface LabUserState {
  labId: string;
  unlockedLevel: LabLevel;
  levelScores: Partial<Record<LabLevel, number[]>>;
  totalCompleted: number;
}

export interface LabFeedback {
  type: 'success' | 'level-up' | 'badge';
  title: string;
  message: string;
  xpEarned: number;
  newLevel?: LabLevel;
  badgeId?: string;
}

export interface LabProgress {
  userId: string;
  labId: string;
  exerciseId: string;
  level: LabLevel;
  completed: boolean;
  completionTime: number;
  wrongAttempts: number;
  hintsUsed: number;
  score: number;
  completedAt?: number;
  startedAt: number;
}
