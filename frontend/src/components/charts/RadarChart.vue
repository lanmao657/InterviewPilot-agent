<template>
  <div ref="chartRef" class="w-full h-80"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import * as echarts from 'echarts'

import { useThemeStore } from '@/stores/theme'

interface Props {
  data: {
    clarity: number
    structure: number
    evidence: number
    reflection: number
  }
}

const props = defineProps<Props>()
const theme = useThemeStore()
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const isDark = computed(() => theme.resolved === 'dark')

const colors = computed(() => ({
  primary: isDark.value ? '#60a5fa' : '#3b82f6',
  primaryAlpha: isDark.value ? 'rgba(96, 165, 250, 0.3)' : 'rgba(59, 130, 246, 0.3)',
  text: isDark.value ? '#f1f5f9' : '#1e293b',
  textSecondary: isDark.value ? '#94a3b8' : '#64748b',
  splitLine: isDark.value ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)',
}))

function updateChart() {
  if (!chart) return

  const c = colors.value
  const option = {
    radar: {
      indicator: [
        { name: '表达清晰度', max: 100 },
        { name: '结构化程度', max: 100 },
        { name: '证据充分度', max: 100 },
        { name: '复盘深度', max: 100 },
      ],
      axisName: { color: c.textSecondary },
      splitLine: { lineStyle: { color: c.splitLine } },
      splitArea: { show: false },
      axisLine: { lineStyle: { color: c.splitLine } },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: [
              props.data.clarity,
              props.data.structure,
              props.data.evidence,
              props.data.reflection,
            ],
            name: '能力维度',
            areaStyle: { color: c.primaryAlpha },
            lineStyle: { color: c.primary, width: 2 },
            itemStyle: { color: c.primary },
          },
        ],
      },
    ],
  }

  chart.setOption(option, true)
}

const handleResize = () => chart?.resize()

watch(() => props.data, updateChart, { deep: true })
watch(isDark, updateChart)

onMounted(() => {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value)
  updateChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})
</script>
