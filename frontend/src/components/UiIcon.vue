<script setup lang="ts">
defineProps<{ name: string; size?: number | string }>()
</script>

<template>
  <svg class="ico" :style="{ width: (size ?? 16) + 'px', height: (size ?? 16) + 'px' }" aria-hidden="true">
    <use :href="`#${name}`" />
  </svg>
</template>
