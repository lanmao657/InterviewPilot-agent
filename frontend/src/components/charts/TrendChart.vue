<template>
  <div ref="chartRef" class="w-full h-80"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import { LineChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import type { ECharts } from 'echarts/core'

import { useThemeStore } from '@/stores/theme'

echarts.use([LineChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

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
let chart: ECharts | null = null

const isDark = computed(() => theme.resolved === 'dark')

// 多维度配色
const dimColors = {
  overall: { light: '#9f432f', dark: '#f08b70' },
  clarity: { light: '#32675f', dark: '#78b9ae' },
  structure: { light: '#5e6d3c', dark: '#a9bd78' },
  evidence: { light: '#946313', dark: '#e3b66b' },
  reflection: { light: '#5c5a78', dark: '#aaa7d1' },
}

const dimLabels: Record<string, string> = {
  overall: '总分',
  clarity: '表达清晰度',
  structure: '结构化程度',
  evidence: '证据充分度',
  reflection: '复盘深度',
}

const colors = computed(() => ({
  text: isDark.value ? '#f2ede5' : '#292621',
  textSecondary: isDark.value ? '#c1b9ad' : '#5f5a52',
  splitLine: isDark.value ? '#443e36' : '#d8d0c4',
  tooltipBg: isDark.value ? '#2b2722' : '#ffffff',
  tooltipBorder: isDark.value ? '#5b5348' : '#d8d0c4',
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
    smooth: false,
    lineStyle: { color: getColor(dim), width: dim === 'overall' ? 3 : 2 },
    itemStyle: { color: getColor(dim) },
    symbol: 'circle',
    symbolSize: dim === 'overall' ? 8 : 5,
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
