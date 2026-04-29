<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>设置</CardTitle>
      <CardDescription>模型配置通过后端环境变量管理，前端只展示当前说明。</CardDescription>
    </CardHeader>
    <CardContent class="grid gap-4 md:grid-cols-2">
      <label class="flex flex-col gap-2 text-sm font-medium">
        API 地址
        <Input model-value="VITE_API_BASE_URL=http://localhost:8000/api" readonly />
      </label>
      <label class="flex flex-col gap-2 text-sm font-medium">
        模型配置
        <Input model-value="AI_BASE_URL / AI_API_KEY / AI_MODEL" readonly />
      </label>
    </CardContent>
  </Card>
</template>
