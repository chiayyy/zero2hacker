import React, { useState, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  BeakerIcon,
  ArrowLeftIcon,
  LockClosedIcon,
  PuzzlePieceIcon,
} from '@heroicons/react/24/outline';
import { useLabStore } from '../store/lab-store';
import { useLabSession } from '../hooks/useLabSession';
import { useLabExercises } from '../hooks/useLabExercises';
import { getLabLevelConfigs, generateCodeFromBlocks } from '../lib/lab-engine';
import { LabLevel } from '../types/lab';
import LabLevelSelector from '../components/lab/LabLevelSelector';
import BlockEditor from '../components/lab/BlockEditor';
import CodePreview from '../components/lab/CodePreview';
import FillInBlank from '../components/lab/FillInBlank';
import LabCodeEditor from '../components/lab/LabCodeEditor';
import LabFeedbackOverlay from '../components/lab/LabFeedbackOverlay';
import LabProgressBar from '../components/lab/LabProgressBar';

interface LabMeta {
  labId: string;
  title: string;
  description: string;
  narrative: string;
  category: string;
}

const categoryColors: Record<string, string> = {
  crypto: 'text-purple-600 dark:text-purple-400 bg-purple-500/10',
  web: 'text-blue-600 dark:text-blue-400 bg-blue-500/10',
  logic: 'text-green-600 dark:text-green-400 bg-green-500/10',
  phishing: 'text-red-600 dark:text-red-400 bg-red-500/10',
};

const Lab: React.FC = () => {
  const [selectedLab, setSelectedLab] = useState<LabMeta | null>(null);

  const { exercises } = useLabExercises();
  const {
    currentLabId,
    currentLevel,
    currentExercise,
    blankAnswers,
    labStates,
    startLab,
    submitExercise,
    completeExercise,
    exitLab,
    setBlockSequence,
    setBlankAnswer,
    setGeneratedCode,
  } = useLabSession();

  const feedback = useLabStore((s) => s.feedback);
  const setFeedback = useLabStore((s) => s.setFeedback);
  const initLabState = useLabStore((s) => s.initLabState);
  const generatedCode = useLabStore((s) => s.generatedCode);

  const levelConfigs = getLabLevelConfigs();

  // Derive unique labs from exercises (using level 1 as metadata source)
  const labs = useMemo<LabMeta[]>(() => {
    const seen = new Set<string>();
    const result: LabMeta[] = [];
    for (const ex of exercises) {
      if (ex.level === 1 && !seen.has(ex.labId)) {
        seen.add(ex.labId);
        // Extract base title (remove "— Block Builder" suffix)
        const baseTitle = ex.title.split('—')[0].trim();
        result.push({
          labId: ex.labId,
          title: baseTitle,
          description: ex.description,
          narrative: ex.narrative,
          category: ex.category,
        });
      }
    }
    return result;
  }, [exercises]);

  const getLabUnlockedLevel = (labId: string): LabLevel =>
    labStates[labId]?.unlockedLevel || 1;

  const getCompletedLevels = (labId: string): LabLevel[] => {
    const state = labStates[labId];
    if (!state) return [];
    return ([1, 2, 3, 4] as LabLevel[]).filter((level) => {
      const scores = state.levelScores[level] || [];
      return scores.length > 0 && scores.some((s) => s > 0);
    });
  };

  const handleSelectLab = useCallback(
    (lab: LabMeta) => {
      setSelectedLab(lab);
      initLabState(lab.labId);
    },
    [initLabState]
  );

  const handleSelectLevel = useCallback(
    (level: LabLevel) => {
      if (!selectedLab) return;
      startLab(selectedLab.labId, level);
    },
    [selectedLab, startLab]
  );

  const handleSequenceChange = useCallback(
    (sequence: string[]) => {
      setBlockSequence(sequence);
      if (currentExercise && currentLevel === 2) {
        const code = generateCodeFromBlocks(currentExercise, sequence);
        setGeneratedCode(code);
      }
    },
    [setBlockSequence, currentExercise, currentLevel, setGeneratedCode]
  );

  const handleBlockValidate = useCallback(() => submitExercise(), [submitExercise]);
  const handleBlockComplete = useCallback(() => completeExercise(), [completeExercise]);
  const handleBlankValidate = useCallback(() => submitExercise(), [submitExercise]);
  const handleBlankComplete = useCallback(() => completeExercise(), [completeExercise]);
  const handleCodeValidate = useCallback((code: string) => submitExercise(code), [submitExercise]);
  const handleCodeComplete = useCallback((code: string) => completeExercise(code), [completeExercise]);

  const handleFeedbackContinue = useCallback(() => {
    setFeedback(null);
  }, [setFeedback]);

  const handleBackToListing = useCallback(() => {
    exitLab();
    setSelectedLab(null);
  }, [exitLab]);

  const handleBackToLevels = useCallback(() => {
    exitLab();
  }, [exitLab]);

  // ---- RENDER: Active exercise ----
  if (currentExercise && currentLabId) {
    return (
      <div className="space-y-6">
        <AnimatePresence>
          {feedback && (
            <LabFeedbackOverlay feedback={feedback} onContinue={handleFeedbackContinue} />
          )}
        </AnimatePresence>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
        >
          {/* Header */}
          <div className="flex items-center gap-4 mb-6">
            <button
              onClick={handleBackToLevels}
              className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
            >
              <ArrowLeftIcon className="w-4 h-4" /> Back to Levels
            </button>
            <div className="flex-1">
              <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">
                {currentExercise.title}
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {currentExercise.description}
              </p>
            </div>
            <span className="text-xs text-primary-600 dark:text-primary-400 font-mono bg-primary-500/10 px-2 py-1 rounded-full">
              Level {currentLevel}
            </span>
          </div>

          {/* Narrative */}
          <div className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-xl p-4 mb-6">
            <p className="text-sm text-gray-600 dark:text-gray-400 italic">
              {currentExercise.narrative}
            </p>
          </div>

          {/* Level-specific content */}
          <div className="min-h-[400px]">
            {currentLevel === 1 && currentExercise.blocks && currentExercise.correctBlockOrder && (
              <BlockEditor
                blocks={currentExercise.blocks}
                correctOrder={currentExercise.correctBlockOrder}
                hints={currentExercise.hints}
                onSequenceChange={handleSequenceChange}
                onValidate={handleBlockValidate}
                onComplete={handleBlockComplete}
              />
            )}

            {currentLevel === 2 && currentExercise.blocks && currentExercise.correctBlockOrder && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <BlockEditor
                  blocks={currentExercise.blocks}
                  correctOrder={currentExercise.correctBlockOrder}
                  hints={currentExercise.hints}
                  onSequenceChange={handleSequenceChange}
                  onValidate={handleBlockValidate}
                  onComplete={handleBlockComplete}
                />
                <CodePreview code={generatedCode} />
              </div>
            )}

            {currentLevel === 3 && currentExercise.blankTemplate && currentExercise.blanks && (
              <FillInBlank
                template={currentExercise.blankTemplate}
                blanks={currentExercise.blanks}
                hints={currentExercise.hints}
                answers={blankAnswers}
                onAnswerChange={setBlankAnswer}
                onValidate={handleBlankValidate}
                onComplete={handleBlankComplete}
              />
            )}

            {currentLevel === 4 && (
              <LabCodeEditor
                starterCode={currentExercise.starterCode || ''}
                testCases={currentExercise.testCases}
                hints={currentExercise.hints}
                onValidate={handleCodeValidate}
                onComplete={handleCodeComplete}
              />
            )}
          </div>
        </motion.div>
      </div>
    );
  }

  // ---- RENDER: Lab detail (level selector) ----
  if (selectedLab) {
    const labId = selectedLab.labId;
    const unlockedLevel = getLabUnlockedLevel(labId);
    const completedLevels = getCompletedLevels(labId);

    return (
      <div className="space-y-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {/* Header */}
          <div className="flex items-center gap-4 mb-6">
            <button
              onClick={handleBackToListing}
              className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
            >
              <ArrowLeftIcon className="w-4 h-4" /> Back to Labs
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {selectedLab.title}
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400">{selectedLab.description}</p>
            </div>
          </div>

          {/* Narrative */}
          <div className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-xl p-4 mb-6">
            <p className="text-sm text-gray-600 dark:text-gray-400 italic">{selectedLab.narrative}</p>
          </div>

          {/* Level Selector */}
          <div className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-2xl p-6 mb-6">
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-1">
              Choose Your Level
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
              Progress through levels to master this challenge. Higher levels unlock as you perform well.
            </p>
            <LabLevelSelector
              levels={levelConfigs}
              unlockedLevel={unlockedLevel}
              currentLevel={unlockedLevel}
              onSelectLevel={handleSelectLevel}
            />
          </div>

          {/* Progress Bar */}
          <div className="mb-6">
            <LabProgressBar
              unlockedLevel={unlockedLevel}
              completedLevels={completedLevels}
              currentLevel={unlockedLevel}
            />
          </div>

          {/* Level cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {levelConfigs.map((config) => {
              const isUnlocked = config.level <= unlockedLevel;
              const isCompleted = completedLevels.includes(config.level);

              return (
                <motion.button
                  key={config.level}
                  className={`bg-white dark:bg-dark-800 border rounded-xl p-4 text-left transition-all ${
                    isUnlocked
                      ? 'border-gray-200 dark:border-dark-700 hover:border-primary-400 hover:shadow-md cursor-pointer'
                      : 'border-gray-200 dark:border-dark-700 opacity-50 cursor-not-allowed'
                  } ${isCompleted ? 'border-success-500/40' : ''}`}
                  onClick={() => isUnlocked && handleSelectLevel(config.level)}
                  whileHover={isUnlocked ? { scale: 1.02 } : {}}
                  whileTap={isUnlocked ? { scale: 0.98 } : {}}
                  disabled={!isUnlocked}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-primary-600 dark:text-primary-400 font-medium">
                      Level {config.level}
                    </span>
                    {!isUnlocked && <LockClosedIcon className="w-4 h-4 text-gray-400" />}
                    {isCompleted && (
                      <span className="text-xs text-success-600 dark:text-success-400">✓ Done</span>
                    )}
                  </div>
                  <div className="text-sm font-bold text-gray-900 dark:text-gray-100 mb-1">
                    {config.name}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {config.description}
                  </div>
                </motion.button>
              );
            })}
          </div>
        </motion.div>
      </div>
    );
  }

  // ---- RENDER: Lab listing ----
  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        className="bg-gradient-to-r from-primary-600 to-purple-600 rounded-2xl p-8 text-white"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex items-center gap-3 mb-2">
          <BeakerIcon className="w-8 h-8" />
          <h1 className="text-3xl font-bold">Lab Mode</h1>
        </div>
        <p className="text-white/80">
          Progressive coding challenges — from visual blocks to full code. Master each concept step by step.
        </p>
      </motion.div>

      {/* Lab grid */}
      <motion.div
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
      >
        {labs.map((lab, i) => {
          const unlockedLevel = getLabUnlockedLevel(lab.labId);
          const completedLevels = getCompletedLevels(lab.labId);
          const categoryStyle = categoryColors[lab.category] || 'text-gray-600 bg-gray-500/10';

          return (
            <motion.div
              key={lab.labId}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-2xl p-6 hover:border-primary-400 hover:shadow-lg transition-all cursor-pointer group"
              onClick={() => handleSelectLab(lab)}
            >
              {/* Top row */}
              <div className="flex items-start justify-between mb-3">
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${categoryStyle}`}>
                  {lab.category}
                </span>
                <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400">
                  <span className="font-medium text-primary-600 dark:text-primary-400">
                    Lvl {unlockedLevel}
                  </span>
                  <span>/4</span>
                </div>
              </div>

              {/* Title */}
              <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                {lab.title}
              </h3>

              {/* Description */}
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 line-clamp-2">
                {lab.description}
              </p>

              {/* Level progress pills */}
              <div className="flex gap-1">
                {([1, 2, 3, 4] as LabLevel[]).map((level) => {
                  const isCompleted = completedLevels.includes(level);
                  const isUnlocked = level <= unlockedLevel;
                  return (
                    <div
                      key={level}
                      className={`flex-1 h-1.5 rounded-full transition-all ${
                        isCompleted
                          ? 'bg-success-500'
                          : isUnlocked
                          ? 'bg-primary-500'
                          : 'bg-gray-200 dark:bg-dark-600'
                      }`}
                    />
                  );
                })}
              </div>

              {/* CTA */}
              <div className="mt-4 flex items-center gap-2 text-sm text-primary-600 dark:text-primary-400 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                <PuzzlePieceIcon className="w-4 h-4" />
                <span>Start Lab</span>
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {labs.length === 0 && (
        <div className="text-center text-gray-500 dark:text-gray-400 py-16">
          No lab challenges available yet.
        </div>
      )}
    </div>
  );
};

export default Lab;
