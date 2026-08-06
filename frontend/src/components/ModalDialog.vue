<script setup lang="ts">
/** Markazda ochiladigan modal — forma oynalari uchun. */
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
    <Transition name="modal">
      <div v-if="open" class="wrap" role="dialog" aria-modal="true" :aria-label="title">
        <div class="box">
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
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.veil {
  position: fixed;
  inset: 0;
  z-index: 140;
  background: rgba(0, 0, 0, 0.55);
  backdrop-filter: blur(2px);
}
.wrap {
  position: fixed;
  inset: 0;
  z-index: 141;
  display: grid;
  place-items: center;
  padding: 18px;
  pointer-events: none;
}
.box {
  pointer-events: auto;
  width: min(430px, 100%);
  max-height: calc(100vh - 36px);
  display: flex;
  flex-direction: column;
  background: var(--frame);
  border: 1px solid var(--line);
  border-radius: var(--r-l);
  box-shadow: var(--shadow-pop);
  overflow: hidden;
}
header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 16px 13px;
  border-bottom: 1px solid var(--line-soft);
}
.ttl {
  flex: 1;
  min-width: 0;
}
.ttl h2 {
  font-family: var(--f-display);
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.02em;
}
.ttl p {
  font-size: 12px;
  color: var(--text-3);
  margin-top: 2px;
}
.body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
footer {
  padding: 13px 16px;
  border-top: 1px solid var(--line-soft);
  display: flex;
  gap: 9px;
}

.modal-enter-active,
.modal-leave-active {
  transition:
    opacity var(--dur-2) var(--ease-out),
    transform var(--dur-2) var(--ease-out);
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.97);
}

@media (max-width: 560px) {
  .wrap {
    place-items: end center;
    padding: 0;
  }
  .box {
    width: 100%;
    max-height: 88vh;
    border-radius: var(--r-l) var(--r-l) 0 0;
    border-bottom: 0;
  }
}
</style>
