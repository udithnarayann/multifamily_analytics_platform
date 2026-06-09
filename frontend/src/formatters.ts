export function formatInteger(value: number | null | undefined): string {
  return value == null ? '—' : new Intl.NumberFormat('en-US').format(value);
}

export function formatPercent(value: number | null | undefined): string {
  if (value == null) return '—';
  return `${(value * 100).toFixed(1)}%`;
}

export function formatRatio(value: number | null | undefined): string {
  return value == null ? '—' : value.toFixed(2);
}

export function formatCurrencyCompact(value: number | null | undefined): string {
  if (value == null) return '—';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) return '—';
  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value));
}
