import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { BlankDefinition } from '../../types/lab';
import LabButton from './LabButton';
import { CheckCircleIcon, LightBulbIcon } from '@heroicons/react/24/outline';

interface FillInBlankProps {
  template: string;
  blanks: BlankDefinition[];
  hints: string[];
  answers: Record<number, string>;
  onAnswerChange: (blankId: number, value: string) => void;
  onValidate: () => { correct: boolean; message: string; details?: Record<string, boolean> };
  onComplete: () => void;
}

export default function FillInBlank({
  template,
  blanks,
  hints,
  answers,
  onAnswerChange,
  onValidate,
  onComplete,
}: FillInBlankProps) {
  const [blankResults, setBlankResults] = useState<Record<number, boolean>>({});
  const [correct, setCorrect] = useState(false);
  const [message, setMessage] = useState('');
  const [showHint, setShowHint] = useState(-1);
  const [blankHints, setBlankHints] = useState<Record<number, boolean>>({});

  const handleValidate = useCallback(() => {
    const result = onValidate();
    setMessage(result.message);
    if (result.correct) {
      setCorrect(true);
      const allCorrect: Record<number, boolean> = {};
      blanks.forEach((b) => (allCorrect[b.id] = true));
      setBlankResults(allCorrect);
    } else if (result.details) {
      const results: Record<number, boolean> = {};
      for (const [key, val] of Object.entries(result.details)) {
        results[Number(key)] = val;
      }
      setBlankResults(results);
    }
  }, [onValidate, blanks]);

  const toggleBlankHint = (blankId: number) => {
    setBlankHints((prev) => ({ ...prev, [blankId]: !prev[blankId] }));
  };

  const revealHint = () => {
    if (showHint < hints.length - 1) setShowHint((prev) => prev + 1);
  };

  const renderTemplate = () => {
    const parts = template.split(/(___BLANK_\d+___)/g);
    return (
      <pre className="font-mono text-sm leading-relaxed whitespace-pre-wrap text-gray-800 dark:text-gray-200">
        {parts.map((part, i) => {
          const blankMatch = part.match(/___BLANK_(\d+)___/);
          if (blankMatch) {
            const blankId = parseInt(blankMatch[1]);
            const blank = blanks.find((b) => b.id === blankId);
            const result = blankResults[blankId];
            const hasResult = blankId in blankResults;

            return (
              <span key={i} className="inline-block relative mx-1 align-middle">
                <input
                  type="text"
                  value={answers[blankId] || ''}
                  onChange={(e) => onAnswerChange(blankId, e.target.value)}
                  disabled={correct}
                  className={`inline-block rounded px-2 py-0.5 font-mono text-sm border bg-gray-100 dark:bg-dark-700 outline-none transition-colors ${
                    hasResult
                      ? result
                        ? 'border-success-500 bg-success-500/10 text-success-700 dark:text-success-400'
                        : 'border-danger-500 bg-danger-500/10 text-danger-700 dark:text-danger-400'
                      : 'border-gray-300 dark:border-dark-500 focus:border-primary-500'
                  }`}
                  placeholder={`blank ${blankId + 1}`}
                  style={{ width: `${Math.max((answers[blankId]?.length || 8) + 2, 8)}ch` }}
                />
                {blank?.hint && (
                  <button
                    onClick={() => toggleBlankHint(blankId)}
                    className="absolute -top-1 -right-5 text-warning-500 hover:text-warning-400 text-xs font-bold"
                    title="Show hint"
                  >
                    ?
                  </button>
                )}
                {blankHints[blankId] && blank?.hint && (
                  <motion.div
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute top-full left-0 mt-1 text-xs text-warning-600 dark:text-warning-400 bg-white dark:bg-dark-800 border border-warning-500/30 rounded px-2 py-1 whitespace-nowrap z-10 shadow-lg"
                  >
                    {blank.hint}
                  </motion.div>
                )}
              </span>
            );
          }
          return <span key={i}>{part}</span>;
        })}
      </pre>
    );
  };

  return (
    <div className="flex flex-col h-full">
      <div className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-xl p-3 mb-4">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Fill in the blanks with the correct values.
        </p>
      </div>

      <div className="flex-1 bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-600 rounded-xl p-6 mb-4 overflow-y-auto min-h-[300px]">
        {renderTemplate()}
      </div>

      <div className="flex items-center gap-3 mb-3">
        <LabButton onClick={handleValidate} disabled={correct}>
          <CheckCircleIcon className="w-4 h-4" /> Check Answers
        </LabButton>
        <LabButton variant="ghost" size="sm" onClick={revealHint} disabled={showHint >= hints.length - 1}>
          <LightBulbIcon className="w-4 h-4" /> Hint
        </LabButton>
        {correct && (
          <LabButton variant="secondary" onClick={onComplete}>
            Continue
          </LabButton>
        )}
      </div>

      <AnimatePresence>
        {message && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`text-sm p-3 rounded-lg mb-3 ${
              correct
                ? 'bg-success-500/10 text-success-600 dark:text-success-400 border border-success-500/20'
                : 'bg-danger-500/10 text-danger-600 dark:text-danger-400 border border-danger-500/20'
            }`}
          >
            {message}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showHint >= 0 && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
            {hints.slice(0, showHint + 1).map((hint, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-warning-600 dark:text-warning-400 mb-1">
                <LightBulbIcon className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>{hint}</span>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
