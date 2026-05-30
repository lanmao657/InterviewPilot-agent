<!-- frontend/src/pages/DocumentsPage.vue -->
<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { ChevronDown, ChevronUp, ClipboardPaste, FileText, Loader2, Stethoscope, Trash2, Upload } from 'lucide-vue-next'
import { computed, ref } from 'vue'

import ResumeAnalysis from '@/components/ResumeAnalysis.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { api, type DocumentItem } from '@/lib/api'

const queryClient = useQueryClient()
const documentsQuery = useQuery({ queryKey: ['documents'], queryFn: api.documents })
const plansQuery = useQuery({ queryKey: ['plans'], queryFn: api.plans })
const targetRole = ref('高级前端工程师')
const resumeFile = ref<File | null>(null)
const jdFile = ref<File | null>(null)
const jdText = ref('')
const jdTab = ref<'file' | 'text'>('file')
const message = ref('')
const resumeInputRef = ref<HTMLInputElement | null>(null)
const jdInputRef = ref<HTMLInputElement | null>(null)

// 展开/收起全文预览
const expandedDocId = ref<number | null>(null)
// 删除确认
const deleteConfirmId = ref<number | null>(null)
// 诊断展开
const analyzingId = ref<number | null>(null)

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

const deleteMutation = useMutation({
  mutationFn: (id: number) => api.deleteDocument(id),
  onSuccess: () => {
    deleteConfirmId.value = null
    message.value = '文档已删除'
    queryClient.invalidateQueries({ queryKey: ['documents'] })
  },
  onError: (err: Error) => {
    message.value = `删除失败：${err.message}`
  },
})

const analyzeMutation = useMutation({
  mutationFn: (id: number) => api.analyzeDocument(id),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['documents'] })
  },
  onError: (err: Error) => {
    message.value = `诊断失败：${err.message}`
  },
})

const jdTextMutation = useMutation({
  mutationFn: (text: string) => api.uploadJDText(text),
  onSuccess: () => {
    jdText.value = ''
    message.value = 'JD 文本上传并解析成功'
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
  if (!file) return
  message.value = ''
  uploadMutation.mutate({ kind, file })
}

function handleFileSelect(kind: 'resume' | 'job-description', event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  if (kind === 'resume') {
    resumeFile.value = file
  } else {
    jdFile.value = file
  }

  upload(kind)
}

function preview(doc: DocumentItem) {
  return String(doc.summary.preview ?? '').slice(0, 120)
}

function toggleExpand(docId: number) {
  expandedDocId.value = expandedDocId.value === docId ? null : docId
}

function confirmDelete(docId: number) {
  deleteConfirmId.value = docId
}

function cancelDelete() {
  deleteConfirmId.value = null
}

// 格式化上传时间
function formatTime(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
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
          <input
            ref="resumeInputRef"
            hidden
            type="file"
            accept=".pdf,.docx,.pptx,.txt"
            @change="handleFileSelect('resume', $event)"
          />
          <Button
            class="mt-3"
            size="sm"
            :disabled="uploadMutation.isPending.value"
            @click="resumeInputRef?.click()"
          >
            <Upload class="size-4" />
            {{ resumeFile ? resumeFile.name : '选择并上传简历' }}
          </Button>
        </div>

        <div class="glass-flat rounded-xl p-4">
          <div class="mb-3 flex items-center justify-between">
            <p class="text-sm font-semibold">职位 JD</p>
            <div class="flex rounded-lg bg-[var(--bg-input)] p-0.5">
              <button
                class="rounded-md px-2.5 py-1 text-xs font-medium transition-all"
                :class="jdTab === 'file' ? 'bg-[var(--primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'"
                @click="jdTab = 'file'"
              >
                <Upload class="inline size-3 mr-1" />上传文件
              </button>
              <button
                class="rounded-md px-2.5 py-1 text-xs font-medium transition-all"
                :class="jdTab === 'text' ? 'bg-[var(--primary)] text-white shadow-sm' : 'text-[var(--text-muted)] hover:text-[var(--text-primary)]'"
                @click="jdTab = 'text'"
              >
                <ClipboardPaste class="inline size-3 mr-1" />粘贴文本
              </button>
            </div>
          </div>

          <!-- 文件上传模式 -->
          <template v-if="jdTab === 'file'">
            <input
              ref="jdInputRef"
              hidden
              type="file"
              accept=".pdf,.docx,.pptx,.txt"
              @change="handleFileSelect('job-description', $event)"
            />
            <Button
              class="mt-1"
              size="sm"
              :disabled="uploadMutation.isPending.value"
              @click="jdInputRef?.click()"
            >
              <Upload class="size-4" />
              {{ jdFile ? jdFile.name : '选择并上传 JD' }}
            </Button>
          </template>

          <!-- 文本粘贴模式 -->
          <template v-else>
            <Textarea
              v-model="jdText"
              class="min-h-32 mt-1"
              placeholder="粘贴职位描述内容，至少 10 个字符..."
            />
            <p class="mt-1 text-right text-xs text-[var(--text-muted)]">{{ jdText.length }} 字</p>
            <Button
              class="mt-2"
              size="sm"
              :disabled="jdText.length < 10 || jdTextMutation.isPending.value"
              @click="jdTextMutation.mutate(jdText)"
            >
              <ClipboardPaste class="size-4" />
              {{ jdTextMutation.isPending.value ? '解析中...' : '提交 JD 文本' }}
            </Button>
          </template>
        </div>

        <Button :disabled="planMutation.isPending.value" @click="planMutation.mutate()">
          生成准备计划
        </Button>
        <p v-if="message" class="text-sm" :class="message.includes('失败') ? 'text-[var(--error)]' : 'text-[var(--primary)]'">
          {{ message }}
        </p>
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
          <!-- 文档头部信息 -->
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2 min-w-0">
              <FileText class="size-4 shrink-0 text-[var(--primary)]" />
              <p class="truncate font-medium">{{ doc.filename }}</p>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <Badge :variant="doc.kind === 'resume' ? 'default' : 'accent'">
                {{ doc.kind === 'resume' ? '简历' : 'JD' }}
              </Badge>
              <span class="text-xs text-[var(--text-muted)]">{{ formatTime(doc.created_at) }}</span>
            </div>
          </div>

          <!-- 预览文本 -->
          <p class="mt-2 text-sm text-[var(--text-muted)]">
            {{ expandedDocId === doc.id ? String(doc.summary.preview ?? '') : preview(doc) }}
          </p>

          <!-- 操作按钮 -->
          <div class="mt-3 flex items-center gap-2">
            <Button variant="ghost" size="sm" @click="toggleExpand(doc.id)">
              <ChevronUp v-if="expandedDocId === doc.id" class="size-3" />
              <ChevronDown v-else class="size-3" />
              {{ expandedDocId === doc.id ? '收起' : '查看全文' }}
            </Button>

            <!-- 简历诊断按钮（仅简历类型显示） -->
            <Button
              v-if="doc.kind === 'resume'"
              variant="ghost"
              size="sm"
              :disabled="analyzeMutation.isPending.value && analyzingId === doc.id"
              @click="analyzeMutation.mutate(doc.id); analyzingId = doc.id"
            >
              <Loader2 v-if="analyzeMutation.isPending.value && analyzingId === doc.id" class="size-3 animate-spin" />
              <Stethoscope v-else class="size-3" />
              {{ doc.analysis ? '查看诊断' : 'AI 诊断' }}
            </Button>

            <!-- 删除确认流程 -->
            <template v-if="deleteConfirmId === doc.id">
              <span class="text-xs text-[var(--error)]">确认删除？</span>
              <Button variant="ghost" size="sm" class="text-[var(--error)]" :disabled="deleteMutation.isPending.value" @click="deleteMutation.mutate(doc.id)">
                确认
              </Button>
              <Button variant="ghost" size="sm" @click="cancelDelete">取消</Button>
            </template>
            <Button v-else variant="ghost" size="sm" class="text-[var(--text-muted)] hover:text-[var(--error)]" @click="confirmDelete(doc.id)">
              <Trash2 class="size-3" />
              删除
            </Button>
          </div>

          <!-- 简历诊断结果展示 -->
          <div v-if="doc.analysis && doc.kind === 'resume'" class="mt-4 rounded-xl glass p-4">
            <ResumeAnalysis :data="doc.analysis as any" />
          </div>
        </div>
        <p v-if="!documentsQuery.data.value?.length" class="text-sm text-[var(--text-muted)]">还没有上传资料。</p>
      </div>
    </div>
  </div>
</template>
