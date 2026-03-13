import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { analyticsService, userService } from '../services/api';
import { UserAnalytics, LearningProgress } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts';

const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899', '#f43f5e'];

const Analytics: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [progress, setProgress] = useState<LearningProgress | null>(null);

  useEffect(() => {
    if (user) {
      fetchData();
    }
  }, [user]);

  const fetchData = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const [analyticsData, progressData] = await Promise.all([
        analyticsService.getUserAnalytics(user.id),
        userService.getUserProgress(user.id),
      ]);
      setAnalytics(analyticsData);
      setProgress(progressData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mock data for charts (in real app, this would come from API)
  const activityData = [
    { day: 'Mon', challenges: 3, points: 150 },
    { day: 'Tue', challenges: 2, points: 100 },
    { day: 'Wed', challenges: 5, points: 250 },
    { day: 'Thu', challenges: 1, points: 50 },
    { day: 'Fri', challenges: 4, points: 200 },
    { day: 'Sat', challenges: 6, points: 300 },
    { day: 'Sun', challenges: 2, points: 100 },
  ];

  const categoryData = progress?.category_breakdown
    ? Object.entries(progress.category_breakdown).map(([name, data]) => ({
        name,
        solved: data.solved,
        total: data.total,
        percentage: data.total > 0 ? Math.round((data.solved / data.total) * 100) : 0,
      }))
    : [
        { name: 'Cryptography', solved: 5, total: 10, percentage: 50 },
        { name: 'Web Security', solved: 3, total: 8, percentage: 38 },
        { name: 'Forensics', solved: 2, total: 6, percentage: 33 },
        { name: 'Steganography', solved: 4, total: 7, percentage: 57 },
        { name: 'Network', solved: 1, total: 5, percentage: 20 },
      ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Learning Analytics
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Track your progress and identify areas for improvement
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white"
        >
          <div className="text-3xl font-bold">{analytics?.total_challenges_solved || 0}</div>
          <div className="text-blue-100 text-sm">Challenges Solved</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card bg-gradient-to-br from-green-500 to-green-600 text-white"
        >
          <div className="text-3xl font-bold">{Math.round((analytics?.solve_rate || 0) * 100)}%</div>
          <div className="text-green-100 text-sm">Success Rate</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white"
        >
          <div className="text-3xl font-bold">{analytics?.avg_solve_time ? `${Math.round(analytics.avg_solve_time)}m` : 'N/A'}</div>
          <div className="text-purple-100 text-sm">Avg. Solve Time</div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card bg-gradient-to-br from-orange-500 to-orange-600 text-white"
        >
          <div className="text-3xl font-bold">{analytics?.consecutive_days || 0}</div>
          <div className="text-orange-100 text-sm">Day Streak</div>
        </motion.div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Activity Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Weekly Activity
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={activityData}>
                <defs>
                  <linearGradient id="colorPoints" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                <XAxis dataKey="day" className="text-gray-600 dark:text-gray-400" />
                <YAxis className="text-gray-600 dark:text-gray-400" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(17, 24, 39, 0.9)',
                    border: 'none',
                    borderRadius: '8px',
                    color: 'white',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="points"
                  stroke="#6366f1"
                  fillOpacity={1}
                  fill="url(#colorPoints)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Category Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Category Progress
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                <XAxis type="number" domain={[0, 100]} unit="%" />
                <YAxis dataKey="name" type="category" width={100} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(17, 24, 39, 0.9)',
                    border: 'none',
                    borderRadius: '8px',
                    color: 'white',
                  }}
                  formatter={(value: number) => [`${value}%`, 'Progress']}
                />
                <Bar dataKey="percentage" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <span className="text-2xl mr-2">💪</span> Strengths
          </h3>
          {analytics?.strengths && analytics.strengths.length > 0 ? (
            <ul className="space-y-3">
              {analytics.strengths.map((strength, index) => (
                <li key={index} className="flex items-center space-x-3">
                  <span className="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center text-green-600 dark:text-green-400">
                    ✓
                  </span>
                  <span className="text-gray-700 dark:text-gray-300">{strength}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-center py-6">
              <p className="text-gray-500 dark:text-gray-400">
                Complete more challenges to discover your strengths!
              </p>
            </div>
          )}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
            <span className="text-2xl mr-2">🎯</span> Areas to Improve
          </h3>
          {analytics?.weaknesses && analytics.weaknesses.length > 0 ? (
            <ul className="space-y-3">
              {analytics.weaknesses.map((weakness, index) => (
                <li key={index} className="flex items-center space-x-3">
                  <span className="w-8 h-8 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center text-yellow-600 dark:text-yellow-400">
                    !
                  </span>
                  <span className="text-gray-700 dark:text-gray-300">{weakness}</span>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-center py-6">
              <p className="text-gray-500 dark:text-gray-400">
                Keep practicing to identify areas for improvement!
              </p>
            </div>
          )}
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Recent Activity
        </h3>
        {progress?.recent_activity && progress.recent_activity.length > 0 ? (
          <div className="space-y-4">
            {progress.recent_activity.map((activity, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
              >
                <div className="flex items-center space-x-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    activity.status === 'solved'
                      ? 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-400'
                      : 'bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-400'
                  }`}>
                    {activity.status === 'solved' ? '✓' : '✗'}
                  </div>
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">
                      {activity.challenge_title}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(activity.timestamp).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                {activity.points_earned > 0 && (
                  <div className="text-green-600 dark:text-green-400 font-bold">
                    +{activity.points_earned} pts
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="text-4xl mb-2">📊</div>
            <p className="text-gray-500 dark:text-gray-400">
              No recent activity. Start solving challenges!
            </p>
          </div>
        )}
      </motion.div>

      {/* Learning Recommendations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
        className="card bg-gradient-to-r from-primary-50 to-purple-50 dark:from-primary-900/20 dark:to-purple-900/20"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
          <span className="text-2xl mr-2">💡</span> Personalized Recommendations
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
            <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Recommended Focus</div>
            <div className="font-semibold text-gray-900 dark:text-white">
              {analytics?.recommended_topics?.[0] || 'Web Security Basics'}
            </div>
          </div>
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
            <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Suggested Difficulty</div>
            <div className="font-semibold text-gray-900 dark:text-white">
              {analytics?.preferred_difficulty || 'Medium'}
            </div>
          </div>
          <div className="p-4 bg-white dark:bg-gray-800 rounded-lg">
            <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Learning Velocity</div>
            <div className="font-semibold text-gray-900 dark:text-white">
              {analytics?.learning_velocity ? `${analytics.learning_velocity.toFixed(1)}x` : '1.0x'} average
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Analytics;
