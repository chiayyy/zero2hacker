import { motion } from 'framer-motion';
import { LabFeedback } from '../../types/lab';
import LabButton from './LabButton';
import LabCountUp from './LabCountUp';

interface LabFeedbackOverlayProps {
  feedback: LabFeedback;
  onContinue: () => void;
}

export default function LabFeedbackOverlay({ feedback, onContinue }: LabFeedbackOverlayProps) {
  return (
    <motion.div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Particle burst */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {Array.from({ length: 20 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 rounded-full"
            style={{
              background: ['#3b82f6', '#a855f7', '#10b981', '#f59e0b'][i % 4],
              left: '50%',
              top: '50%',
            }}
            initial={{ x: 0, y: 0, opacity: 1, scale: 1 }}
            animate={{
              x: (Math.random() - 0.5) * 400,
              y: (Math.random() - 0.5) * 400,
              opacity: 0,
              scale: 0,
            }}
            transition={{ duration: 1.5, delay: 0.2 + i * 0.03, ease: 'easeOut' }}
          />
        ))}
      </div>

      <motion.div
        className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-2xl p-8 text-center max-w-md mx-4 relative shadow-2xl"
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 20, delay: 0.1 }}
      >
        <motion.div
          className="text-6xl mb-4"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: 'spring', delay: 0.3 }}
        >
          {feedback.type === 'level-up' ? '🚀' : feedback.type === 'badge' ? '🏆' : '✅'}
        </motion.div>

        <h2 className="text-2xl font-bold mb-2 bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
          {feedback.title}
        </h2>

        <p className="text-gray-500 dark:text-gray-400 mb-4">{feedback.message}</p>

        <motion.div
          className="flex items-center justify-center gap-2 mb-4"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <span className="text-warning-500 text-lg font-bold">+</span>
          <span className="text-warning-500 text-2xl font-bold">
            <LabCountUp value={feedback.xpEarned} duration={1} />
          </span>
          <span className="text-warning-500 text-lg font-bold">XP</span>
        </motion.div>

        {feedback.newLevel && (
          <motion.div
            className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3 mb-4"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7 }}
          >
            <span className="text-purple-600 dark:text-purple-400 text-sm font-medium">
              Level {feedback.newLevel} Unlocked!
            </span>
          </motion.div>
        )}

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
        >
          <LabButton onClick={onContinue} size="lg">
            Continue
          </LabButton>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
