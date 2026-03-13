import React from 'react';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';
import {
  PuzzlePieceIcon,
  TrophyIcon,
  FireIcon,
  ChartBarIcon,
  SparklesIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';
import { challengeService, userService, analyticsService } from '../services/api';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  // Fetch user progress
  const { data: progress, isLoading: progressLoading } = useQuery(
    ['userProgress', user?.id],
    () => userService.getUserProgress(user!.id),
    { enabled: !!user }
  );

  // Fetch recommended challenges
  const { data: recommendedChallenges, isLoading: challengesLoading } = useQuery(
    'recommendedChallenges',
    () => challengeService.getRecommended(5)
  );

  // Fetch personalized recommendations
  const { data: recommendations } = useQuery(
    'personalizedRecommendations',
    () => analyticsService.getPersonalizedRecommendations(5)
  );

  if (progressLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" text="Loading your dashboard..." />
      </div>
    );
  }

  const stats = [
    {
      name: 'Challenges Solved',
      value: progress?.solved_challenges || 0,
      total: progress?.total_challenges || 0,
      icon: PuzzlePieceIcon,
      color: 'text-blue-600'
    },
    {
      name: 'Current Streak',
      value: user?.streak_days || 0,
      suffix: 'days',
      icon: FireIcon,
      color: 'text-orange-600'
    },
    {
      name: 'Total Points',
      value: user?.total_points || 0,
      icon: TrophyIcon,
      color: 'text-yellow-600'
    },
    {
      name: 'Current Level',
      value: user?.level || 1,
      icon: ChartBarIcon,
      color: 'text-green-600'
    }
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <motion.div
        className="bg-gradient-to-r from-primary-600 to-purple-600 rounded-2xl p-8 text-white"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome back, {user?.display_name || user?.username}!
            </h1>
            <p className="text-blue-100 text-lg">
              Ready to continue your cybersecurity journey?
            </p>
          </div>
          <div className="hidden md:block">
            <SparklesIcon className="h-16 w-16 text-blue-200" />
          </div>
        </div>

        {/* Quick action buttons */}
        <div className="mt-6 flex flex-wrap gap-3">
          <button className="btn-secondary bg-white bg-opacity-20 hover:bg-opacity-30 border-white border-opacity-30">
            <PuzzlePieceIcon className="h-4 w-4 mr-2" />
            Browse Challenges
          </button>
          <button className="btn-secondary bg-white bg-opacity-20 hover:bg-opacity-30 border-white border-opacity-30">
            <ChartBarIcon className="h-4 w-4 mr-2" />
            View Analytics
          </button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.name}
            className="card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <div className="flex items-center">
              <div className={`p-3 rounded-lg bg-gray-100 dark:bg-dark-700 ${stat.color}`}>
                <stat.icon className="h-6 w-6" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {stat.name}
                </p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stat.value}
                  {stat.total && <span className="text-gray-500">/{stat.total}</span>}
                  {stat.suffix && <span className="text-sm text-gray-500 ml-1">{stat.suffix}</span>}
                </p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Recent Activity */}
        <motion.div
          className="card"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
            Recent Activity
          </h2>
          <div className="space-y-4">
            {progress?.recent_activity?.slice(0, 5).map((activity, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className={`p-2 rounded-lg ${
                  activity.status === 'solved'
                    ? 'bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400'
                    : 'bg-yellow-100 text-yellow-600 dark:bg-yellow-900 dark:text-yellow-400'
                }`}>
                  {activity.status === 'solved' ? (
                    <TrophyIcon className="h-4 w-4" />
                  ) : (
                    <ClockIcon className="h-4 w-4" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {activity.challenge_title}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {activity.status === 'solved' ? `+${activity.points_earned} points` : 'In progress'}
                  </p>
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {new Date(activity.timestamp).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Recommended Challenges */}
        <motion.div
          className="card"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
            Recommended for You
          </h2>
          {challengesLoading ? (
            <LoadingSpinner size="md" />
          ) : (
            <div className="space-y-4">
              {recommendedChallenges?.slice(0, 5).map((challenge) => (
                <div key={challenge.id} className="border border-gray-200 dark:border-dark-600 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900 dark:text-white truncate">
                      {challenge.title}
                    </h3>
                    <span className={`badge difficulty-${challenge.difficulty}`}>
                      {challenge.difficulty}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 truncate">
                    {challenge.short_description}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {challenge.points} points
                    </span>
                    <button className="btn-primary text-xs px-3 py-1">
                      Start
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* Progress Overview */}
      <motion.div
        className="card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
      >
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
          Progress by Category
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {progress?.category_breakdown && Object.entries(progress.category_breakdown).map(([category, data]) => (
            <div key={category} className="text-center">
              <div className="mb-2">
                <div className="text-lg font-bold text-gray-900 dark:text-white">
                  {data.solved}/{data.total}
                </div>
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  {category}
                </div>
              </div>
              <div className="w-full bg-gray-200 dark:bg-dark-700 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(data.solved / data.total) * 100}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {Math.round((data.solved / data.total) * 100)}% complete
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;