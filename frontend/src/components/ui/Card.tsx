import React, { type HTMLAttributes } from 'react';
import { cn } from '../layout/MainLayout';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
}

export const Card: React.FC<CardProps> = ({ className, glass = false, children, ...props }) => {
  return (
    <div
      className={cn(
        'rounded-2xl overflow-hidden transition-all duration-300',
        glass ? 'glass-card' : 'bg-white/80 dark:bg-gray-800/80 backdrop-blur shadow-sm border border-slate-100 dark:border-gray-700 hover:shadow-md hover:border-primary/20 dark:hover:border-primary/30',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div className={cn('px-6 py-5 border-b border-slate-100 dark:border-gray-700/50', className)} {...props}>
    {children}
  </div>
);

export const CardTitle: React.FC<HTMLAttributes<HTMLHeadingElement>> = ({ className, children, ...props }) => (
  <h3 className={cn('text-lg font-semibold text-slate-900 dark:text-gray-100', className)} {...props}>
    {children}
  </h3>
);

export const CardContent: React.FC<HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => (
  <div className={cn('p-6', className)} {...props}>
    {children}
  </div>
);
