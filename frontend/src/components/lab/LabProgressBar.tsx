import { motion } from 'framer-motion';
import { LabLevel } from '../../types/lab';

interface LabProgressBarProps {
  unlockedLevel: LabLevel;
  completedLevels: LabLevel[];
  currentLevel: LabLevel;
}

const levelColors: Record<LabLevel, string> = {
  1: '#3b82f6',
  2: '#a855f7',
  3: '#10b981',
  4: '#f59e0b',
};

const levelNames: Record<LabLevel, string> = {
  1: 'Blocks',
  2: 'Blocks+Code',
  3: 'Fill Blanks',
  4: 'Full Code',
};

export default function LabProgressBar({
  unlockedLevel,
  completedLevels,
  currentLevel,
}: LabProgressBarProps) {
  const levels: LabLevel[] = [1, 2, 3, 4];

  return (
    <div className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-xl p-3">
      <div className="flex items-center gap-1">
        {levels.map((level) => {
          const isCompleted = completedLevels.includes(level);
          const isCurrent = level === currentLevel;
          const isLocked = level > unlockedLevel;

          return (
            <div key={level} className="flex-1 relative">
              <div className="h-2 rounded-full bg-gray-200 dark:bg-dark-600 overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{ background: levelColors[level] }}
                  initial={{ width: '0%' }}
                  animate={{
                    width: isCompleted ? '100%' : isCurrent ? '50%' : isLocked ? '0%' : '10%',
                  }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                />
              </div>
              <span
                className={`text-[10px] mt-1 block text-center ${
                  isCurrent
                    ? 'text-primary-600 dark:text-primary-400'
                    : isLocked
                    ? 'text-gray-400 dark:text-gray-600'
                    : 'text-gray-500 dark:text-gray-400'
                }`}
              >
                {levelNames[level]}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
