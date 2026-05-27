<script setup lang="ts">
import { Moon, Sun } from 'lucide-vue-next'

import { Button } from '@/components/ui/button'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <Button variant="ghost" size="icon" @click="theme.toggleTheme()">
    <Sun v-if="theme.resolved === 'dark'" class="size-5" />
    <Moon v-else class="size-5" />
  </Button>
</template>
