import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { challengeService } from '../services/api';
import { Challenge, ChallengeAttempt } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { toast } from 'react-hot-toast';
import {
  TrophyIcon,
  DocumentTextIcon,
  FolderOpenIcon,
  FlagIcon,
  LightBulbIcon,
  ChartBarIcon,
  CalculatorIcon,
  AcademicCapIcon,
  UsersIcon,
  ClockIcon,
  StarIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

const ChallengeDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [loading, setLoading] = useState(true);
  const [flagInput, setFlagInput] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [hints, setHints] = useState<string[]>([]);
  const [currentHintLevel, setCurrentHintLevel] = useState(0);
  const [loadingHint, setLoadingHint] = useState(false);

  // Timer state
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(true);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Attempts state
  const [userAttempts, setUserAttempts] = useState<ChallengeAttempt[]>([]);
  const [isSolved, setIsSolved] = useState(false);
  const [earnedPoints, setEarnedPoints] = useState(0);

  useEffect(() => {
    if (id) {
      fetchChallenge();
      fetchUserAttempts();
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  // Timer effect
  useEffect(() => {
    if (isTimerRunning && !isSolved) {
      timerRef.current = setInterval(() => {
        setElapsedTime(prev => prev + 1);
      }, 1000);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isTimerRunning, isSolved]);

  const fetchChallenge = async () => {
    try {
      setLoading(true);
      const data = await challengeService.getChallenge(parseInt(id!));
      setChallenge(data);
    } catch (error) {
      console.error('Error fetching challenge:', error);
      toast.error('Failed to load challenge');
      navigate('/challenges');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserAttempts = async () => {
    try {
      const attempts = await challengeService.getAttempts(parseInt(id!));
      setUserAttempts(attempts);

      // Check if already solved
      const solvedAttempt = attempts.find(a => a.is_correct);
      if (solvedAttempt) {
        setIsSolved(true);
        setIsTimerRunning(false);
        setEarnedPoints(solvedAttempt.points_earned);
      }
    } catch (error) {
      console.error('Error fetching attempts:', error);
    }
  };

  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hrs > 0) {
      return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSubmitFlag = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!flagInput.trim()) {
      toast.error('Please enter a flag');
      return;
    }

    try {
      setSubmitting(true);
      const result = await challengeService.submitAttempt(parseInt(id!), flagInput);

      if (result.is_correct) {
        setIsSolved(true);
        setIsTimerRunning(false);
        setEarnedPoints(result.points_earned);
        toast.success(`Correct! You earned ${result.points_earned} points!`);
        setFlagInput('');
        fetchChallenge();
        fetchUserAttempts();
      } else {
        toast.error('Incorrect flag. Try again!');
        fetchUserAttempts();
      }
    } catch (error: any) {
      console.error('Error submitting flag:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit flag');
    } finally {
      setSubmitting(false);
    }
  };

  const handleGetHint = async () => {
    if (!challenge?.hints || currentHintLevel >= challenge.hints.length) {
      toast.error('No more hints available');
      return;
    }

    try {
      setLoadingHint(true);
      const nextLevel = currentHintLevel + 1;
      const result = await challengeService.getHint(parseInt(id!), nextLevel);

      setHints([...hints, result.hint]);
      setCurrentHintLevel(nextLevel);
      toast.success('Hint unlocked! (-15% points penalty)');
    } catch (error) {
      console.error('Error getting hint:', error);
      toast.error('Failed to get hint');
    } finally {
      setLoadingHint(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      beginner: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      easy: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      hard: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      expert: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    };
    return colors[difficulty as keyof typeof colors] || colors.medium;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  if (!challenge) {
    return (
      <div className="card text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">Challenge not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Success Banner */}
      {isSolved && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl p-6 shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <TrophyIcon className="w-10 h-10 text-yellow-300" />
              <div>
                <h3 className="text-xl font-bold">Challenge Completed!</h3>
                <p className="text-green-100">Great job! You've solved this challenge.</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold">+{earnedPoints}</div>
              <div className="text-green-100">points earned</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {challenge.title}
            </h1>
            <span className={`px-3 py-1 text-sm font-medium rounded-full ${getDifficultyColor(challenge.difficulty)}`}>
              {challenge.difficulty}
            </span>
          </div>
          <div className="flex items-center space-x-6 text-sm text-gray-600 dark:text-gray-400">
            <span className="text-primary-600 dark:text-primary-400 font-semibold text-lg">
              {challenge.points} points
            </span>
            <span className="flex items-center gap-1"><UsersIcon className="w-4 h-4" />{challenge.solve_count} solves</span>
            {challenge.estimated_time && <span className="flex items-center gap-1"><ClockIcon className="w-4 h-4" />Est. {challenge.estimated_time} min</span>}
          </div>
        </div>
      </div>

      {/* Timer and Attempts Bar */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800 dark:bg-gray-900 text-white rounded-xl p-4 flex items-center justify-between"
      >
        <div className="flex items-center space-x-8">
          {/* Timer */}
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${isTimerRunning ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`}></div>
            <div>
              <div className="text-xs text-gray-400 uppercase">Time Elapsed</div>
              <div className="text-2xl font-mono font-bold">{formatTime(elapsedTime)}</div>
            </div>
          </div>

          {/* Attempts */}
          <div className="border-l border-gray-600 pl-8">
            <div className="text-xs text-gray-400 uppercase">Your Attempts</div>
            <div className="text-2xl font-bold">{userAttempts.length}</div>
          </div>

          {/* Hints Used */}
          <div className="border-l border-gray-600 pl-8">
            <div className="text-xs text-gray-400 uppercase">Hints Used</div>
            <div className="text-2xl font-bold">{currentHintLevel} / {challenge.hints?.length || 0}</div>
          </div>
        </div>

        {/* Status */}
        <div className={`px-4 py-2 rounded-full font-semibold flex items-center gap-2 ${isSolved ? 'bg-green-600' : 'bg-yellow-600'}`}>
          {isSolved ? <><CheckCircleIcon className="w-4 h-4" /> Solved</> : <><ClockIcon className="w-4 h-4" /> In Progress</>}
        </div>
      </motion.div>

      {/* Tags */}
      {challenge.tags && challenge.tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {challenge.tags.map((tag, index) => (
            <span
              key={index}
              className="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700
                       text-gray-700 dark:text-gray-300 rounded-full"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <motion.div
            className="card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <DocumentTextIcon className="w-5 h-5 text-primary-500" /> Description
            </h2>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
              {challenge.description}
            </p>
          </motion.div>

          {/* Challenge Files */}
          {challenge.files_url && (
            <motion.div
              className="card bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-2 border-blue-200 dark:border-blue-800"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.05 }}
            >
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <FolderOpenIcon className="w-5 h-5 text-blue-500" /> Challenge Files
              </h2>
              <div className="flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                            d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">Challenge Resource File</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">Download to analyze and find the flag</div>
                  </div>
                </div>
                <a
                  href={challenge.files_url?.startsWith('http') ? challenge.files_url : challenge.files_url}
                  download
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg
                           transition-colors duration-200 flex items-center space-x-2 font-semibold"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  <span>Download</span>
                </a>
              </div>
            </motion.div>
          )}

          {/* Flag Submission */}
          <motion.div
            className={`card ${isSolved ? 'opacity-75' : ''}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
          >
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <FlagIcon className="w-5 h-5 text-red-500" /> Submit Flag
            </h2>
            <form onSubmit={handleSubmitFlag} className="space-y-4">
              <div>
                <input
                  type="text"
                  value={flagInput}
                  onChange={(e) => setFlagInput(e.target.value)}
                  placeholder="flag{...} or the flag content"
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent
                           font-mono text-lg"
                  disabled={submitting || isSolved}
                />
              </div>
              <button
                type="submit"
                disabled={submitting || !flagInput.trim() || isSolved}
                className="w-full px-6 py-3 bg-primary-600 hover:bg-primary-700
                         disabled:bg-gray-400 disabled:cursor-not-allowed
                         text-white font-semibold rounded-lg transition-colors duration-200
                         flex items-center justify-center space-x-2"
              >
                {submitting ? (
                  <>
                    <LoadingSpinner />
                    <span>Checking...</span>
                  </>
                ) : isSolved ? (
                  <span>✓ Already Solved</span>
                ) : (
                  <span>Submit Flag</span>
                )}
              </button>
            </form>

            {/* Recent Attempts */}
            {userAttempts.length > 0 && (
              <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
                <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-3">
                  Your Recent Attempts
                </h3>
                <div className="space-y-2 max-h-32 overflow-y-auto">
                  {userAttempts.slice(0, 5).map((attempt, index) => (
                    <div
                      key={attempt.id}
                      className={`flex items-center justify-between p-2 rounded text-sm
                        ${attempt.is_correct
                          ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                          : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300'}`}
                    >
                      <span className="font-mono">{attempt.flag_submitted?.substring(0, 30)}...</span>
                      <span>{attempt.is_correct ? '✓ Correct' : '✗ Wrong'}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>

          {/* Hints */}
          {challenge.hints && challenge.hints.length > 0 && (
            <motion.div
              className="card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <LightBulbIcon className="w-5 h-5 text-yellow-500" /> Hints
                </h2>
                <span className="text-sm text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-3 py-1 rounded-full">
                  {currentHintLevel} / {challenge.hints.length} unlocked
                </span>
              </div>

              <p className="text-sm text-yellow-600 dark:text-yellow-400 mb-4">
                Each hint reduces your final score by 15%
              </p>

              {hints.length > 0 && (
                <div className="space-y-3 mb-4">
                  {hints.map((hint, index) => (
                    <div
                      key={index}
                      className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200
                               dark:border-blue-800 rounded-lg"
                    >
                      <div className="flex items-start space-x-3">
                        <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white
                                       rounded-full flex items-center justify-center text-sm font-semibold">
                          {index + 1}
                        </span>
                        <p className="text-gray-700 dark:text-gray-300">{hint}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {currentHintLevel < challenge.hints.length && !isSolved && (
                <button
                  onClick={handleGetHint}
                  disabled={loadingHint}
                  className="w-full px-4 py-3 bg-yellow-500 hover:bg-yellow-600
                           disabled:bg-gray-400 disabled:cursor-not-allowed
                           text-white rounded-lg transition-colors duration-200 font-semibold"
                >
                  {loadingHint ? 'Loading...' : `Unlock Hint ${currentHintLevel + 1}`}
                </button>
              )}
            </motion.div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Stats */}
          <motion.div
            className="card"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3 }}
          >
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <ChartBarIcon className="w-5 h-5 text-primary-500" /> Statistics
            </h2>
            <dl className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <dt className="text-gray-600 dark:text-gray-400">Points</dt>
                <dd className="font-bold text-xl text-primary-600 dark:text-primary-400">
                  {challenge.points}
                </dd>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <dt className="text-gray-600 dark:text-gray-400">Total Solves</dt>
                <dd className="font-bold text-xl text-gray-900 dark:text-white">
                  {challenge.solve_count}
                </dd>
              </div>
              <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <dt className="text-gray-600 dark:text-gray-400">Total Attempts</dt>
                <dd className="font-bold text-xl text-gray-900 dark:text-white">
                  {challenge.attempt_count}
                </dd>
              </div>
              {challenge.average_rating && (
                <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <dt className="text-gray-600 dark:text-gray-400">Rating</dt>
                  <dd className="font-bold text-xl text-yellow-500">
                    <span className="flex items-center gap-1"><StarIcon className="w-4 h-4" />{challenge.average_rating.toFixed(1)}</span>
                  </dd>
                </div>
              )}
              {challenge.average_solve_time && (
                <div className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <dt className="text-gray-600 dark:text-gray-400">Avg. Solve Time</dt>
                  <dd className="font-bold text-gray-900 dark:text-white">
                    {Math.round(challenge.average_solve_time)} min
                  </dd>
                </div>
              )}
            </dl>
          </motion.div>

          {/* Score Calculator */}
          <motion.div
            className="card bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: 0.05 }}
          >
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <CalculatorIcon className="w-5 h-5 text-purple-500" /> Score Calculator
            </h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Base Points</span>
                <span className="font-semibold">{challenge.points}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Hint Penalty</span>
                <span className="font-semibold text-red-500">-{currentHintLevel * 15}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Time Bonus</span>
                <span className="font-semibold text-green-500">
                  {elapsedTime < (challenge.estimated_time || 30) * 30 ? '+20%' : '0%'}
                </span>
              </div>
              <hr className="border-gray-300 dark:border-gray-600" />
              <div className="flex justify-between text-lg">
                <span className="font-semibold">Estimated Score</span>
                <span className="font-bold text-primary-600">
                  ~{Math.round(challenge.points * Math.max(0.5, 1 - currentHintLevel * 0.15) *
                    (elapsedTime < (challenge.estimated_time || 30) * 30 ? 1.2 : 1))}
                </span>
              </div>
            </div>
          </motion.div>

          {/* Learning Objectives */}
          {challenge.learning_objectives && challenge.learning_objectives.length > 0 && (
            <motion.div
              className="card"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <AcademicCapIcon className="w-5 h-5 text-green-500" /> Learning Objectives
              </h2>
              <ul className="space-y-2">
                {challenge.learning_objectives.map((objective, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <svg
                      className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300 text-sm">{objective}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChallengeDetail;
