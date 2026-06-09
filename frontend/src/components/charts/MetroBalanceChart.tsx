import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { BalanceBucket } from '../../api/types';
import { formatCurrencyCompact } from '../../formatters';

interface MetroBalanceChartProps {
  data: BalanceBucket[];
}

export function MetroBalanceChart({ data }: MetroBalanceChartProps) {
  const chartData = data.map((item) => ({ ...item, balance: item.total_ending_balance ?? 0 }));

  if (chartData.length === 0) {
    return <div className="empty-chart">No metro balance data available yet.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 10, right: 10, bottom: 55, left: 20 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="key" angle={-35} textAnchor="end" interval={0} height={85} />
        <YAxis tickFormatter={formatCurrencyCompact} />
        <Tooltip formatter={(value) => formatCurrencyCompact(Number(value))} />
        <Bar dataKey="balance" fill="#0f766e" radius={[6, 6, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
