/** Mijozda shaxsiy raqam bo'lmasa — Uyimiz qo'llab-quvvatlash xizmati. */
export const SUPPORT_PHONE = '+998 71 200 00 88'

/** `tel:` havolasi uchun raqamdan bo'shliq va qavslarni olib tashlaydi. */
export function telHref(phone: string): string {
  return 'tel:' + phone.replace(/[^\d+]/g, '')
}
