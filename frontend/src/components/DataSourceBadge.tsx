interface DataSourceBadgeProps {
  children: string;
  tone?: 'hud' | 'freddie' | 'neutral';
}

export function DataSourceBadge({ children, tone = 'neutral' }: DataSourceBadgeProps) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
