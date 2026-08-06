<script setup lang="ts">
/** Raqamni 0 dan berilgan qiymatgacha yumshoq sanaydi (KPI kartalari uchun). */
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { nf } from '@/lib/format'

const props = withDefaults(
  defineProps<{ value: number; duration?: number; digits?: number }>(),
  { duration: 900, digits: 0 },
)

const shown = ref(0)
let frame = 0
let guard = 0

function stop() {
  cancelAnimationFrame(frame)
  window.clearTimeout(guard)
}

function run(to: number) {
  stop()
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  // Yashirin tabda requestAnimationFrame ishlamaydi — bunday holda darhol
  // yakuniy qiymatni ko'rsatamiz, aks holda raqam 0 bo'lib qolib ketadi.
  if (reduced || props.duration === 0 || document.hidden) {
    shown.value = to
    return
  }

  const start = performance.now()
  const step = (now: number) => {
    const p = Math.min((now - start) / props.duration, 1)
    // easeOutCubic
    shown.value = to * (1 - Math.pow(1 - p, 3))
    if (p < 1) frame = requestAnimationFrame(step)
    else shown.value = to
  }
  frame = requestAnimationFrame(step)

  // Kadr umuman kelmasa ham, qiymat baribir to'g'ri ko'rinsin.
  guard = window.setTimeout(() => {
    if (shown.value !== to) {
      cancelAnimationFrame(frame)
      shown.value = to
    }
  }, props.duration + 120)
}

onMounted(() => run(props.value))
watch(() => props.value, (v) => run(v))
onBeforeUnmount(stop)
</script>

<template>
  <span>{{ nf(shown, digits) }}</span>
</template>
