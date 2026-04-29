<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { Upload } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { api, type DocumentItem } from '@/lib/api'

const queryClient = useQueryClient()
const documentsQuery = useQuery({ queryKey: ['documents'], queryFn: api.documents })
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const targetRole = ref('高级前端工程师')
const resumeFile = ref<File | null>(null)
const jdFile = ref<File | null>(null)
const message = ref('')

const resumes = computed(() => documentsQuery.data.value?.filter((item) => item.kind === 'resume') ?? [])
const jds = computed(() => documentsQuery.data.value?.filter((item) => item.kind === 'job_description') ?? [])

const uploadMutation = useMutation({
  mutationFn: ({ kind, file }: { kind: 'resume' | 'job-description'; file: File }) => api.uploadDocument(kind, file),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['documents'] }),
})

const planMutation = useMutation({
  mutationFn: () =>
    api.createPlan({
      resume_id: resumes.value[0]?.id,
      job_description_id: jds.value[0]?.id,
      title: `${targetRole.value} 面试准备计划`,
      target_role: targetRole.value,
    }),
  onSuccess: () => {
    message.value = '准备计划已生成'
    queryClient.invalidateQueries({ queryKey: ['plans'] })
  },
})

async function upload(kind: 'resume' | 'job-description') {
  const file = kind === 'resume' ? resumeFile.value : jdFile.value
  if (!file) return
  await uploadMutation.mutateAsync({ kind, file })
  message.value = '上传并解析成功'
}

function preview(doc: DocumentItem) {
  return String(doc.summary.preview ?? '').slice(0, 120)
}
</script>

<template>
  <div class="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
    <Card>
      <CardHeader>
        <CardTitle>简历与 JD</CardTitle>
        <CardDescription>上传材料后生成岗位匹配准备计划。</CardDescription>
      </CardHeader>
      <CardContent class="flex flex-col gap-5">
        <label class="flex flex-col gap-2 text-sm font-medium">
          目标岗位
          <Input v-model="targetRole" />
        </label>
        <div class="rounded-lg border bg-background/70 p-4">
          <p class="text-sm font-semibold">简历</p>
          <input class="mt-3 text-sm" type="file" accept=".pdf,.docx,.txt" @change="resumeFile = ($event.target as HTMLInputElement).files?.[0] ?? null" />
          <Button class="mt-3" size="sm" :disabled="!resumeFile || uploadMutation.isPending.value" @click="upload('resume')">
            <Upload data-icon="inline-start" />
            上传简历
          </Button>
        </div>
        <div class="rounded-lg border bg-background/70 p-4">
          <p class="text-sm font-semibold">职位 JD</p>
          <input class="mt-3 text-sm" type="file" accept=".pdf,.docx,.txt" @change="jdFile = ($event.target as HTMLInputElement).files?.[0] ?? null" />
          <Button class="mt-3" size="sm" :disabled="!jdFile || uploadMutation.isPending.value" @click="upload('job-description')">
            <Upload data-icon="inline-start" />
            上传 JD
          </Button>
        </div>
        <Button :disabled="planMutation.isPending.value" @click="planMutation.mutate()">
          生成准备计划
        </Button>
        <p v-if="message" class="text-sm text-primary">{{ message }}</p>
      </CardContent>
    </Card>

    <Card>
      <CardHeader>
        <CardTitle>资料库</CardTitle>
        <CardDescription>最新计划数：{{ plansQuery.data.value?.length ?? 0 }}</CardDescription>
      </CardHeader>
      <CardContent class="flex flex-col gap-3">
        <div v-for="doc in documentsQuery.data.value" :key="doc.id" class="rounded-lg border bg-background/70 p-4">
          <div class="flex items-center justify-between gap-3">
            <p class="font-medium">{{ doc.filename }}</p>
            <Badge>{{ doc.kind === 'resume' ? '简历' : 'JD' }}</Badge>
          </div>
          <p class="mt-2 text-sm text-muted-foreground">{{ preview(doc) }}</p>
        </div>
        <p v-if="!documentsQuery.data.value?.length" class="text-sm text-muted-foreground">还没有上传资料。</p>
      </CardContent>
    </Card>
  </div>
</template>
