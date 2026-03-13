// ============================================
// Lab Session Hook — manages lab session lifecycle
// ============================================

import { useCallback } from 'react';
import { LabLevel, LabFeedback } from '../types/lab';
import { useLabStore } from '../store/lab-store';
import { useLabExercises } from './useLabExercises';
import { useTimer } from './useTimer';
import {
  computeLabPerformance,
  shouldUnlockNextLevel,
  getLabLevelConfigs,
} from '../lib/lab-engine';
import { validateLabExercise, LabValidationResult } from '../lib/lab-validator';
import { calculateXPReward } from '../lib/xp-system';
import api from '../services/api';

export function useLabSession() {
  const {
    currentLabId,
    currentLevel,
    currentExercise,
    wrongAttempts,
    hintsUsed,
    blockSequence,
    blankAnswers,
    labStates,
    setCurrentLabId,
    setCurrentLevel,
    setCurrentExercise,
    startSession,
    incrementWrongAttempts,
    useHint: useLabHint,
    setBlockSequence,
    setBlankAnswer,
    resetBlankAnswers,
    setLabState,
    initLabState,
    setFeedback,
    setGeneratedCode,
    resetSession,
  } = useLabStore();

  const { getExercise } = useLabExercises();
  const timer = useTimer({ autoStart: false });

  const startLab = useCallback(
    async (labId: string, level: LabLevel) => {
      initLabState(labId);
      setCurrentLabId(labId);
      setCurrentLevel(level);

      const exercise = getExercise(labId, level);
      setCurrentExercise(exercise);

      resetSession();
      startSession();
      timer.reset();
      timer.start();

      // Load saved progress from backend
      try {
        const response = await api.get(`/labs/${labId}/progress`);
        if (response.data) {
          const savedState = response.data;
          setLabState(labId, {
            labId,
            unlockedLevel: savedState.unlocked_level || 1,
            levelScores: savedState.level_scores || {},
            totalCompleted: savedState.total_completed || 0,
          });
        }
      } catch {
        // No saved progress yet, use defaults
      }
    },
    [initLabState, setCurrentLabId, setCurrentLevel, getExercise, setCurrentExercise, resetSession, startSession, timer, setLabState]
  );

  const submitExercise = useCallback(
    (code?: string): LabValidationResult => {
      if (!currentExercise) {
        return { correct: false, message: 'No exercise loaded.' };
      }

      const result = validateLabExercise(currentExercise, currentLevel, {
        blockSequence,
        blankAnswers,
        code,
      });

      if (!result.correct) {
        incrementWrongAttempts();
      }

      return result;
    },
    [currentExercise, currentLevel, blockSequence, blankAnswers, incrementWrongAttempts]
  );

  const completeExercise = useCallback(
    (_code?: string) => {
      if (!currentExercise || !currentLabId) return;

      timer.pause();
      const completionTime = timer.time;

      const performanceScore = computeLabPerformance(
        completionTime,
        wrongAttempts,
        hintsUsed > 0,
        currentLevel
      );

      const xpEarned = calculateXPReward(
        currentExercise.rewardXP,
        currentLevel <= 2 ? 'easy' : currentLevel === 3 ? 'medium' : 'hard',
        completionTime,
        wrongAttempts,
        hintsUsed
      );

      const labState = labStates[currentLabId] || {
        labId: currentLabId,
        unlockedLevel: 1 as LabLevel,
        levelScores: {},
        totalCompleted: 0,
      };

      const prevScores = labState.levelScores[currentLevel] || [];
      const newScores = [...prevScores, performanceScore];
      const updatedState = {
        ...labState,
        levelScores: { ...labState.levelScores, [currentLevel]: newScores },
        totalCompleted: labState.totalCompleted + 1,
      };

      const canUnlock = shouldUnlockNextLevel(updatedState, currentLevel);
      let newLevel: LabLevel | undefined;

      if (canUnlock && currentLevel < 4) {
        const nextLevel = (currentLevel + 1) as LabLevel;
        if (nextLevel > updatedState.unlockedLevel) {
          updatedState.unlockedLevel = nextLevel;
          newLevel = nextLevel;
        }
      }

      setLabState(currentLabId, updatedState);

      // Save progress to backend
      api.post(`/labs/${currentLabId}/progress`, {
        unlocked_level: updatedState.unlockedLevel,
        level_scores: updatedState.levelScores,
        total_completed: updatedState.totalCompleted,
      }).catch(() => {
        // Silently ignore backend errors for lab progress
      });

      const feedback: LabFeedback = {
        type: newLevel ? 'level-up' : 'success',
        title: newLevel ? 'Level Up!' : 'Exercise Complete',
        message: newLevel
          ? `You've unlocked Level ${newLevel}: ${getLabLevelConfigs().find((c) => c.level === newLevel)?.name}!`
          : 'Great work! Exercise completed successfully.',
        xpEarned,
        newLevel,
      };

      setFeedback(feedback);
    },
    [
      currentExercise,
      currentLabId,
      currentLevel,
      timer,
      wrongAttempts,
      hintsUsed,
      labStates,
      setLabState,
      setFeedback,
    ]
  );

  const exitLab = useCallback(() => {
    timer.pause();
    resetSession();
    setCurrentLabId(null);
    setCurrentExercise(null);
  }, [timer, resetSession, setCurrentLabId, setCurrentExercise]);

  return {
    currentLabId,
    currentLevel,
    currentExercise,
    wrongAttempts,
    hintsUsed,
    blockSequence,
    blankAnswers,
    labStates,
    timer,

    startLab,
    submitExercise,
    completeExercise,
    exitLab,
    setCurrentLevel,
    setBlockSequence,
    setBlankAnswer,
    resetBlankAnswers,
    useHint: useLabHint,
    setGeneratedCode,
  };
}
