<script setup lang="ts">
defineProps<{ title: string; note?: string; eyebrow?: string }>()
</script>

<template>
  <header class="head anim-rise">
    <div>
      <span v-if="eyebrow" class="eyebrow">{{ eyebrow }}</span>
      <h1>{{ title }}</h1>
      <p v-if="note">{{ note }}</p>
    </div>
    <div class="act"><slot /></div>
  </header>
</template>

<style scoped>
.head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}
h1 {
  font-family: var(--f-display);
  font-size: 21px;
  font-weight: 600;
  letter-spacing: -0.02em;
  margin-top: 3px;
}
p {
  font-size: 12.5px;
  color: var(--text-3);
  margin-top: 2px;
}
.act {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
</style>
