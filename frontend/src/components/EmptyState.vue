<script setup lang="ts">
/** Bo'sh ekran — brend imzosi (girih yulduzi) shu yerda takrorlanadi. */
withDefaults(defineProps<{ title: string; note?: string; icon?: string }>(), { icon: 'i-inbox' })
</script>

<template>
  <div class="empty girih">
    <div class="mark">
      <svg class="ico" style="width: 30px; height: 30px"><use href="#star" /></svg>
    </div>
    <h3>{{ title }}</h3>
    <p v-if="note">{{ note }}</p>
    <div v-if="$slots.default" class="act"><slot /></div>
  </div>
</template>

<style scoped>
.empty {
  display: grid;
  place-items: center;
  text-align: center;
  padding: 48px 24px;
  border: 1px dashed var(--line);
  border-radius: var(--r-l);
  background-color: var(--surface);
  animation: fade var(--dur-3) var(--ease-out) both;
}
.mark {
  display: grid;
  place-items: center;
  width: 60px;
  height: 60px;
  border-radius: var(--r-l);
  background: var(--teal-glow);
  color: var(--teal);
  margin-bottom: 14px;
  animation: pulse-ring 2.6s var(--ease-out) infinite;
}
h3 {
  font-family: var(--f-display);
  font-size: 17px;
  font-weight: 600;
  letter-spacing: -0.01em;
}
p {
  font-size: 12.5px;
  color: var(--text-3);
  margin-top: 5px;
  max-width: 44ch;
  line-height: 1.6;
}
.act {
  margin-top: 16px;
}
</style>
