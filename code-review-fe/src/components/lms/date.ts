export const TODAY = new Date("2026-02-14T00:00:00")

export function formatDate(date: string) {
  return new Date(date).toLocaleDateString("vi-VN")
}

export function daysUntil(date: string) {
  const target = new Date(date)
  return Math.ceil((target.getTime() - TODAY.getTime()) / (1000 * 60 * 60 * 24))
}
