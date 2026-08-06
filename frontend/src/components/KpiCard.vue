<script setup lang="ts">
import CountUp from './CountUp.vue'
import Sparkline from './Sparkline.vue'
import UiIcon from './UiIcon.vue'

withDefaults(
  defineProps<{
    label: string
    value: number
    unit?: string
    delta?: number | null
    icon?: string
    tone?: 'teal' | 'brass' | 'plain'
    spark?: number[]
    digits?: number
  }>(),
  { tone: 'plain', digits: 0 },
)
</script>

<template>
  <article class="kpi" :class="`t-${tone}`">
    <header>
      <span class="lbl">{{ label }}</span>
      <span v-if="icon" class="chip"><UiIcon :name="icon" :size="14" /></span>
    </header>

    <div class="val">
      <b><CountUp :value="value" :digits="digits" /></b>
      <span v-if="unit" class="unit">{{ unit }}</span>
      <span v-if="delta != null && delta !== 0" class="delta">+{{ delta }}</span>
    </div>

    <Sparkline v-if="spark && spark.length > 1" :points="spark" class="spark" />
  </article>
</template>

<style scoped>
.kpi {
  position: relative;
  padding: 15px;
  border-radius: var(--r-m);
  background: var(--surface);
  border: 1px solid var(--line-soft);
  overflow: hidden;
  transition:
    transform var(--dur-2) var(--ease-out),
    border-color var(--dur-2) var(--ease-out),
    box-shadow var(--dur-2) var(--ease-out);
}
.kpi:hover {
  transform: translateY(-3px);
  border-color: var(--line);
  box-shadow: var(--shadow-card);
}

/* rangli ohang — yuqori chetdagi nozik yorug'lik */
.kpi::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 90px;
  opacity: 0;
  transition: opacity var(--dur-2) var(--ease-out);
  pointer-events: none;
}
.t-teal::before {
  background: radial-gradient(180px 70px at 18% 0%, var(--teal-glow), transparent 70%);
  opacity: 1;
}
.t-brass::before {
  background: radial-gradient(180px 70px at 18% 0%, var(--brass-glow), transparent 70%);
  opacity: 1;
}

header {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}
.lbl {
  font-size: 11px;
  color: var(--text-3);
  line-height: 1.35;
}
.chip {
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: var(--surface-2);
  color: var(--text-3);
  flex: none;
  transition: color var(--dur-2) var(--ease-out);
}
.t-teal .chip {
  color: var(--teal);
  background: var(--teal-glow);
}
.t-brass .chip {
  color: var(--brass);
  background: var(--brass-glow);
}

.val {
  position: relative;
  display: flex;
  align-items: baseline;
  gap: 5px;
}
.val b {
  font-family: var(--f-display);
  font-size: 23px;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text);
}
.t-brass .val b {
  color: var(--brass);
}
.unit {
  font-size: 13px;
  color: var(--text-2);
  font-weight: 600;
}
.delta {
  font-size: 11px;
  color: var(--teal);
  margin-left: 2px;
  font-weight: 700;
}

.spark {
  margin-top: 10px;
}
</style>
