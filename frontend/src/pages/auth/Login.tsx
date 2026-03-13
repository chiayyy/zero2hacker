import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { motion, AnimatePresence } from 'framer-motion';
import { EyeIcon, EyeSlashIcon, ShieldExclamationIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../../contexts/AuthContext';
import { LoginForm } from '../../types';
import LoadingSpinner from '../../components/ui/LoadingSpinner';

const SQL_PATTERN = /('|--|;|\/\*|\*\/|xp_|exec\s|select\s|insert\s|drop\s|union\s|or\s+1\s*=\s*1|1=1)/i;
const XSS_PATTERN = /<\s*script|javascript:|on\w+\s*=|<\s*img|<\s*svg|alert\s*\(|document\.|window\./i;

const Login: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [hackerDetected, setHackerDetected] = useState(false);
  const { login, user } = useAuth();
  const navigate = useNavigate();

  const checkForHacking = (value: string) => {
    if (SQL_PATTERN.test(value) || XSS_PATTERN.test(value)) {
      setHackerDetected(true);
    }
  };

  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<LoginForm>();

  // Redirect when user is logged in
  useEffect(() => {
    if (user) {
      console.log('User is logged in, navigating to dashboard:', user);
      navigate('/dashboard', { replace: true });
    }
  }, [user, navigate]);

  const onSubmit = async (data: LoginForm) => {
    try {
      setLoading(true);
      console.log('Attempting login...');
      await login(data);
      console.log('Login completed');
      // Navigation will happen automatically via useEffect when user is set
    } catch (error) {
      console.error('Login error:', error);
      // Error is handled in AuthContext
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Hacker Easter Egg Banner */}
      <AnimatePresence>
        {hackerDetected && (
          <motion.div
            initial={{ opacity: 0, y: -16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -16 }}
            className="mb-5 rounded-xl border border-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 p-4"
          >
            <div className="flex items-start gap-3">
              <ShieldExclamationIcon className="h-6 w-6 text-yellow-500 shrink-0 mt-0.5" />
              <div>
                <p className="font-bold text-yellow-800 dark:text-yellow-300 text-sm">
                  Nice try, hacker! We see you. 👀
                </p>
                <p className="text-yellow-700 dark:text-yellow-400 text-xs mt-1">
                  Inputs are parameterised. But since you're curious…{' '}
                  <a
                    href="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="underline font-semibold hover:text-yellow-900 dark:hover:text-yellow-200"
                  >
                    claim your reward here
                  </a>
                  .
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
          Welcome back
        </h2>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Continue your cybersecurity learning journey
        </p>
      </div>

      {/* Hidden honeypot — bots fill this, humans don't */}
      <input
        type="text"
        name="username_confirm"
        tabIndex={-1}
        aria-hidden="true"
        style={{ position: 'absolute', left: '-9999px', opacity: 0, pointerEvents: 'none' }}
        autoComplete="off"
      />

      <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Email address
          </label>
          <input
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Invalid email address',
              },
              onChange: (e) => checkForHacking(e.target.value),
            })}
            type="email"
            className="input mt-1"
            placeholder="Enter your email"
          />
          {errors.email && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">
              {errors.email.message}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Password
          </label>
          <div className="relative mt-1">
            <input
              {...register('password', {
                required: 'Password is required',
                onChange: (e) => checkForHacking(e.target.value),
              })}
              type={showPassword ? 'text' : 'password'}
              className="input pr-10"
              placeholder="Enter your password"
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 flex items-center pr-3"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeSlashIcon className="h-5 w-5 text-gray-400" />
              ) : (
                <EyeIcon className="h-5 w-5 text-gray-400" />
              )}
            </button>
          </div>
          {errors.password && (
            <p className="mt-1 text-sm text-red-600 dark:text-red-400">
              {errors.password.message}
            </p>
          )}
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <input
              id="remember-me"
              name="remember-me"
              type="checkbox"
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              Remember me
            </label>
          </div>
        </div>

        <motion.button
          type="submit"
          disabled={loading}
          className="btn-primary w-full flex items-center justify-center"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {loading ? (
            <LoadingSpinner size="sm" color="text-white" />
          ) : (
            'Sign in'
          )}
        </motion.button>
      </form>

      <div className="mt-6">
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-gray-300 dark:border-gray-600" />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-white dark:bg-dark-900 text-gray-500">
              New to Zero2Hacker?
            </span>
          </div>
        </div>

        <div className="mt-6">
          <Link
            to="/auth/register"
            className="btn-outline w-full text-center"
          >
            Create an account
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
