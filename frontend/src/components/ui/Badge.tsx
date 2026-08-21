import React, { type HTMLAttributes } from 'react';
import { cn } from '../layout/MainLayout';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
}

export const Badge: React.FC<BadgeProps> = ({
  className,
  variant = 'neutral',
  children,
  ...props
}) => {
  const variants = {
    success: 'bg-success-light text-success-dark dark:bg-success-dark/20 dark:text-success-light',
    warning: 'bg-warning-light text-warning-dark dark:bg-warning-dark/20 dark:text-warning-light',
    danger: 'bg-danger-light text-danger-dark dark:bg-danger-dark/20 dark:text-danger-light',
    info: 'bg-primary-50 text-primary-700 dark:bg-primary-900/30 dark:text-primary-200',
    neutral: 'bg-slate-100 text-slate-700 dark:bg-gray-800 dark:text-gray-300',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors',
        variants[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};
