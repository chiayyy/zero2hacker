import React, { ReactNode } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';

interface LabButtonProps extends HTMLMotionProps<'button'> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
  loading?: boolean;
}

const variants = {
  primary: 'bg-primary-600 hover:bg-primary-700 text-white border border-primary-500',
  secondary: 'bg-purple-600 hover:bg-purple-700 text-white border border-purple-500',
  danger: 'bg-danger-600 hover:bg-danger-700 text-white border border-danger-500',
  ghost: 'bg-transparent text-gray-400 hover:text-gray-200 border border-gray-600 hover:border-gray-400',
};

const sizes = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
};

export default function LabButton({
  variant = 'primary',
  size = 'md',
  children,
  loading,
  disabled,
  ...props
}: LabButtonProps) {
  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      className={`rounded-lg font-medium transition-all duration-200 inline-flex items-center gap-2
        ${variants[variant]} ${sizes[size]}
        ${disabled || loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          Loading...
        </>
      ) : (
        children
      )}
    </motion.button>
  );
}
