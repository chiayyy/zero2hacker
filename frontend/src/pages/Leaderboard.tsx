import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { userService } from '../services/api';
import { LeaderboardEntry } from '../types';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const Leaderboard: React.FC = () => {
  const { user } = useAuth();
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState<'all' | 'weekly' | 'monthly'>('all');

  useEffect(() => {
    fetchLeaderboard();
  }, [timeframe]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const data = await userService.getLeaderboard({ limit: 50, timeframe });
      setLeaderboard(data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1: return '🥇';
      case 2: return '🥈';
      case 3: return '🥉';
      default: return `#${rank}`;
    }
  };

  const getRankStyle = (rank: number) => {
    switch (rank) {
      case 1: return 'bg-gradient-to-r from-yellow-400 to-amber-500 text-white';
      case 2: return 'bg-gradient-to-r from-gray-300 to-gray-400 text-gray-800';
      case 3: return 'bg-gradient-to-r from-orange-400 to-orange-600 text-white';
      default: return 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300';
    }
  };

  const currentUserRank = leaderboard.find(entry => entry.user_id === user?.id);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Leaderboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            See how you rank against other hackers
          </p>
        </div>

        {/* Timeframe Filter */}
        <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          {(['all', 'weekly', 'monthly'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                timeframe === tf
                  ? 'bg-white dark:bg-gray-700 text-primary-600 dark:text-primary-400 shadow'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
              }`}
            >
              {tf === 'all' ? 'All Time' : tf === 'weekly' ? 'This Week' : 'This Month'}
            </button>
          ))}
        </div>
      </div>

      {/* Current User Rank Card */}
      {currentUserRank && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-primary-500 to-purple-600 text-white rounded-xl p-6"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center text-2xl font-bold">
                {currentUserRank.rank <= 3 ? getRankIcon(currentUserRank.rank) : `#${currentUserRank.rank}`}
              </div>
              <div>
                <h3 className="text-xl font-bold">Your Ranking</h3>
                <p className="text-white/80">Keep pushing to climb higher!</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold">{currentUserRank.total_points}</div>
              <div className="text-white/80">Points</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Top 3 Podium */}
      {!loading && leaderboard.length >= 3 && (
        <div className="grid grid-cols-3 gap-4 mb-8">
          {/* Second Place */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card text-center pt-8"
          >
            <div className="text-4xl mb-2">🥈</div>
            <div className="w-16 h-16 mx-auto bg-gradient-to-br from-gray-300 to-gray-400 rounded-full flex items-center justify-center text-xl font-bold text-gray-800 mb-3">
              {leaderboard[1]?.display_name?.charAt(0) || leaderboard[1]?.username.charAt(0)}
            </div>
            <h3 className="font-bold text-gray-900 dark:text-white truncate px-2">
              {leaderboard[1]?.display_name || leaderboard[1]?.username}
            </h3>
            <p className="text-2xl font-bold text-gray-600 dark:text-gray-300">
              {leaderboard[1]?.total_points}
            </p>
            <p className="text-sm text-gray-500">Points</p>
          </motion.div>

          {/* First Place */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card text-center bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 border-2 border-yellow-400"
          >
            <div className="text-5xl mb-2">🥇</div>
            <div className="w-20 h-20 mx-auto bg-gradient-to-br from-yellow-400 to-amber-500 rounded-full flex items-center justify-center text-2xl font-bold text-white mb-3 ring-4 ring-yellow-200">
              {leaderboard[0]?.display_name?.charAt(0) || leaderboard[0]?.username.charAt(0)}
            </div>
            <h3 className="font-bold text-gray-900 dark:text-white text-lg truncate px-2">
              {leaderboard[0]?.display_name || leaderboard[0]?.username}
            </h3>
            <p className="text-3xl font-bold text-yellow-600">
              {leaderboard[0]?.total_points}
            </p>
            <p className="text-sm text-gray-500">Points</p>
          </motion.div>

          {/* Third Place */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card text-center pt-12"
          >
            <div className="text-4xl mb-2">🥉</div>
            <div className="w-14 h-14 mx-auto bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center text-lg font-bold text-white mb-3">
              {leaderboard[2]?.display_name?.charAt(0) || leaderboard[2]?.username.charAt(0)}
            </div>
            <h3 className="font-bold text-gray-900 dark:text-white truncate px-2">
              {leaderboard[2]?.display_name || leaderboard[2]?.username}
            </h3>
            <p className="text-xl font-bold text-orange-600">
              {leaderboard[2]?.total_points}
            </p>
            <p className="text-sm text-gray-500">Points</p>
          </motion.div>
        </div>
      )}

      {/* Full Leaderboard Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card overflow-hidden"
      >
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
          Full Rankings
        </h2>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <LoadingSpinner />
          </div>
        ) : leaderboard.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-4xl mb-2">📊</div>
            <p className="text-gray-500 dark:text-gray-400">
              No rankings yet. Be the first to complete a challenge!
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-400">Rank</th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-600 dark:text-gray-400">User</th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-600 dark:text-gray-400">Level</th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-600 dark:text-gray-400">Solves</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-600 dark:text-gray-400">Points</th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((entry, index) => (
                  <motion.tr
                    key={entry.user_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors ${
                      entry.user_id === user?.id ? 'bg-primary-50 dark:bg-primary-900/20' : ''
                    }`}
                  >
                    <td className="px-4 py-4">
                      <span className={`inline-flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold ${getRankStyle(entry.rank)}`}>
                        {entry.rank <= 3 ? getRankIcon(entry.rank) : entry.rank}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-primary-400 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                          {entry.display_name?.charAt(0) || entry.username.charAt(0)}
                        </div>
                        <div>
                          <div className="font-medium text-gray-900 dark:text-white">
                            {entry.display_name || entry.username}
                            {entry.user_id === user?.id && (
                              <span className="ml-2 text-xs bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 px-2 py-0.5 rounded-full">
                                You
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            @{entry.username}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-center">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                        Lvl {entry.level}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-center text-gray-600 dark:text-gray-300">
                      {entry.solve_count}
                    </td>
                    <td className="px-4 py-4 text-right">
                      <span className="text-lg font-bold text-gray-900 dark:text-white">
                        {entry.total_points.toLocaleString()}
                      </span>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default Leaderboard;
