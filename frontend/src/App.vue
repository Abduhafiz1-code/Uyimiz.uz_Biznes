<script setup lang="ts">
import { onMounted } from 'vue'

import IconSprite from '@/components/IconSprite.vue'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()

// index.html mavzuni birinchi bo'yoqdan oldin qo'yadi; bu yerda store bilan moslaymiz.
onMounted(() => theme.apply())
</script>

<template>
  <IconSprite />
  <RouterView />
</template>
