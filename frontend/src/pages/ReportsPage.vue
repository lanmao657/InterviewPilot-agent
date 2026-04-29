<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { FileBarChart } from 'lucide-vue-next'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { api } from '@/lib/api'

const reportsQuery = useQuery({ queryKey: ['reports'], queryFn: api.reports })
</script>

<template>
  <div class="grid gap-4 lg:grid-cols-2">
    <Card v-for="report in reportsQuery.data.value" :key="report.id">
      <CardHeader>
        <div class="flex items-start justify-between gap-3">
          <div>
            <CardTitle>{{ report.title }}</CardTitle>
            <CardDescription>STAR Feedback 复盘</CardDescription>
          </div>
          <Badge variant="accent">{{ report.overall_score }} 分</Badge>
        </div>
      </CardHeader>
      <CardContent class="flex flex-col gap-4">
        <Progress :value="report.overall_score" />
        <p class="whitespace-pre-line text-sm leading-6 text-muted-foreground">{{ report.content }}</p>
      </CardContent>
    </Card>
    <Card v-if="!reportsQuery.data.value?.length" class="lg:col-span-2">
      <CardHeader>
        <FileBarChart class="text-primary" />
        <CardTitle>还没有报告</CardTitle>
        <CardDescription>完成至少一轮模拟面试后生成复盘报告。</CardDescription>
      </CardHeader>
    </Card>
  </div>
</template>
