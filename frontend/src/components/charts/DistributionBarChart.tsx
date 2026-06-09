import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { CountBucket } from '../../api/types';

interface DistributionBarChartProps {
  data: CountBucket[];
  color?: string;
}

export function DistributionBarChart({ data, color = '#2563eb' }: DistributionBarChartProps) {
  const chartData = data.slice(0, 12);

  if (chartData.length === 0) {
    return <div className="empty-chart">No data available yet.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 10, right: 10, bottom: 40, left: 10 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="key" angle={-35} textAnchor="end" interval={0} height={70} />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Bar dataKey="count" fill={color} radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
