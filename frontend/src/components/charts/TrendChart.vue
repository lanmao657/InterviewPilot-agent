<template>
  <div ref="chartRef" class="w-full h-80"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import * as echarts from 'echarts'

import { useThemeStore } from '@/stores/theme'

interface TrendPoint {
  label: string
  overall: number
  clarity?: number
  structure?: number
  evidence?: number
  reflection?: number
}

interface Props {
  data: TrendPoint[]
  multiDimension?: boolean
}

const props = withDefaults(defineProps<Props>(), { multiDimension: false })
const theme = useThemeStore()
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const isDark = computed(() => theme.resolved === 'dark')

// 多维度配色
const dimColors = {
  overall: { light: '#3b82f6', dark: '#60a5fa' },
  clarity: { light: '#8b5cf6', dark: '#a78bfa' },
  structure: { light: '#10b981', dark: '#34d399' },
  evidence: { light: '#f59e0b', dark: '#fbbf24' },
  reflection: { light: '#ef4444', dark: '#f87171' },
}

const dimLabels: Record<string, string> = {
  overall: '总分',
  clarity: '表达清晰度',
  structure: '结构化程度',
  evidence: '证据充分度',
  reflection: '复盘深度',
}

const colors = computed(() => ({
  text: isDark.value ? '#f1f5f9' : '#1e293b',
  textSecondary: isDark.value ? '#94a3b8' : '#64748b',
  splitLine: isDark.value ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
  tooltipBg: isDark.value ? 'rgba(30, 41, 59, 0.95)' : 'rgba(255, 255, 255, 0.95)',
  tooltipBorder: isDark.value ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)',
}))

function getColor(dim: string): string {
  const c = dimColors[dim as keyof typeof dimColors]
  return c ? (isDark.value ? c.dark : c.light) : '#94a3b8'
}

function updateChart() {
  if (!chart) return
  const c = colors.value

  // 构建系列数据
  const dimensions = props.multiDimension
    ? ['overall', 'clarity', 'structure', 'evidence', 'reflection']
    : ['overall']

  const series = dimensions.map((dim) => ({
    name: dimLabels[dim] ?? dim,
    data: props.data.map((item) => (item as unknown as Record<string, number>)[dim] ?? 0),
    type: 'line' as const,
    smooth: true,
    lineStyle: { color: getColor(dim), width: dim === 'overall' ? 3 : 2 },
    itemStyle: { color: getColor(dim) },
    symbol: 'circle',
    symbolSize: dim === 'overall' ? 8 : 5,
    ...(dim === 'overall' && !props.multiDimension
      ? {
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: `${getColor(dim)}80` },
              { offset: 1, color: `${getColor(dim)}15` },
            ]),
          },
        }
      : {}),
  }))

  const option = {
    grid: { left: 48, right: 20, top: props.multiDimension ? 40 : 20, bottom: 32 },
    legend: props.multiDimension
      ? {
          data: dimensions.map((d) => dimLabels[d] ?? d),
          top: 0,
          textStyle: { color: c.textSecondary, fontSize: 11 },
          itemWidth: 16,
          itemHeight: 2,
        }
      : undefined,
    xAxis: {
      type: 'category',
      data: props.data.map((item) => item.label),
      axisLabel: { color: c.textSecondary },
      axisLine: { lineStyle: { color: c.splitLine } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: { color: c.textSecondary },
      splitLine: { lineStyle: { color: c.splitLine } },
    },
    tooltip: {
      trigger: 'axis',
      backgroundColor: c.tooltipBg,
      borderColor: c.tooltipBorder,
      textStyle: { color: c.text },
    },
    series,
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
