import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { analyticsService, userService } from '../services/api';
import { UserAnalytics, LearningProgress } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  BoltIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  LightBulbIcon,
  CheckCircleIcon,
  XCircleIcon,
} from '@heroicons/react/24/outline';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import axios from 'axios';

const api = axios.create({ baseURL: process.env.REACT_APP_API_URL || '/api/v1' });

const Analytics: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [progress, setProgress] = useState<LearningProgress | null>(null);
  const [activityData, setActivityData] = useState<{ day: string; challenges: number; points: number }[]>([]);

  useEffect(() => {
    if (user) fetchData();
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchData = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const [analyticsData, progressData, weeklyData] = await Promise.all([
        analyticsService.getUserAnalytics(user.id),
        userService.getUserProgress(user.id),
        api.get(`/analytics/user/${user.id}/weekly-activity`, { headers }).then(r => r.data).catch(() => []),
      ]);
      setAnalytics(analyticsData);
      setProgress(progressData);
      setActivityData(weeklyData);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const categoryData = progress?.category_breakdown
    ? Object.entries(progress.category_breakdown).map(([name, data]) => ({
        name,
        solved: (data as any).solved,
        total: (data as any).total,
        percentage: (data as any).total > 0 ? Math.round(((data as any).solved / (data as any).total) * 100) : 0,
      }))
    : [];

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
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Learning Analytics</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">
          Track your progress and identify areas for improvement
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Challenges Solved', value: analytics?.total_challenges_solved || 0, color: 'from-blue-500 to-blue-600', sub: 'text-blue-100' },
          { label: 'Success Rate', value: `${Math.round((analytics?.solve_rate || 0) * 100)}%`, color: 'from-green-500 to-green-600', sub: 'text-green-100' },
          { label: 'Avg. Solve Time', value: analytics?.avg_solve_time ? `${Math.round(analytics.avg_solve_time)}m` : 'N/A', color: 'from-purple-500 to-purple-600', sub: 'text-purple-100' },
          { label: 'Day Streak', value: analytics?.consecutive_days || 0, color: 'from-orange-500 to-orange-600', sub: 'text-orange-100' },
        ].map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`card bg-gradient-to-br ${s.color} text-white`}
          >
            <div className="text-3xl font-bold">{s.value}</div>
            <div className={`${s.sub} text-sm`}>{s.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Weekly Activity — real data */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }} className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Weekly Activity</h3>
          {activityData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={activityData}>
                  <defs>
                    <linearGradient id="colorPoints" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                  <XAxis dataKey="day" className="text-gray-600 dark:text-gray-400" />
                  <YAxis className="text-gray-600 dark:text-gray-400" />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(17,24,39,0.9)', border: 'none', borderRadius: '8px', color: 'white' }}
                  />
                  <Area type="monotone" dataKey="points" stroke="#6366f1" fillOpacity={1} fill="url(#colorPoints)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center">
              <p className="text-gray-500 dark:text-gray-400">No activity this week yet.</p>
            </div>
          )}
        </motion.div>

        {/* Category Progress — real data */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Category Progress</h3>
          {categoryData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
                  <XAxis type="number" domain={[0, 100]} unit="%" />
                  <YAxis dataKey="name" type="category" width={100} />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(17,24,39,0.9)', border: 'none', borderRadius: '8px', color: 'white' }}
                    formatter={(value: number) => [`${value}%`, 'Progress']}
                  />
                  <Bar dataKey="percentage" fill="#6366f1" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center">
              <p className="text-gray-500 dark:text-gray-400">Solve challenges to see category progress.</p>
            </div>
          )}
        </motion.div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <BoltIcon className="w-5 h-5 text-green-500" />
            Strengths
          </h3>
          {analytics?.strengths && analytics.strengths.length > 0 ? (
            <ul className="space-y-3">
              {analytics.strengths.map((strength, index) => (
                <li key={index} className="flex items-center space-x-3">
                  <CheckCircleIcon className="w-6 h-6 text-green-500 shrink-0" />
                  <span className="text-gray-700 dark:text-gray-300">{strength}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-center py-6">
              Complete more challenges to discover your strengths!
            </p>
          )}
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }} className="card">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <ExclamationTriangleIcon className="w-5 h-5 text-yellow-500" />
            Areas to Improve
          </h3>
          {analytics?.weaknesses && analytics.weaknesses.length > 0 ? (
            <ul className="space-y-3">
              {analytics.weaknesses.map((weakness, index) => (
                <li key={index} className="flex items-center space-x-3">
                  <ExclamationTriangleIcon className="w-6 h-6 text-yellow-500 shrink-0" />
                  <span className="text-gray-700 dark:text-gray-300">{weakness}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-center py-6">
              Keep practicing to identify areas for improvement!
            </p>
          )}
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }} className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <ChartBarIcon className="w-5 h-5 text-primary-500" />
          Recent Activity
        </h3>
        {progress?.recent_activity && progress.recent_activity.length > 0 ? (
          <div className="space-y-4">
            {progress.recent_activity.map((activity: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    activity.status === 'solved'
                      ? 'bg-green-100 dark:bg-green-900'
                      : 'bg-red-100 dark:bg-red-900'
                  }`}>
                    {activity.status === 'solved'
                      ? <CheckCircleIcon className="w-5 h-5 text-green-600 dark:text-green-400" />
                      : <XCircleIcon className="w-5 h-5 text-red-600 dark:text-red-400" />
                    }
                  </div>
                  <div>
                    <div className="font-medium text-gray-900 dark:text-white">{activity.challenge_title}</div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {new Date(activity.timestamp).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                {activity.points_earned > 0 && (
                  <div className="text-green-600 dark:text-green-400 font-bold">+{activity.points_earned} pts</div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <ChartBarIcon className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
            <p className="text-gray-500 dark:text-gray-400">No recent activity. Start solving challenges!</p>
          </div>
        )}
      </motion.div>

      {/* Recommendations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
        className="card bg-gradient-to-r from-primary-50 to-purple-50 dark:from-primary-900/20 dark:to-purple-900/20"
      >
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <LightBulbIcon className="w-5 h-5 text-yellow-500" />
          Personalized Recommendations
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
