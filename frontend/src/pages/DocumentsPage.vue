<!-- frontend/src/pages/DocumentsPage.vue -->
<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { FileText, Upload } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
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
  onSuccess: () => {
    message.value = '上传并解析成功'
    queryClient.invalidateQueries({ queryKey: ['documents'] })
  },
  onError: (err: Error) => {
    message.value = `上传失败：${err.message}`
  },
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
  if (!file) {
    message.value = '请先选择文件'
    return
  }
  message.value = ''
  uploadMutation.mutate({ kind, file })
}

function preview(doc: DocumentItem) {
  return String(doc.summary.preview ?? '').slice(0, 120)
}
</script>

<template>
  <div class="grid gap-5 xl:grid-cols-[0.9fr_1.1fr]">
    <!-- 上传区域 -->
    <div class="glass rounded-2xl p-6">
      <h2 class="text-lg font-semibold">简历与 JD</h2>
      <p class="mb-5 text-sm text-[var(--text-secondary)]">上传材料后生成岗位匹配准备计划</p>

      <div class="flex flex-col gap-5">
        <label class="flex flex-col gap-2 text-sm font-medium">
          目标岗位
          <Input v-model="targetRole" />
        </label>

        <div class="glass-flat rounded-xl p-4">
          <p class="mb-3 text-sm font-semibold">简历</p>
          <input class="text-sm" type="file" accept=".pdf,.docx,.pptx,.txt" @change="resumeFile = ($event.target as HTMLInputElement).files?.[0] ?? null" />
          <Button class="mt-3" size="sm" :disabled="!resumeFile || uploadMutation.isPending.value" @click="upload('resume')">
            <Upload class="size-4" />
            上传简历
          </Button>
        </div>

        <div class="glass-flat rounded-xl p-4">
          <p class="mb-3 text-sm font-semibold">职位 JD</p>
          <input class="text-sm" type="file" accept=".pdf,.docx,.pptx,.txt" @change="jdFile = ($event.target as HTMLInputElement).files?.[0] ?? null" />
          <Button class="mt-3" size="sm" :disabled="!jdFile || uploadMutation.isPending.value" @click="upload('job-description')">
            <Upload class="size-4" />
            上传 JD
          </Button>
        </div>

        <Button :disabled="planMutation.isPending.value" @click="planMutation.mutate()">
          生成准备计划
        </Button>
        <p v-if="message" class="text-sm text-[var(--primary)]">{{ message }}</p>
      </div>
    </div>

    <!-- 资料库 -->
    <div class="glass rounded-2xl p-6">
      <h2 class="text-lg font-semibold">资料库</h2>
      <p class="mb-5 text-sm text-[var(--text-secondary)]">最新计划数：{{ plansQuery.data.value?.length ?? 0 }}</p>

      <div class="flex flex-col gap-3">
        <div
          v-for="(doc, index) in documentsQuery.data.value"
          :key="doc.id"
          class="glass-flat rounded-xl p-4 animate-stagger"
          :style="{ '--stagger-index': index }"
        >
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <FileText class="size-4 text-[var(--primary)]" />
              <p class="font-medium">{{ doc.filename }}</p>
            </div>
            <Badge :variant="doc.kind === 'resume' ? 'default' : 'accent'">
              {{ doc.kind === 'resume' ? '简历' : 'JD' }}
            </Badge>
          </div>
          <p class="mt-2 text-sm text-[var(--text-muted)]">{{ preview(doc) }}</p>
        </div>
        <p v-if="!documentsQuery.data.value?.length" class="text-sm text-[var(--text-muted)]">还没有上传资料。</p>
      </div>
    </div>
  </div>
</template>
