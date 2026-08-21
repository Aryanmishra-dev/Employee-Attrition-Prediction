import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

const Predict: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<{ score: number; risk: string } | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setResult({ score: 0.78, risk: 'High' });
      setIsLoading(false);
    }, 1500);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-slate-900 dark:text-white">Single Prediction Assessment</h2>
        <p className="mt-2 text-slate-600 dark:text-gray-400">Enter employee data below to generate an instant attrition risk score.</p>
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        <Card glass className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Employee Data</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Age</label>
                  <input type="number" className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:focus:border-primary" placeholder="e.g. 34" required />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Department</label>
                  <select className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white">
                    <option>Sales</option>
                    <option>Research & Development</option>
                    <option>Human Resources</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Monthly Income ($)</label>
                  <input type="number" className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white" placeholder="e.g. 5000" required />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Years at Company</label>
                  <input type="number" className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white" placeholder="e.g. 5" required />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Job Satisfaction (1-4)</label>
                  <input type="number" min="1" max="4" className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white" placeholder="e.g. 3" required />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 dark:text-gray-300">Overtime</label>
                  <select className="w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 dark:border-gray-600 dark:bg-gray-800 dark:text-white">
                    <option>Yes</option>
                    <option>No</option>
                  </select>
                </div>
              </div>
              
              <div className="pt-4 border-t border-slate-100 dark:border-gray-700">
                <Button type="submit" className="w-full sm:w-auto" isLoading={isLoading}>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generate Prediction
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card glass className="relative overflow-hidden">
            {isLoading && (
              <div className="absolute inset-0 z-10 flex items-center justify-center bg-white/50 backdrop-blur-sm dark:bg-gray-800/50">
                <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
              </div>
            )}
            <CardHeader>
              <CardTitle>Result</CardTitle>
            </CardHeader>
            <CardContent>
              {result ? (
                <div className="text-center animate-slide-up">
                  <div className="relative mx-auto mb-4 flex h-32 w-32 items-center justify-center rounded-full border-8 border-danger/20">
                    <div className="text-4xl font-bold text-danger">{(result.score * 100).toFixed(0)}%</div>
                  </div>
                  <Badge variant="danger" className="mb-4 text-sm px-3 py-1 text-base">{result.risk} Risk</Badge>
                  <p className="text-sm text-slate-600 dark:text-gray-400">
                    This profile exhibits strong indicators associated with historical attrition.
                  </p>
                </div>
              ) : (
                <div className="flex h-48 flex-col items-center justify-center text-center text-slate-400">
                  <AlertCircle className="mb-2 h-10 w-10 opacity-50" />
                  <p className="text-sm">Submit the form to see the prediction result here.</p>
                </div>
              )}
            </CardContent>
          </Card>
          
          {result && (
             <Card glass className="animate-slide-up border-success/30 bg-success-light/30 dark:bg-success-dark/10">
               <CardContent className="p-5">
                 <div className="flex items-start">
                   <CheckCircle2 className="mt-0.5 mr-3 h-5 w-5 text-success" />
                   <div>
                     <h4 className="font-semibold text-slate-900 dark:text-gray-100">Recommended Action</h4>
                     <p className="mt-1 text-sm text-slate-600 dark:text-gray-300">Schedule a 1:1 check-in to discuss career progression and current workload constraints.</p>
                   </div>
                 </div>
               </CardContent>
             </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Predict;
