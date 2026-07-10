<script setup lang="ts">
import { Moon, Sun } from 'lucide-vue-next'

import { Button } from '@/components/ui/button'
import { useThemeStore } from '@/stores/theme'

const theme = useThemeStore()
</script>

<template>
  <Button
    variant="ghost"
    size="icon"
    :aria-label="theme.resolved === 'dark' ? '切换为浅色主题' : '切换为深色主题'"
    :title="theme.resolved === 'dark' ? '切换为浅色主题' : '切换为深色主题'"
    @click="theme.toggleTheme()"
  >
    <Sun v-if="theme.resolved === 'dark'" class="size-5" />
    <Moon v-else class="size-5" />
  </Button>
</template>
