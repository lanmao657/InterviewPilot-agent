<script setup lang="ts">
import { onMounted } from 'vue'

import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
onMounted(() => theme.initSystemListener())
</script>

<template>
  <RouterView />
</template>
