<script setup lang="ts">
import IconSprite from '@/components/IconSprite.vue'
</script>

<template>
  <div class="nf girih">
    <IconSprite />
    <svg class="mark"><use href="#star" /></svg>
    <h1 class="h-disp">Bu sahifa topilmadi</h1>
    <p>Manzil noto'g'ri yoki sahifa ko'chirilgan. Panelga qaytib, ishni davom ettiring.</p>
    <RouterLink to="/" class="btn btn-pri">Panelga qaytish</RouterLink>
  </div>
</template>

<style scoped>
.nf {
  min-height: 100vh;
  display: grid;
  place-content: center;
  justify-items: center;
  text-align: center;
  padding: 30px;
  gap: 4px;
}
.mark {
  width: 52px;
  height: 52px;
  color: var(--teal);
  margin-bottom: 16px;
  animation: pop var(--dur-3) var(--ease-out) both;
}
h1 {
  font-size: 27px;
}
p {
  color: var(--text-3);
  font-size: 13.5px;
  max-width: 42ch;
  margin: 8px 0 20px;
  line-height: 1.6;
}
</style>
