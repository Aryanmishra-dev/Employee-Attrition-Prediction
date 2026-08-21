import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Doughnut, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const Analytics: React.FC = () => {
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
  };

  const donutData = {
    labels: ['Low Risk', 'Medium Risk', 'High Risk'],
    datasets: [
      {
        data: [65, 20, 15],
        backgroundColor: [
          'rgba(16, 185, 129, 0.8)', // success
          'rgba(245, 158, 11, 0.8)', // warning
          'rgba(239, 68, 68, 0.8)',  // danger
        ],
        borderWidth: 0,
      },
    ],
  };

  const lineData = {
    labels: ['20-25', '26-35', '36-45', '46-55', '55+'],
    datasets: [
      {
        label: 'Average Attrition Risk',
        data: [0.35, 0.42, 0.28, 0.15, 0.1],
        borderColor: 'rgba(79, 70, 229, 1)',
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Portfolio Analytics</h2>
        <p className="text-slate-600 dark:text-gray-400">Deep dive into organizational risk factors.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card glass className="h-96 flex flex-col">
          <CardHeader>
            <CardTitle>Risk Distribution</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 min-h-0 flex items-center justify-center">
            <div className="h-full w-full pb-4">
              <Doughnut options={{...chartOptions, plugins: { legend: { position: 'bottom' }}}} data={donutData} />
            </div>
          </CardContent>
        </Card>

        <Card glass className="h-96 lg:col-span-2 flex flex-col">
          <CardHeader>
            <CardTitle>Risk by Age Group</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 min-h-0">
            <Line options={chartOptions} data={lineData} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Analytics;
