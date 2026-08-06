<script setup lang="ts">
/** Kichik trend chizig'i — KPI kartalari ostida. Chizilishi animatsiyalanadi. */
import { computed } from 'vue'

const props = withDefaults(defineProps<{ points: number[]; height?: number }>(), { height: 26 })

const W = 100

const geometry = computed(() => {
  const pts = props.points
  const max = Math.max(...pts)
  const min = Math.min(...pts)
  const span = max - min || 1
  const step = W / Math.max(pts.length - 1, 1)
  const coords = pts.map((p, i) => {
    const x = i * step
    const y = props.height - 3 - ((p - min) / span) * (props.height - 6)
    return `${x.toFixed(2)},${y.toFixed(2)}`
  })
  return {
    line: `M${coords.join(' L')}`,
    area: `M0,${props.height} L${coords.join(' L')} L${W},${props.height} Z`,
  }
})

const uid = `sparkfill-${Math.random().toString(36).slice(2, 9)}`
</script>

<template>
  <svg class="spark" :viewBox="`0 0 ${W} ${height}`" preserveAspectRatio="none" aria-hidden="true">
    <defs>
      <linearGradient :id="uid" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="var(--teal)" stop-opacity="0.28" />
        <stop offset="100%" stop-color="var(--teal)" stop-opacity="0" />
      </linearGradient>
    </defs>
    <path :d="geometry.area" :fill="`url(#${uid})`" class="area" />
    <path :d="geometry.line" fill="none" stroke="var(--teal)" stroke-width="1.6" class="line" />
  </svg>
</template>

<style scoped>
.spark {
  display: block;
  width: 100%;
  height: v-bind('height + "px"');
  overflow: visible;
}
.line {
  stroke-dasharray: 240;
  stroke-dashoffset: 240;
  animation: draw 1.1s var(--ease-out) 0.15s forwards;
  vector-effect: non-scaling-stroke;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.area {
  opacity: 0;
  animation: fade 0.7s var(--ease-out) 0.6s forwards;
}
@keyframes draw {
  to {
    stroke-dashoffset: 0;
  }
}
</style>
