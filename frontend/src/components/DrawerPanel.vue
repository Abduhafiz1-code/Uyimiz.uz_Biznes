<script setup lang="ts">
/** O'ngdan chiqadigan yon panel — mijoz/obyekt/bitim tafsilotlari uchun. */
import { onBeforeUnmount, watch } from 'vue'

import UiIcon from './UiIcon.vue'

const props = defineProps<{ open: boolean; title: string; subtitle?: string }>()
const emit = defineEmits<{ close: [] }>()

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

watch(
  () => props.open,
  (open) => {
    document.body.style.overflow = open ? 'hidden' : ''
    if (open) window.addEventListener('keydown', onKey)
    else window.removeEventListener('keydown', onKey)
  },
)

onBeforeUnmount(() => {
  document.body.style.overflow = ''
  window.removeEventListener('keydown', onKey)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="veil">
      <div v-if="open" class="veil" @click="emit('close')" />
    </Transition>
    <Transition name="drawer">
      <aside v-if="open" class="drawer" role="dialog" aria-modal="true" :aria-label="title">
        <header>
          <div class="ttl">
            <h2>{{ title }}</h2>
            <p v-if="subtitle">{{ subtitle }}</p>
          </div>
          <button class="btn btn-ghost btn-icon" aria-label="Yopish" @click="emit('close')">
            <UiIcon name="i-x" :size="16" />
          </button>
        </header>
        <div class="body"><slot /></div>
        <footer v-if="$slots.footer"><slot name="footer" /></footer>
      </aside>
    </Transition>
  </Teleport>
</template>

<style scoped>
.veil {
  position: fixed;
  inset: 0;
  z-index: 120;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
}
.drawer {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 121;
  width: min(430px, 100vw);
  display: flex;
  flex-direction: column;
  background: var(--frame);
  border-left: 1px solid var(--line);
  box-shadow: var(--shadow-pop);
}
header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 18px 18px 14px;
  border-bottom: 1px solid var(--line-soft);
}
.ttl {
  flex: 1;
  min-width: 0;
}
.ttl h2 {
  font-family: var(--f-display);
  font-size: 19px;
  font-weight: 600;
  letter-spacing: -0.02em;
}
.ttl p {
  font-size: 12.5px;
  color: var(--text-3);
  margin-top: 2px;
}
.body {
  flex: 1;
  overflow-y: auto;
  padding: 18px;
}
footer {
  padding: 14px 18px;
  border-top: 1px solid var(--line-soft);
  display: flex;
  gap: 9px;
}
</style>
