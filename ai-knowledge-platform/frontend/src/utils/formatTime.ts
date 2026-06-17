import dayjs from 'dayjs'

export function formatTime(dateStr?: string): string {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm')
}

export function formatDate(dateStr?: string): string {
  if (!dateStr) return '-'
  return dayjs(dateStr).format('YYYY-MM-DD')
}
