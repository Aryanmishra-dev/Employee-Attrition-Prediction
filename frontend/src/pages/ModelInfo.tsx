import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Shield, Database, Cpu } from 'lucide-react';

const ModelInfo: React.FC = () => {
  const metrics = [
    { label: 'Accuracy', value: 0.7823, color: 'bg-primary' },
    { label: 'AUC-ROC', value: 0.8108, color: 'bg-indigo-500' },
    { label: 'F1 Score', value: 0.4754, color: 'bg-blue-500' },
    { label: 'Precision', value: 0.3867, color: 'bg-sky-500' },
    { label: 'Recall', value: 0.6170, color: 'bg-cyan-500' },
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Model Documentation</h2>
        <p className="text-slate-600 dark:text-gray-400">Technical details and performance metrics for the Attrition Prediction model.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card glass className="flex flex-col items-center justify-center p-6 text-center">
          <div className="mb-4 rounded-full bg-primary/10 p-3 text-primary">
            <Cpu className="h-6 w-6" />
          </div>
          <h3 className="font-semibold text-slate-900 dark:text-white">Algorithm</h3>
          <p className="mt-1 text-sm text-slate-500">Logistic Regression (Optimized)</p>
        </Card>
        
        <Card glass className="flex flex-col items-center justify-center p-6 text-center">
          <div className="mb-4 rounded-full bg-success/10 p-3 text-success">
            <Database className="h-6 w-6" />
          </div>
          <h3 className="font-semibold text-slate-900 dark:text-white">Dataset</h3>
          <p className="mt-1 text-sm text-slate-500">IBM HR Analytics (1,470 rows)</p>
        </Card>
        
        <Card glass className="flex flex-col items-center justify-center p-6 text-center">
          <div className="mb-4 rounded-full bg-warning/10 p-3 text-warning">
            <Shield className="h-6 w-6" />
          </div>
          <h3 className="font-semibold text-slate-900 dark:text-white">Objective</h3>
          <p className="mt-1 text-sm text-slate-500">Recall Optimization (F2 Score)</p>
        </Card>
      </div>

      <Card glass>
        <CardHeader>
          <CardTitle>Performance Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {metrics.map((metric) => (
              <div key={metric.label}>
                <div className="mb-2 flex justify-between text-sm font-medium">
                  <span className="text-slate-700 dark:text-gray-300">{metric.label}</span>
                  <span className="text-slate-900 dark:text-white">{(metric.value * 100).toFixed(2)}%</span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-gray-700">
                  <div
                    className={`h-full rounded-full ${metric.color} transition-all duration-1000 ease-out`}
                    style={{ width: `${metric.value * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-8 rounded-xl bg-slate-50 p-4 text-sm text-slate-600 dark:bg-gray-800/50 dark:text-gray-400">
            <strong>Note:</strong> The model is intentionally tuned to favor recall over precision. In the context of HR attrition, missing an at-risk employee (false negative) is considered more costly than incorrectly flagging a stable employee for review (false positive).
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ModelInfo;
