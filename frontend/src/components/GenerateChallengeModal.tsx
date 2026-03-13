import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { XMarkIcon, SparklesIcon, BeakerIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';
import api from '../services/api';

interface GeneratedChallenge {
  id: number;
  title: string;
  description: string;
  difficulty: string;
  points: number;
  category_id: number;
  tags?: string[];
}

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onGenerated: (challenge: GeneratedChallenge) => void;
}

const CATEGORY_KEYS = ['cryptography', 'web', 'forensics', 'network', 'binary', 'misc'] as const;

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: 'text-green-600 dark:text-green-400',
  easy: 'text-blue-600 dark:text-blue-400',
  medium: 'text-yellow-600 dark:text-yellow-400',
  hard: 'text-orange-600 dark:text-orange-400',
  expert: 'text-red-600 dark:text-red-400',
};

const CATEGORY_NAMES: Record<string, string> = {
  cryptography: 'Cryptography',
  web: 'Web Security',
  forensics: 'Forensics',
  network: 'Network Security',
  binary: 'Binary / Reversing',
  misc: 'Miscellaneous',
};

const DIFFICULTY_LABELS: Record<string, string> = {
  beginner: 'Beginner',
  easy: 'Easy',
  medium: 'Medium',
  hard: 'Hard',
  expert: 'Expert',
};

const GenerateChallengeModal: React.FC<Props> = ({ isOpen, onClose, onGenerated }) => {

  const [category, setCategory] = useState('cryptography');
  const [difficulty, setDifficulty] = useState('beginner');
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [generated, setGenerated] = useState<GeneratedChallenge | null>(null);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    setLoading(true);
    setError('');
    setGenerated(null);
    try {
      const res = await api.post('/ai/generate-challenge', {
        category,
        difficulty,
        topic: topic.trim() || category,
      });
      const challenge: GeneratedChallenge = res.data;
      setGenerated(challenge);
      onGenerated(challenge);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Generation failed — please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setGenerated(null);
    setError('');
    setTopic('');
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            key="backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            onClick={handleClose}
          />

          {/* Modal */}
          <motion.div
            key="modal"
            initial={{ opacity: 0, scale: 0.93, y: 24 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.93, y: 24 }}
            transition={{ type: 'spring', stiffness: 320, damping: 28 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none"
          >
            <div
              className="bg-white dark:bg-dark-800 rounded-2xl shadow-2xl w-full max-w-md pointer-events-auto
                         border border-gray-200 dark:border-dark-700"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-dark-700">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-gradient-to-br from-primary-500 to-purple-600">
                    <SparklesIcon className="h-5 w-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gray-900 dark:text-white">Generate Challenge</h2>
                    <p className="text-xs text-gray-500 dark:text-gray-400">AI-crafted just for you</p>
                  </div>
                </div>
                <button
                  onClick={handleClose}
                  className="p-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-200
                             hover:bg-gray-100 dark:hover:bg-dark-700 transition-colors"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>

              <div className="p-6 space-y-5">
                {!generated ? (
                  <>
                    {/* Category */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Category
                      </label>
                      <select
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-dark-600
                                   bg-white dark:bg-dark-700 text-gray-900 dark:text-white text-sm
                                   focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      >
                        {CATEGORY_KEYS.map((val) => (
                          <option key={val} value={val}>{CATEGORY_NAMES[val]}</option>
                        ))}
                      </select>
                    </div>

                    {/* Difficulty */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Difficulty
                      </label>
                      <div className="grid grid-cols-5 gap-2">
                        {(['beginner', 'easy', 'medium', 'hard', 'expert'] as const).map((d) => (
                          <button
                            key={d}
                            onClick={() => setDifficulty(d)}
                            className={`py-1.5 text-xs font-medium rounded-lg border transition-all
                              ${difficulty === d
                                ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                                : 'border-gray-200 dark:border-dark-600 text-gray-600 dark:text-gray-400 hover:border-gray-400'
                              }`}
                          >
                            {DIFFICULTY_LABELS[d]}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Topic hint */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                        Topic / Theme <span className="text-gray-400 font-normal">(optional)</span>
                      </label>
                      <input
                        type="text"
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        placeholder="e.g. ancient ciphers, JWT tokens, PNG headers…"
                        className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-dark-600
                                   bg-white dark:bg-dark-700 text-gray-900 dark:text-white text-sm
                                   focus:ring-2 focus:ring-primary-500 focus:border-transparent placeholder-gray-400"
                        maxLength={80}
                        onKeyDown={(e) => e.key === 'Enter' && !loading && handleGenerate()}
                      />
                    </div>

                    {error && (
                      <p className="text-sm text-danger-600 dark:text-danger-400 bg-danger-50 dark:bg-danger-900/20
                                    px-3 py-2 rounded-lg">
                        {error}
                      </p>
                    )}

                    <motion.button
                      onClick={handleGenerate}
                      disabled={loading}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.97 }}
                      className="w-full py-3 rounded-xl font-semibold text-white text-sm
                                 bg-gradient-to-r from-primary-600 to-purple-600
                                 hover:from-primary-700 hover:to-purple-700
                                 disabled:opacity-60 disabled:cursor-not-allowed
                                 flex items-center justify-center gap-2 transition-all"
                    >
                      {loading ? (
                        <>
                          <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24" fill="none">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                          </svg>
                          Generating…
                        </>
                      ) : (
                        <>
                          <SparklesIcon className="h-4 w-4" />
                          Generate Challenge
                        </>
                      )}
                    </motion.button>
                  </>
                ) : (
                  /* Success state */
                  <motion.div
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-4"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-full bg-success-100 dark:bg-success-900/30">
                        <CheckCircleIcon className="h-6 w-6 text-success-600 dark:text-success-400" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-white text-sm">Challenge created!</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Added to your challenge list</p>
                      </div>
                    </div>

                    <div className="rounded-xl border border-gray-200 dark:border-dark-600
                                    bg-gray-50 dark:bg-dark-700 p-4 space-y-2">
                      <div className="flex items-start justify-between gap-2">
                        <h3 className="font-semibold text-gray-900 dark:text-white text-sm leading-snug">
                          {generated.title}
                        </h3>
                        <span className={`text-xs font-medium capitalize shrink-0 ${DIFFICULTY_COLORS[generated.difficulty] || ''}`}>
                          {generated.difficulty}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-3">
                        {generated.description}
                      </p>
                      <div className="flex items-center gap-3 pt-1">
                        <span className="text-xs font-semibold text-primary-600 dark:text-primary-400">
                          {generated.points} pts
                        </span>
                        {generated.tags?.slice(0, 2).map((t) => (
                          <span key={t} className="text-xs px-2 py-0.5 bg-gray-200 dark:bg-dark-600
                                                   text-gray-600 dark:text-gray-300 rounded">
                            {t}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="flex gap-3">
                      <Link
                        to={`/challenges/${generated.id}`}
                        onClick={handleClose}
                        className="flex-1 py-2.5 rounded-xl text-sm font-semibold text-center text-white
                                   bg-gradient-to-r from-primary-600 to-purple-600
                                   hover:from-primary-700 hover:to-purple-700 transition-all"
                      >
                        Start Challenge
                      </Link>
                      <button
                        onClick={() => { setGenerated(null); setTopic(''); }}
                        className="flex-1 py-2.5 rounded-xl text-sm font-medium
                                   border border-gray-300 dark:border-dark-600
                                   text-gray-700 dark:text-gray-300
                                   hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors"
                      >
                        Generate Another
                      </button>
                    </div>
                  </motion.div>
                )}
              </div>

              {!generated && (
                <div className="px-6 pb-4 flex items-center gap-2 text-xs text-gray-400 dark:text-gray-500">
                  <BeakerIcon className="h-3.5 w-3.5 shrink-0" />
                  Challenges are saved permanently to your account.
                </div>
              )}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default GenerateChallengeModal;
