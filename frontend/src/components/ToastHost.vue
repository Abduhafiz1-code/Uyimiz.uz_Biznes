<script setup lang="ts">
import { toast } from '@/stores/toast'
import UiIcon from './UiIcon.vue'

const icons: Record<string, string> = { ok: 'i-check', err: 'i-x', info: 'i-bell' }
</script>

<template>
  <TransitionGroup name="toast" tag="div" class="host">
    <div v-for="t in toast.items.value" :key="t.id" class="toast" :class="t.kind" role="status">
      <UiIcon :name="icons[t.kind]" :size="15" />
      <span>{{ t.text }}</span>
      <button class="close" aria-label="Yopish" @click="toast.dismiss(t.id)">
        <UiIcon name="i-x" :size="13" />
      </button>
    </div>
  </TransitionGroup>
</template>

<style scoped>
.host {
  position: fixed;
  right: 18px;
  bottom: 18px;
  z-index: 200;
  display: flex;
  flex-direction: column;
  gap: 9px;
  pointer-events: none;
}
.toast {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 236px;
  max-width: 360px;
  padding: 11px 12px;
  border-radius: var(--r-m);
  background: var(--surface);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-pop);
  font-size: 13px;
  color: var(--text);
}
.toast.ok {
  border-color: color-mix(in srgb, var(--teal) 45%, transparent);
  color: var(--teal);
}
.toast.err {
  border-color: color-mix(in srgb, var(--rose) 45%, transparent);
  color: var(--rose);
}
.toast span {
  flex: 1;
  color: var(--text);
}
.close {
  background: none;
  border: 0;
  color: var(--text-3);
  cursor: pointer;
  padding: 2px;
  display: grid;
  place-items: center;
}
.close:hover {
  color: var(--text);
}
</style>
