import React from 'react';
import { Card, CardContent } from './Card';
import { cn } from '../layout/MainLayout';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  description?: string;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon: Icon,
  trend,
  trendValue,
  description,
  className,
}) => {
  return (
    <Card className={cn('animate-slide-up', className)}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500 dark:text-gray-400">{title}</p>
            <h4 className="mt-2 text-3xl font-bold text-slate-900 dark:text-gray-100">{value}</h4>
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary dark:bg-primary/20 dark:text-primary-300">
            <Icon className="h-6 w-6" />
          </div>
        </div>
        
        {(trend || description) && (
          <div className="mt-4 flex items-center text-sm">
            {trend && (
              <span
                className={cn(
                  'flex items-center font-medium mr-2',
                  trend === 'up' ? 'text-success-dark dark:text-success' : '',
                  trend === 'down' ? 'text-danger-dark dark:text-danger' : '',
                  trend === 'neutral' ? 'text-slate-500 dark:text-gray-400' : ''
                )}
              >
                {trend === 'up' && <TrendingUp className="mr-1 h-4 w-4" />}
                {trend === 'down' && <TrendingDown className="mr-1 h-4 w-4" />}
                {trend === 'neutral' && <Minus className="mr-1 h-4 w-4" />}
                {trendValue}
              </span>
            )}
            {description && <span className="text-slate-500 dark:text-gray-400">{description}</span>}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
