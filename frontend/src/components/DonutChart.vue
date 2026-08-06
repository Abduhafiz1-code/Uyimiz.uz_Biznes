<script setup lang="ts">
/** Voronka taqsimoti uchun halqa diagramma — Bitimlar sahifasida. */
import { computed } from 'vue'

const props = defineProps<{
  slices: { label: string; value: number; color: string }[]
  centerValue?: string | number
  centerLabel?: string
}>()

const R = 42
const C = 2 * Math.PI * R

const total = computed(() => props.slices.reduce((s, x) => s + x.value, 0))

const arcs = computed(() => {
  let acc = 0
  return props.slices.map((s) => {
    const frac = total.value ? s.value / total.value : 0
    const arc = {
      ...s,
      dash: `${(frac * C).toFixed(2)} ${(C - frac * C).toFixed(2)}`,
      offset: (-acc * C).toFixed(2),
      percent: Math.round(frac * 100),
    }
    acc += frac
    return arc
  })
})
</script>

<template>
  <div class="donut-wrap">
    <svg viewBox="0 0 110 110" class="donut" role="img" aria-label="Bitimlar taqsimoti">
      <circle cx="55" cy="55" :r="R" fill="none" stroke="var(--surface-2)" stroke-width="13" />
      <circle
        v-for="(a, i) in arcs"
        :key="a.label"
        cx="55"
        cy="55"
        :r="R"
        fill="none"
        :stroke="a.color"
        stroke-width="13"
        stroke-linecap="butt"
        :stroke-dasharray="a.dash"
        :stroke-dashoffset="a.offset"
        transform="rotate(-90 55 55)"
        class="arc"
        :style="{ animationDelay: `${i * 0.08}s` }"
      />
    </svg>
    <div v-if="centerValue !== undefined" class="center">
      <b>{{ centerValue }}</b>
      <small v-if="centerLabel">{{ centerLabel }}</small>
    </div>
  </div>
</template>

<style scoped>
.donut-wrap {
  position: relative;
  width: 132px;
  height: 132px;
  flex: none;
}
.donut {
  width: 100%;
  height: 100%;
}
.arc {
  opacity: 0;
  animation: fade 0.5s var(--ease-out) forwards;
  transition: stroke-dasharray 0.6s var(--ease-out);
}
.center {
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  text-align: center;
  pointer-events: none;
}
.center b {
  display: block;
  font-family: var(--f-display);
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.center small {
  font-size: 10.5px;
  color: var(--text-3);
}
</style>
