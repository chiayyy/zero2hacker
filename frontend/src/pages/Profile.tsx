import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import { analyticsService } from '../services/api';
import { UserAnalytics } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import { toast } from 'react-hot-toast';
import { TrophyIcon, StarIcon, PencilSquareIcon } from '@heroicons/react/24/outline';

const Profile: React.FC = () => {
  const { user, updateUserProfile } = useAuth();
  const [, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [analytics, setAnalytics] = useState<UserAnalytics | null>(null);
  const [editMode, setEditMode] = useState(false);

  const [formData, setFormData] = useState<{
    display_name: string;
    skill_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  }>({
    display_name: '',
    skill_level: 'beginner',
  });


  useEffect(() => {
    if (user) {
      setFormData({
        display_name: user.display_name || '',
        skill_level: (user.skill_level as any) || 'beginner',
      });
      fetchAnalytics();
    }
  }, [user]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchAnalytics = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const data = await analyticsService.getUserAnalytics(user.id);
      setAnalytics(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await updateUserProfile(formData);
      setEditMode(false);
      toast.success('Profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const getSkillLevelColor = (level: string) => {
    const colors: Record<string, string> = {
      beginner: 'bg-green-100 text-green-800',
      intermediate: 'bg-blue-100 text-blue-800',
      advanced: 'bg-purple-100 text-purple-800',
      expert: 'bg-red-100 text-red-800',
    };
    return colors[level] || colors.beginner;
  };

  const getLevelProgress = () => {
    if (!user) return 0;
    const currentProgress = user.total_points % 500;
    return (currentProgress / 500) * 100;
  };

  if (!user) {
    return <div className="flex items-center justify-center min-h-screen"><LoadingSpinner /></div>;
  }

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Profile Settings</h1>
        {!editMode ? (
          <button
            onClick={() => setEditMode(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
          >
            <PencilSquareIcon className="w-4 h-4" /> Edit Profile
          </button>
        ) : (
          <div className="flex space-x-3">
            <button onClick={() => setEditMode(false)} className="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-white rounded-lg transition-colors">
              Cancel
            </button>
            <button onClick={handleSave} disabled={saving} className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors disabled:opacity-50">
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        )}
      </div>

      {/* Profile Card */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card">
        <div className="flex items-start space-x-6">
          <div className="relative">
            <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-purple-600 rounded-full flex items-center justify-center text-3xl font-bold text-white">
              {user.display_name?.charAt(0) || user.username.charAt(0)}
            </div>
            <div className="absolute -bottom-1 -right-1 bg-green-500 w-6 h-6 rounded-full border-4 border-white dark:border-gray-800"></div>
          </div>

          <div className="flex-1">
            {editMode ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Display Name</label>
                  <input
                    type="text"
                    value={formData.display_name}
                    onChange={(e) => setFormData({ ...formData, display_name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Skill Level</label>
                  <select
                    value={formData.skill_level}
                    onChange={(e) => setFormData({ ...formData, skill_level: e.target.value as any })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                    <option value="expert">Expert</option>
                  </select>
                </div>
              </div>
            ) : (
              <>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{user.display_name || user.username}</h2>
                <p className="text-gray-500 dark:text-gray-400">@{user.username}</p>
                <div className="flex items-center space-x-3 mt-3">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSkillLevelColor(user.skill_level)}`}>
                    {user.skill_level}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">{user.role}</span>
                </div>
              </>
            )}
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Points', value: user.total_points, color: 'text-primary-600' },
          { label: 'Current Level', value: `Level ${user.level}`, color: 'text-green-600' },
          { label: 'Day Streak', value: user.streak_days, color: 'text-orange-600' },
          { label: 'Challenges Solved', value: analytics?.total_challenges_solved || 0, color: 'text-purple-600' },
        ].map((s, i) => (
          <motion.div key={s.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }} className="card text-center">
            <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
            <div className="text-sm text-gray-600 dark:text-gray-400">{s.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Level Progress */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }} className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Level Progress</h3>
        <div className="flex items-center space-x-4">
          <div className="flex-shrink-0 w-12 h-12 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
            <span className="text-primary-600 dark:text-primary-400 font-bold">{user.level}</span>
          </div>
          <div className="flex-1">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-600 dark:text-gray-400">Progress to Level {user.level + 1}</span>
              <span className="text-gray-900 dark:text-white font-medium">{user.total_points % 500} / 500 XP</span>
            </div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(getLevelProgress(), 100)}%` }}
              />
            </div>
          </div>
          <div className="flex-shrink-0 w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center">
            <span className="text-gray-400 font-bold">{user.level + 1}</span>
          </div>
        </div>
      </motion.div>

      {/* Badges */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <TrophyIcon className="w-5 h-5 text-yellow-500" />
          Badges &amp; Achievements
        </h3>
        {user.badges && user.badges.length > 0 ? (
          <div className="grid grid-cols-4 md:grid-cols-6 gap-4">
            {user.badges.map((badge, index) => (
              <div key={index} className="text-center">
                <div className="w-16 h-16 mx-auto bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
                  <StarIcon className="w-8 h-8 text-white" />
                </div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-2">{badge}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <TrophyIcon className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
            <p className="text-gray-500 dark:text-gray-400">Complete challenges to earn badges!</p>
          </div>
        )}
      </motion.div>

      {/* Account Info */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }} className="card">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Account Information</h3>
        <dl className="space-y-4">
          {[
            { label: 'Email', value: user.email },
            { label: 'Username', value: `@${user.username}` },
            { label: 'Member Since', value: new Date(user.created_at).toLocaleDateString() },
          ].map((item) => (
            <div key={item.label} className="flex justify-between py-2 border-b border-gray-200 dark:border-gray-700 last:border-0">
              <dt className="text-gray-600 dark:text-gray-400">{item.label}</dt>
              <dd className="text-gray-900 dark:text-white">{item.value}</dd>
            </div>
          ))}
          <div className="flex justify-between py-2">
            <dt className="text-gray-600 dark:text-gray-400">Account Status</dt>
            <dd className={`font-medium ${user.is_active ? 'text-green-600' : 'text-red-600'}`}>
              {user.is_active ? 'Active' : 'Inactive'}
            </dd>
          </div>
        </dl>
      </motion.div>
    </div>
  );
};

export default Profile;
