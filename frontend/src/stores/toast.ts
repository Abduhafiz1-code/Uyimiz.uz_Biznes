import { ref } from 'vue'

export type ToastKind = 'ok' | 'err' | 'info'

export interface Toast {
  id: number
  kind: ToastKind
  text: string
}

const items = ref<Toast[]>([])
let seq = 0

function push(kind: ToastKind, text: string, ms = 3200) {
  const id = ++seq
  items.value.push({ id, kind, text })
  window.setTimeout(() => dismiss(id), ms)
}

function dismiss(id: number) {
  items.value = items.value.filter((t) => t.id !== id)
}

export const toast = {
  items,
  dismiss,
  ok: (text: string) => push('ok', text),
  err: (text: string) => push('err', text),
  info: (text: string) => push('info', text),
}
