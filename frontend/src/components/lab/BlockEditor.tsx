import { useState, useCallback, useEffect } from 'react';
import { motion, AnimatePresence, Reorder } from 'framer-motion';
import { BlockDefinition } from '../../types/lab';
import LabButton from './LabButton';
import {
  CheckCircleIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline';

interface BlockEditorProps {
  blocks: BlockDefinition[];
  correctOrder: string[];
  hints: string[];
  onSequenceChange: (sequence: string[]) => void;
  onValidate: () => { correct: boolean; message: string };
  onComplete: () => void;
}

export default function BlockEditor({
  blocks,
  correctOrder,
  hints,
  onSequenceChange,
  onValidate,
  onComplete,
}: BlockEditorProps) {
  const [orderedBlocks, setOrderedBlocks] = useState<BlockDefinition[]>(() => {
    const shuffled = [...blocks];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  });
  const [shaking, setShaking] = useState(false);
  const [correct, setCorrect] = useState(false);
  const [message, setMessage] = useState('');
  const [showHint, setShowHint] = useState(-1);

  useEffect(() => {
    onSequenceChange(orderedBlocks.map((b) => b.id));
  }, [orderedBlocks, onSequenceChange]);

  const handleReorder = useCallback((newOrder: BlockDefinition[]) => {
    setOrderedBlocks(newOrder);
    setMessage('');
    setCorrect(false);
  }, []);

  const handleValidate = useCallback(() => {
    const result = onValidate();
    setMessage(result.message);
    if (result.correct) {
      setCorrect(true);
    } else {
      setShaking(true);
      setTimeout(() => setShaking(false), 500);
    }
  }, [onValidate]);

  const revealHint = () => {
    if (showHint < hints.length - 1) setShowHint((prev) => prev + 1);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-xl p-3 mb-4">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Drag and reorder the blocks into the correct sequence.
        </p>
      </div>

      <div
        className={`flex-1 bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-xl p-4 mb-4 overflow-y-auto min-h-[300px] transition-all ${
          shaking ? 'animate-pulse border-danger-500' : ''
        } ${correct ? 'border-success-500' : ''}`}
      >
        <Reorder.Group
          axis="y"
          values={orderedBlocks}
          onReorder={handleReorder}
          className="space-y-2"
        >
          {orderedBlocks.map((block, index) => {
            const isCorrectPosition = correctOrder[index] === block.id;
            return (
              <Reorder.Item
                key={block.id}
                value={block}
                className={`flex items-center gap-3 p-3 rounded-lg border cursor-grab active:cursor-grabbing transition-colors ${
                  correct && isCorrectPosition
                    ? 'border-success-500/50 bg-success-500/10'
                    : 'border-gray-200 dark:border-dark-600 bg-gray-50 dark:bg-dark-700 hover:border-primary-400'
                }`}
                whileDrag={{ scale: 1.02, boxShadow: '0 4px 20px rgba(59,130,246,0.3)' }}
              >
                <span className="text-xs text-gray-400 w-6 text-center font-mono">
                  {index + 1}
                </span>
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: block.color }}
                />
                <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                  {block.label}
                </span>
                {block.fields?.map((field) => (
                  <span
                    key={field.name}
                    className="text-xs text-warning-600 dark:text-warning-400 bg-warning-500/10 px-2 py-0.5 rounded"
                  >
                    {field.default}
                  </span>
                ))}
              </Reorder.Item>
            );
          })}
        </Reorder.Group>
      </div>

      <div className="flex items-center gap-3 mb-3">
        <LabButton onClick={handleValidate} disabled={correct}>
          <CheckCircleIcon className="w-4 h-4" /> Check Order
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
