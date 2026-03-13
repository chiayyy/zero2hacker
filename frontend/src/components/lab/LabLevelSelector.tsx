import { motion } from 'framer-motion';
import { LabLevel, LabLevelConfig } from '../../types/lab';
import {
  LockClosedIcon,
  PuzzlePieceIcon,
  CodeBracketIcon,
  PencilSquareIcon,
  Squares2X2Icon,
} from '@heroicons/react/24/outline';
import { CheckIcon } from '@heroicons/react/24/solid';

interface LabLevelSelectorProps {
  levels: LabLevelConfig[];
  unlockedLevel: LabLevel;
  currentLevel: LabLevel;
  onSelectLevel: (level: LabLevel) => void;
}

const levelIcons: Record<string, React.ReactNode> = {
  puzzle: <PuzzlePieceIcon className="w-5 h-5" />,
  split: <Squares2X2Icon className="w-5 h-5" />,
  edit: <PencilSquareIcon className="w-5 h-5" />,
  code: <CodeBracketIcon className="w-5 h-5" />,
};

export default function LabLevelSelector({
  levels,
  unlockedLevel,
  currentLevel,
  onSelectLevel,
}: LabLevelSelectorProps) {
  return (
    <div className="relative flex items-center justify-center gap-0 py-4">
      <div className="absolute top-1/2 left-[10%] right-[10%] h-0.5 bg-gray-200 dark:bg-dark-600 -translate-y-1/2" />

      {levels.map((config, i) => {
        const isUnlocked = config.level <= unlockedLevel;
        const isCurrent = config.level === currentLevel;
        const isCompleted = config.level < unlockedLevel;

        return (
          <div key={config.level} className="relative flex flex-col items-center flex-1">
            {i > 0 && (
              <div
                className={`absolute top-1/2 right-1/2 w-full h-0.5 -translate-y-1/2 transition-colors duration-500 ${
                  isUnlocked ? 'bg-primary-500' : 'bg-gray-200 dark:bg-dark-600'
                }`}
                style={{ zIndex: 0 }}
              />
            )}

            <motion.button
              className={`relative z-10 w-14 h-14 rounded-full flex items-center justify-center border-2 transition-all ${
                isCurrent
                  ? 'border-primary-500 bg-primary-500/20 ring-4 ring-primary-500/20'
                  : isUnlocked
                  ? 'border-primary-400/50 bg-white dark:bg-dark-800 hover:bg-primary-500/10'
                  : 'border-gray-300 dark:border-dark-600 bg-gray-100 dark:bg-dark-800/50 cursor-not-allowed opacity-50'
              }`}
              onClick={() => isUnlocked && onSelectLevel(config.level)}
              whileHover={isUnlocked ? { scale: 1.1 } : {}}
              whileTap={isUnlocked ? { scale: 0.95 } : {}}
              disabled={!isUnlocked}
            >
              {!isUnlocked ? (
                <LockClosedIcon className="w-5 h-5 text-gray-400" />
              ) : isCompleted ? (
                <CheckIcon className="w-5 h-5 text-success-500" />
              ) : (
                <span className={isCurrent ? 'text-primary-500' : 'text-gray-500 dark:text-gray-400'}>
                  {levelIcons[config.icon] || config.level}
                </span>
              )}

              {isCurrent && (
                <motion.div
                  className="absolute inset-0 rounded-full border-2 border-primary-500"
                  animate={{ scale: [1, 1.3, 1], opacity: [0.5, 0, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
            </motion.button>

            <span
              className={`mt-2 text-xs text-center ${
                isCurrent
                  ? 'text-primary-600 dark:text-primary-400 font-bold'
                  : isUnlocked
                  ? 'text-gray-500 dark:text-gray-400'
                  : 'text-gray-400 dark:text-gray-600'
              }`}
            >
              L{config.level}: {config.name}
            </span>
          </div>
        );
      })}
    </div>
  );
}
