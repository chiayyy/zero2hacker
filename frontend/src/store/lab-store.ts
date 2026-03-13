// ============================================
// Lab Store — Progressive Lab State Management
// ============================================

import { create } from 'zustand';
import { LabLevel, LabExercise, LabUserState, LabFeedback } from '../types/lab';

interface LabStore {
  currentLabId: string | null;
  setCurrentLabId: (labId: string | null) => void;
  currentLevel: LabLevel;
  setCurrentLevel: (level: LabLevel) => void;
  currentExercise: LabExercise | null;
  setCurrentExercise: (exercise: LabExercise | null) => void;

  sessionStartTime: number | null;
  startSession: () => void;
  wrongAttempts: number;
  incrementWrongAttempts: () => void;
  hintsUsed: number;
  useHint: () => void;

  labStates: Record<string, LabUserState>;
  setLabState: (labId: string, state: LabUserState) => void;
  initLabState: (labId: string) => void;

  blockSequence: string[];
  setBlockSequence: (sequence: string[]) => void;

  generatedCode: string;
  setGeneratedCode: (code: string) => void;

  blankAnswers: Record<number, string>;
  setBlankAnswer: (blankId: number, value: string) => void;
  resetBlankAnswers: () => void;

  feedback: LabFeedback | null;
  setFeedback: (feedback: LabFeedback | null) => void;

  resetSession: () => void;
}

export const useLabStore = create<LabStore>((set) => ({
  currentLabId: null,
  setCurrentLabId: (labId) => set({ currentLabId: labId }),
  currentLevel: 1,
  setCurrentLevel: (level) => set({ currentLevel: level }),
  currentExercise: null,
  setCurrentExercise: (exercise) => set({ currentExercise: exercise }),

  sessionStartTime: null,
  startSession: () => set({ sessionStartTime: Date.now(), wrongAttempts: 0, hintsUsed: 0 }),
  wrongAttempts: 0,
  incrementWrongAttempts: () => set((s) => ({ wrongAttempts: s.wrongAttempts + 1 })),
  hintsUsed: 0,
  useHint: () => set((s) => ({ hintsUsed: s.hintsUsed + 1 })),

  labStates: {},
  setLabState: (labId, state) =>
    set((s) => ({ labStates: { ...s.labStates, [labId]: state } })),
  initLabState: (labId) =>
    set((s) => {
      if (s.labStates[labId]) return s;
      return {
        labStates: {
          ...s.labStates,
          [labId]: { labId, unlockedLevel: 1, levelScores: {}, totalCompleted: 0 },
        },
      };
    }),

  blockSequence: [],
  setBlockSequence: (sequence) => set({ blockSequence: sequence }),

  generatedCode: '',
  setGeneratedCode: (code) => set({ generatedCode: code }),

  blankAnswers: {},
  setBlankAnswer: (blankId, value) =>
    set((s) => ({ blankAnswers: { ...s.blankAnswers, [blankId]: value } })),
  resetBlankAnswers: () => set({ blankAnswers: {} }),

  feedback: null,
  setFeedback: (feedback) => set({ feedback }),

  resetSession: () =>
    set({
      sessionStartTime: null,
      wrongAttempts: 0,
      hintsUsed: 0,
      blockSequence: [],
      generatedCode: '',
      blankAnswers: {},
      feedback: null,
    }),
}));
