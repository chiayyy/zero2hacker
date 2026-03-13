// ============================================
// Lab Exercises Hook — loads and filters exercises
// ============================================

import { useMemo, useCallback } from 'react';
import { LabExercise, LabLevel } from '../types/lab';
import exercisesData from '../data/lab-exercises.json';

export function useLabExercises() {
  const exercises = useMemo(() => exercisesData as LabExercise[], []);

  const getExercisesByLab = useCallback(
    (labId: string) => exercises.filter((e) => e.labId === labId),
    [exercises]
  );

  const getExercisesByLevel = useCallback(
    (level: LabLevel) => exercises.filter((e) => e.level === level),
    [exercises]
  );

  const getExercise = useCallback(
    (labId: string, level: LabLevel) =>
      exercises.find((e) => e.labId === labId && e.level === level) || null,
    [exercises]
  );

  return {
    exercises,
    getExercisesByLab,
    getExercisesByLevel,
    getExercise,
  };
}
