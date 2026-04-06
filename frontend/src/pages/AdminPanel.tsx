import React, { useEffect, useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';
import {
  UserIcon,
  ShieldCheckIcon,
  ClockIcon,
  TrophyIcon,
  ArrowPathIcon,
  NoSymbolIcon,
  CheckCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';

// ---- Types ----
interface AdminUser {
  id: number;
  email: string;
  username: string;
  display_name: string | null;
  role: string;
  skill_level: string;
  total_points: number;
  level: number;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_activity: string | null;
  challenges_solved: number;
  challenges_attempted: number;
}

interface AdminChallenge {
  id: number;
  title: string;
  difficulty: string;
  points: number;
  category_id: number;
}

interface UserAttempt {
  attempt_id: number;
  challenge_id: number;
  challenge_title: string;
  difficulty: string;
  points: number;
  status: string;
  is_correct: boolean;
  points_earned: number;
  started_at: string;
  completed_at: string | null;
}

// ---- Helpers ----
const api = axios.create({ baseURL: process.env.REACT_APP_API_URL || '/api/v1' });

function authHeaders() {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function timeAgo(dateStr: string | null): string {
  if (!dateStr) return 'Never';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'Just now';
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
}

const difficultyColor: Record<string, string> = {
  BEGINNER: 'text-green-400',
  EASY: 'text-emerald-400',
  MEDIUM: 'text-yellow-400',
  HARD: 'text-orange-400',
  EXPERT: 'text-red-400',
};

// ---- Reset Modal ----
interface ResetModalProps {
  user: AdminUser;
  challenges: AdminChallenge[];
  onClose: () => void;
  onReset: (userId: number, challengeId: number) => Promise<void>;
}

const ResetModal: React.FC<ResetModalProps> = ({ user, challenges, onClose, onReset }) => {
  const [selected, setSelected] = useState<number | ''>('');
  const [loading, setLoading] = useState(false);

  const handle = async () => {
    if (!selected) return;
    setLoading(true);
    await onReset(user.id, Number(selected));
    setLoading(false);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-dark-800 border border-dark-600 rounded-xl p-6 w-full max-w-md shadow-2xl"
      >
        <h3 className="text-lg font-bold text-white mb-1">Reset Challenge</h3>
        <p className="text-sm text-dark-300 mb-4">
          User: <span className="text-primary-400 font-medium">{user.username}</span>
        </p>

        <label className="block text-sm text-dark-200 mb-2">Select challenge to reset</label>
        <select
          value={selected}
          onChange={e => setSelected(Number(e.target.value))}
          className="w-full bg-dark-700 border border-dark-500 text-white rounded-lg px-3 py-2 mb-6 focus:outline-none focus:border-primary-500"
        >
          <option value="">-- Choose a challenge --</option>
          {challenges.map(c => (
            <option key={c.id} value={c.id}>
              [{c.difficulty}] {c.title} ({c.points}pts)
            </option>
          ))}
        </select>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 rounded-lg border border-dark-500 text-dark-200 hover:bg-dark-700 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handle}
            disabled={!selected || loading}
            className="flex-1 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white font-medium transition-colors disabled:opacity-40"
          >
            {loading ? 'Resetting...' : 'Reset'}
          </button>
        </div>
      </motion.div>
    </div>
  );
};

// ---- Attempts Drawer ----
interface AttemptsDrawerProps {
  userId: number;
  onResetOne: (challengeId: number) => void;
}

const AttemptsDrawer: React.FC<AttemptsDrawerProps> = ({ userId, onResetOne }) => {
  const [attempts, setAttempts] = useState<UserAttempt[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get(`/admin/users/${userId}/attempts`, { headers: authHeaders() })
      .then(r => setAttempts(r.data))
      .catch(() => toast.error('Failed to load attempts'))
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <p className="text-dark-400 text-sm px-4 py-3">Loading attempts…</p>;
  if (!attempts.length) return <p className="text-dark-400 text-sm px-4 py-3">No attempts yet.</p>;

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-dark-400 text-xs uppercase border-b border-dark-600">
            <th className="text-left px-4 py-2">Challenge</th>
            <th className="text-left px-4 py-2">Difficulty</th>
            <th className="text-left px-4 py-2">Status</th>
            <th className="text-left px-4 py-2">Points</th>
            <th className="text-left px-4 py-2">Completed</th>
            <th className="px-4 py-2"></th>
          </tr>
        </thead>
        <tbody>
          {attempts.map(a => (
            <tr key={a.attempt_id} className="border-b border-dark-700 hover:bg-dark-700/40">
              <td className="px-4 py-2 text-white">{a.challenge_title}</td>
              <td className={`px-4 py-2 font-medium ${difficultyColor[a.difficulty] || 'text-dark-300'}`}>
                {a.difficulty}
              </td>
              <td className="px-4 py-2">
                {a.is_correct ? (
                  <span className="text-green-400 font-medium">Solved</span>
                ) : (
                  <span className="text-dark-400">{a.status}</span>
                )}
              </td>
              <td className="px-4 py-2 text-yellow-400">{a.points_earned}</td>
              <td className="px-4 py-2 text-dark-400">{timeAgo(a.completed_at)}</td>
              <td className="px-4 py-2">
                {a.is_correct && (
                  <button
                    onClick={() => onResetOne(a.challenge_id)}
                    className="text-xs text-red-400 hover:text-red-300 flex items-center gap-1"
                  >
                    <ArrowPathIcon className="w-3 h-3" /> Reset
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// ---- Main AdminPanel ----
const AdminPanel: React.FC = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [challenges, setChallenges] = useState<AdminChallenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [expandedUser, setExpandedUser] = useState<number | null>(null);
  const [resetTarget, setResetTarget] = useState<AdminUser | null>(null);

  const fetchUsers = () => {
    api
      .get('/admin/users', { headers: authHeaders() })
      .then(r => setUsers(r.data))
      .catch(() => toast.error('Failed to load users'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchUsers();
    api
      .get('/admin/challenges', { headers: authHeaders() })
      .then(r => setChallenges(r.data))
      .catch(() => {});
  }, []);

  const toggleActive = async (userId: number) => {
    try {
      const r = await api.patch(`/admin/users/${userId}/toggle-active`, {}, { headers: authHeaders() });
      toast.success(r.data.message);
      setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_active: r.data.is_active } : u));
    } catch {
      toast.error('Failed to update user');
    }
  };

  const resetChallenge = async (userId: number, challengeId: number) => {
    try {
      const r = await api.delete(`/admin/users/${userId}/reset-challenge/${challengeId}`, { headers: authHeaders() });
      toast.success(r.data.message);
      fetchUsers();
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Reset failed');
    }
  };

  const filtered = users.filter(u =>
    u.username.toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  );

  const totalUsers = users.length;
  const activeUsers = users.filter(u => u.is_active).length;
  const totalPoints = users.reduce((s, u) => s + u.total_points, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Admin Panel</h1>
        <p className="text-dark-400 mt-1">Manage users, monitor activity, and reset challenges</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Total Users', value: totalUsers, icon: UserIcon, color: 'text-primary-400' },
          { label: 'Active Users', value: activeUsers, icon: CheckCircleIcon, color: 'text-green-400' },
          { label: 'Total Points Earned', value: totalPoints.toLocaleString(), icon: TrophyIcon, color: 'text-yellow-400' },
        ].map(s => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-dark-800 border border-dark-600 rounded-xl p-4 flex items-center gap-4"
          >
            <s.icon className={`w-8 h-8 ${s.color}`} />
            <div>
              <p className="text-2xl font-bold text-white">{s.value}</p>
              <p className="text-sm text-dark-400">{s.label}</p>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Search */}
      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
        <input
          type="text"
          placeholder="Search by username or email…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full bg-dark-800 border border-dark-600 rounded-xl pl-9 pr-4 py-2.5 text-white placeholder-dark-400 focus:outline-none focus:border-primary-500"
        />
      </div>

      {/* User Table */}
      <div className="bg-dark-800 border border-dark-600 rounded-xl overflow-hidden">
        <div className="px-4 py-3 border-b border-dark-600">
          <h2 className="font-semibold text-white flex items-center gap-2">
            <ShieldCheckIcon className="w-5 h-5 text-primary-400" />
            User Management
          </h2>
        </div>

        {loading ? (
          <div className="p-8 text-center text-dark-400">Loading users…</div>
        ) : (
          <div>
            {filtered.map(user => (
              <div key={user.id} className="border-b border-dark-700 last:border-0">
                {/* Row */}
                <div className="flex items-center gap-4 px-4 py-3 hover:bg-dark-700/40 transition-colors">
                  {/* Avatar */}
                  <div className="w-9 h-9 rounded-full bg-primary-600/30 flex items-center justify-center shrink-0">
                    <span className="text-primary-300 font-bold text-sm">
                      {user.username[0].toUpperCase()}
                    </span>
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-white truncate">{user.username}</span>
                      {user.role === 'admin' && (
                        <span className="text-xs bg-primary-600/30 text-primary-300 px-2 py-0.5 rounded-full">Admin</span>
                      )}
                      {!user.is_active && (
                        <span className="text-xs bg-red-600/30 text-red-300 px-2 py-0.5 rounded-full">Inactive</span>
                      )}
                    </div>
                    <p className="text-sm text-dark-400 truncate">{user.email}</p>
                  </div>

                  {/* Stats */}
                  <div className="hidden md:flex items-center gap-6 text-sm">
                    <div className="text-center">
                      <p className="text-yellow-400 font-semibold">{user.total_points}</p>
                      <p className="text-dark-400 text-xs">pts</p>
                    </div>
                    <div className="text-center">
                      <p className="text-green-400 font-semibold">{user.challenges_solved}</p>
                      <p className="text-dark-400 text-xs">solved</p>
                    </div>
                    <div className="text-center min-w-[80px]">
                      <div className="flex items-center gap-1 text-dark-300">
                        <ClockIcon className="w-3.5 h-3.5" />
                        <span>{timeAgo(user.last_activity)}</span>
                      </div>
                      <p className="text-dark-400 text-xs">last active</p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 shrink-0">
                    {user.role !== 'admin' && (
                      <>
                        <button
                          onClick={() => setResetTarget(user)}
                          title="Reset a challenge"
                          className="p-1.5 rounded-lg text-dark-300 hover:text-yellow-400 hover:bg-dark-600 transition-colors"
                        >
                          <ArrowPathIcon className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => toggleActive(user.id)}
                          title={user.is_active ? 'Deactivate user' : 'Activate user'}
                          className={`p-1.5 rounded-lg transition-colors ${
                            user.is_active
                              ? 'text-dark-300 hover:text-red-400 hover:bg-dark-600'
                              : 'text-green-400 hover:bg-dark-600'
                          }`}
                        >
                          {user.is_active
                            ? <NoSymbolIcon className="w-4 h-4" />
                            : <CheckCircleIcon className="w-4 h-4" />
                          }
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => setExpandedUser(expandedUser === user.id ? null : user.id)}
                      className="p-1.5 rounded-lg text-dark-300 hover:bg-dark-600 transition-colors"
                    >
                      {expandedUser === user.id
                        ? <ChevronUpIcon className="w-4 h-4" />
                        : <ChevronDownIcon className="w-4 h-4" />
                      }
                    </button>
                  </div>
                </div>

                {/* Expanded: attempts */}
                {expandedUser === user.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="bg-dark-900/50 border-t border-dark-700"
                  >
                    <AttemptsDrawer
                      userId={user.id}
                      onResetOne={challengeId => resetChallenge(user.id, challengeId)}
                    />
                  </motion.div>
                )}
              </div>
            ))}

            {filtered.length === 0 && (
              <div className="p-8 text-center text-dark-400">No users found.</div>
            )}
          </div>
        )}
      </div>

      {/* Reset Modal */}
      {resetTarget && (
        <ResetModal
          user={resetTarget}
          challenges={challenges}
          onClose={() => setResetTarget(null)}
          onReset={resetChallenge}
        />
      )}
    </div>
  );
};

export default AdminPanel;
