<script setup lang="ts">
/**
 * Mavzu almashtirgichi — dizayn taxtasining ikki varianti o'rtasida:
 * qorong'i (uyimiz-figma-board_2) va yorug' (uyimiz-figma-board-oq).
 */
import { useThemeStore } from '@/stores/theme'
import UiIcon from './UiIcon.vue'

const theme = useThemeStore()
</script>

<template>
  <button
    class="toggle"
    type="button"
    role="switch"
    :aria-checked="theme.isDark"
    :title="`${theme.label} mavzuga o'tish`"
    @click="theme.toggle()"
  >
    <span class="knob" :class="{ right: !theme.isDark }"></span>
    <span class="side" :class="{ on: theme.isDark }"><UiIcon name="i-moon" :size="13" /></span>
    <span class="side" :class="{ on: !theme.isDark }"><UiIcon name="i-sun" :size="13" /></span>
    <span class="sr-only">{{ theme.label }} mavzu</span>
  </button>
</template>

<style scoped>
.toggle {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  padding: 3px;
  border-radius: 20px;
  border: 1px solid var(--line);
  background: var(--surface-2);
  cursor: pointer;
  transition:
    border-color var(--dur-1) var(--ease-out),
    background-color var(--dur-2) var(--ease-in-out);
}
.toggle:hover {
  border-color: var(--teal);
}

.knob {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--teal);
  box-shadow: 0 3px 10px -3px var(--teal);
  transition: transform var(--dur-2) var(--ease-out);
}
.knob.right {
  transform: translateX(28px);
}

.side {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  color: var(--text-3);
  transition: color var(--dur-2) var(--ease-out);
}
.side.on {
  color: var(--on-teal);
}
</style>
