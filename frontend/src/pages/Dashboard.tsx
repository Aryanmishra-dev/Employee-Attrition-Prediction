import React from 'react';
import { Users, AlertTriangle, Activity, Clock } from 'lucide-react';
import { StatCard } from '@/components/ui/StatCard';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
  Filler
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const Dashboard: React.FC = () => {
  const attritionData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Predicted Attrition Risk',
        data: [12, 19, 15, 22, 18, 14],
        backgroundColor: 'rgba(79, 70, 229, 0.2)',
        borderColor: 'rgba(79, 70, 229, 1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const deptData = {
    labels: ['Sales', 'R&D', 'HR', 'Engineering', 'Marketing'],
    datasets: [
      {
        label: 'High Risk Employees',
        data: [15, 8, 3, 24, 7],
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
        borderRadius: 4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
      x: { grid: { display: false } },
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Employees Monitored"
          value="1,470"
          icon={Users}
          trend="up"
          trendValue="+12 this month"
        />
        <StatCard
          title="High Risk Profile"
          value="237"
          icon={AlertTriangle}
          trend="down"
          trendValue="-5% vs last quarter"
          className="[&_h4]:text-danger dark:[&_h4]:text-danger-light"
        />
        <StatCard
          title="Average Satisfaction"
          value="3.2/5.0"
          icon={Activity}
          trend="neutral"
          trendValue="Unchanged"
        />
        <StatCard
          title="Avg. Tenure (Years)"
          value="7.1"
          icon={Clock}
          trend="up"
          trendValue="+0.4 years"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card glass className="h-96 flex flex-col">
          <CardHeader>
            <CardTitle>Attrition Risk Trend (6 Months)</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 min-h-0">
            <Line options={chartOptions} data={attritionData} />
          </CardContent>
        </Card>

        <Card glass className="h-96 flex flex-col">
          <CardHeader>
            <CardTitle>High Risk by Department</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 min-h-0">
            <Bar options={chartOptions} data={deptData} />
          </CardContent>
        </Card>
      </div>

      <Card glass>
        <CardHeader>
          <CardTitle>Recent High-Risk Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600 dark:text-gray-300">
              <thead className="bg-slate-50 dark:bg-gray-800/50 text-xs uppercase text-slate-500 dark:text-gray-400 border-b border-slate-200 dark:border-gray-700">
                <tr>
                  <th className="px-6 py-4 font-medium">Employee ID</th>
                  <th className="px-6 py-4 font-medium">Department</th>
                  <th className="px-6 py-4 font-medium">Job Role</th>
                  <th className="px-6 py-4 font-medium">Risk Score</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-gray-700">
                {[
                  { id: 'EMP-0182', dept: 'Sales', role: 'Sales Executive', score: 0.89 },
                  { id: 'EMP-0245', dept: 'Engineering', role: 'Software Engineer', score: 0.82 },
                  { id: 'EMP-0311', dept: 'R&D', role: 'Research Scientist', score: 0.76 },
                ].map((emp) => (
                  <tr key={emp.id} className="hover:bg-slate-50 dark:hover:bg-gray-800/50 transition-colors">
                    <td className="px-6 py-4 font-medium text-slate-900 dark:text-gray-100">{emp.id}</td>
                    <td className="px-6 py-4">{emp.dept}</td>
                    <td className="px-6 py-4">{emp.role}</td>
                    <td className="px-6 py-4 font-mono">{(emp.score * 100).toFixed(1)}%</td>
                    <td className="px-6 py-4">
                      <Badge variant={emp.score > 0.8 ? 'danger' : 'warning'}>
                        {emp.score > 0.8 ? 'Critical' : 'High'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
