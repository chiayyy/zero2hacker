import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  HomeIcon,
  PuzzlePieceIcon,
  TrophyIcon,
  ChartBarIcon,
  UserIcon,
  Cog6ToothIcon,
  XMarkIcon,
  BeakerIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Labs', href: '/lab', icon: BeakerIcon },
    { name: 'Challenges', href: '/challenges', icon: PuzzlePieceIcon },
    { name: 'AI Generator', href: '/generate-challenge', icon: SparklesIcon },
    { name: 'Leaderboard', href: '/leaderboard', icon: TrophyIcon },
    { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
    { name: 'Profile', href: '/profile', icon: UserIcon },
  ];

  if (user?.role === 'admin') {
    navigation.push({ name: 'Admin Panel', href: '/admin', icon: Cog6ToothIcon });
  }

  const sidebarVariants = {
    open: { x: 0, transition: { type: 'spring' as const, stiffness: 300, damping: 30 } },
    closed: { x: '-100%', transition: { type: 'spring' as const, stiffness: 300, damping: 30 } },
  };

  const NavItems = ({ withClose = false }) => (
    <>
      {navigation.map((item) => {
        const isActive =
          location.pathname === item.href ||
          (item.href !== '/dashboard' && location.pathname.startsWith(item.href));

        return (
          <NavLink
            key={item.name}
            to={item.href}
            onClick={withClose ? onClose : undefined}
            className={`${
              isActive ? 'nav-link-active' : 'nav-link-inactive'
            } group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200`}
          >
            <motion.div
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center w-full"
            >
              <item.icon
                className={`${
                  isActive
                    ? 'text-primary-600 dark:text-primary-400'
                    : 'text-gray-400 group-hover:text-gray-600 dark:group-hover:text-gray-300'
                } mr-3 h-5 w-5 transition-colors duration-200`}
              />
              {item.name}
            </motion.div>
          </NavLink>
        );
      })}
    </>
  );

  return (
    <>
      {/* Desktop Sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col z-30">
        <div className="flex min-h-0 flex-1 flex-col bg-white dark:bg-dark-800 border-r border-gray-200 dark:border-dark-700">
          <div className="flex flex-1 flex-col overflow-y-auto pt-5 pb-4">
            {/* Logo */}
            <div className="flex flex-shrink-0 items-center px-4">
              <motion.div
                className="flex items-center space-x-3"
                whileHover={{ scale: 1.05 }}
                transition={{ type: 'spring', stiffness: 400, damping: 10 }}
              >
                <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">Z</span>
                </div>
                <span className="text-xl font-bold text-gradient">Zero2Hacker</span>
              </motion.div>
            </div>

            {/* Navigation */}
            <nav className="mt-8 flex-1 space-y-1 px-2">
              <NavItems />
            </nav>

            {/* User info */}
            {user && (
              <div className="flex flex-shrink-0 border-t border-gray-200 dark:border-dark-700 p-4">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    {user.avatar_url ? (
                      <img
                        className="h-8 w-8 rounded-full"
                        src={user.avatar_url}
                        alt={user.display_name || user.username}
                      />
                    ) : (
                      <div className="h-8 w-8 rounded-full bg-primary-500 flex items-center justify-center">
                        <span className="text-white text-sm font-medium">
                          {(user.display_name || user.username).charAt(0).toUpperCase()}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="ml-3 flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                      {user.display_name || user.username}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                      Level {user.level} • {user.total_points} pts
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Sidebar */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="lg:hidden fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-dark-800 border-r border-gray-200 dark:border-dark-700"
            variants={sidebarVariants}
            initial="closed"
            animate="open"
            exit="closed"
          >
            <div className="flex min-h-0 flex-1 flex-col">
              <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-dark-700">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-lg">Z</span>
                  </div>
                  <span className="text-xl font-bold text-gradient">Zero2Hacker</span>
                </div>
                <button
                  onClick={onClose}
                  className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>

              <div className="flex flex-1 flex-col overflow-y-auto pt-4 pb-4">
                <nav className="flex-1 space-y-1 px-2">
                  <NavItems withClose />
                </nav>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Sidebar;
