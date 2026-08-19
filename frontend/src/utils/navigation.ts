import { Home, Sparkles, Table, BarChart2, Shield } from 'lucide-react';
import React from 'react';

export interface NavItem {
  label: string;
  path: string;
  icon: React.ElementType;
}

export const PRIMARY_NAV: NavItem[] = [
  { label: 'Dashboard', path: '/', icon: Home },
  { label: 'Single Prediction', path: '/predict', icon: Sparkles },
  { label: 'Batch Prediction', path: '/batch-predict', icon: Table },
  { label: 'Analytics', path: '/analytics', icon: BarChart2 },
  { label: 'Model Info', path: '/model-info', icon: Shield },
];

export const getPageHeaders = (pathname: string): { title: string; subtitle: string } => {
  if (pathname === '/') {
    return {
      title: 'Attrition Command Center',
      subtitle: 'Monitor portfolio risk, recent predictions, and department-level signals in one place.',
    };
  }
  if (pathname === '/predict') {
    return {
      title: 'Single Employee Prediction',
      subtitle: 'Run a structured attrition assessment for one employee.',
    };
  }
  if (pathname === '/batch-predict') {
    return {
      title: 'Batch Prediction',
      subtitle: 'Upload a CSV, preview the first rows, and score attrition risk at scale.',
    };
  }
  if (pathname === '/analytics') {
    return {
      title: 'Analytics',
      subtitle: 'Explore aggregate attrition trends, feature signals, and prediction history.',
    };
  }
  if (pathname === '/model-info') {
    return {
      title: 'Model Info',
      subtitle: 'Transparent documentation for stakeholders reviewing the model and its performance.',
    };
  }
  if (pathname.startsWith('/employee/')) {
    const id = pathname.split('/')[2];
    return {
      title: `Employee ${id} Profile`,
      subtitle: 'Review risk drivers, compare satisfaction signals to the company baseline, and capture HR notes.',
    };
  }
  return { title: 'Attrition Studio', subtitle: '' };
};
