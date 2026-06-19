export function formatDateTime(value: string): string {
  if (!value) return '';
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'medium'
  }).format(new Date(value));
}

export function formatBehavior(value: string): string {
  return value.replace(/_/g, ' ');
}

export function percent(value: number): string {
  return `${Math.round(value * 100)}%`;
}
