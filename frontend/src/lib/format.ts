/** Raqamni o'zbekcha ko'rinishda ajratadi: 18400000 -> "18 400 000". */
export function nf(value: number | string, digits = 0): string {
  const n = typeof value === 'string' ? Number(value) : value
  if (!Number.isFinite(n)) return '0'
  return n.toLocaleString('ru-RU', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  })
}

/** Katta so'm summasini qisqartiradi: 18400000 -> { value: "18,4", unit: "mln" }. */
export function compactSum(value: number | string): { value: string; unit: string } {
  const n = typeof value === 'string' ? Number(value) : value
  if (!Number.isFinite(n)) return { value: '0', unit: '' }
  if (n >= 1_000_000_000) return { value: (n / 1_000_000_000).toFixed(1).replace('.', ','), unit: 'mlrd' }
  if (n >= 1_000_000) return { value: (n / 1_000_000).toFixed(1).replace('.', ','), unit: 'mln' }
  if (n >= 1_000) return { value: (n / 1_000).toFixed(0), unit: 'ming' }
  return { value: String(Math.round(n)), unit: '' }
}

export function money(value: number | string, currency = 'UZS'): string {
  const n = typeof value === 'string' ? Number(value) : value
  if (currency === 'USD') return '$' + nf(n)
  return nf(n) + " so'm"
}

const MONTHS = [
  'yanvar',
  'fevral',
  'mart',
  'aprel',
  'may',
  'iyun',
  'iyul',
  'avgust',
  'sentabr',
  'oktabr',
  'noyabr',
  'dekabr',
]

/** "2 soat oldin", "kecha", "3 kun oldin" — jadval ustunlari uchun. */
export function timeAgo(iso: string | null): string {
  if (!iso) return '—'
  const then = new Date(iso).getTime()
  const mins = Math.round((Date.now() - then) / 60000)
  if (mins < 1) return 'hozir'
  if (mins < 60) return `${mins} daqiqa oldin`
  const hours = Math.round(mins / 60)
  if (hours < 24) return `${hours} soat oldin`
  const days = Math.round(hours / 24)
  if (days === 1) return 'kecha'
  if (days < 30) return `${days} kun oldin`
  const months = Math.round(days / 30)
  return `${months} oy oldin`
}

export function dateLabel(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return `${d.getDate()}-${MONTHS[d.getMonth()]} ${d.getFullYear()}`
}

export function dateTimeLabel(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${d.getDate()}-${MONTHS[d.getMonth()]}, ${hh}:${mm}`
}

export function monthLabel(d = new Date()): string {
  const m = MONTHS[d.getMonth()]
  return m.charAt(0).toUpperCase() + m.slice(1) + ' ' + d.getFullYear()
}

/** Holat nomini pill sinfiga bog'laydi. */
export function statusPill(status: string): string {
  switch (status) {
    case "Qo'ng'iroq kutmoqda":
      return 'pill pill-hot'
    case 'Shartnomada':
    case 'Yopilgan':
    case 'Tasdiqlangan':
    case 'Faol':
      return 'pill pill-ok'
    case 'VIP':
    case 'Premium':
    case 'Band':
      return 'pill pill-vip'
    case 'Rad etilgan':
    case 'Bekor qilingan':
      return 'pill pill-hot'
    default:
      return 'pill'
  }
}
