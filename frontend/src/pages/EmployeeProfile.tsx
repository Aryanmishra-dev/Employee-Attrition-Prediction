import React from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { Mail, Calendar } from 'lucide-react';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const EmployeeProfile: React.FC = () => {
  const { employeeId } = useParams<{ employeeId: string }>();

  const radarData = {
    labels: ['Job Satisfaction', 'Environment', 'Work-Life Balance', 'Relationship', 'Involvement'],
    datasets: [
      {
        label: 'Employee Score',
        data: [2, 3, 2, 4, 3],
        backgroundColor: 'rgba(239, 68, 68, 0.2)',
        borderColor: 'rgba(239, 68, 68, 1)',
        borderWidth: 2,
      },
      {
        label: 'Company Average',
        data: [3.5, 3.2, 3.8, 3.6, 3.5],
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
        borderColor: 'rgba(79, 70, 229, 0.5)',
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-primary to-indigo-700 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
            JD
          </div>
          <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">John Doe</h2>
            <p className="text-slate-500 dark:text-gray-400">{employeeId || 'EMP-4829'} • Senior Developer</p>
            <div className="mt-2 flex gap-2">
              <Badge variant="danger">High Risk (82%)</Badge>
              <Badge variant="neutral">Engineering</Badge>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Mail className="mr-2 h-4 w-4" /> Message</Button>
          <Button><Calendar className="mr-2 h-4 w-4" /> Schedule 1:1</Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3 pt-4">
        <Card glass className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Risk Drivers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="rounded-xl border border-danger/20 bg-danger/5 p-4">
                <h4 className="font-semibold text-danger-dark dark:text-danger-light">Low Job Satisfaction</h4>
                <p className="text-sm text-slate-600 dark:text-gray-300 mt-1">Score of 2/4 is significantly below department average.</p>
              </div>
              <div className="rounded-xl border border-danger/20 bg-danger/5 p-4">
                <h4 className="font-semibold text-danger-dark dark:text-danger-light">Years Since Last Promotion</h4>
                <p className="text-sm text-slate-600 dark:text-gray-300 mt-1">4 years since last promotion, leading to stagnation.</p>
              </div>
              <div className="rounded-xl border border-warning/20 bg-warning/5 p-4">
                <h4 className="font-semibold text-warning-dark dark:text-warning-light">Frequent Overtime</h4>
                <p className="text-sm text-slate-600 dark:text-gray-300 mt-1">Consistent overtime logged over the past 3 months.</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card glass>
          <CardHeader>
            <CardTitle>Satisfaction Radar</CardTitle>
          </CardHeader>
          <CardContent className="h-64 flex justify-center">
            <Radar data={radarData} options={{ responsive: true, maintainAspectRatio: false }} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default EmployeeProfile;
