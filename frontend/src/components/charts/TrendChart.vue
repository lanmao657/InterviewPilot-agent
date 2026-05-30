<template>
  <div ref="chartRef" class="w-full h-80"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import * as echarts from 'echarts'

import { useThemeStore } from '@/stores/theme'

interface Props {
  data: Array<{
    date: string
    score: number
  }>
}

const props = defineProps<Props>()
const theme = useThemeStore()
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const isDark = computed(() => theme.resolved === 'dark')

const colors = computed(() => ({
  primary: isDark.value ? '#60a5fa' : '#3b82f6',
  gradientStart: isDark.value ? 'rgba(96, 165, 250, 0.5)' : 'rgba(59, 130, 246, 0.5)',
  gradientEnd: isDark.value ? 'rgba(96, 165, 250, 0.1)' : 'rgba(59, 130, 246, 0.1)',
  text: isDark.value ? '#f1f5f9' : '#1e293b',
  textSecondary: isDark.value ? '#94a3b8' : '#64748b',
  splitLine: isDark.value ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
  tooltipBg: isDark.value ? 'rgba(30, 41, 59, 0.95)' : 'rgba(255, 255, 255, 0.95)',
  tooltipBorder: isDark.value ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.08)',
}))

function updateChart() {
  if (!chart) return

  const c = colors.value
  const option = {
    grid: { left: 48, right: 20, top: 20, bottom: 32 },
    xAxis: {
      type: 'category',
      data: props.data.map((item) => item.date),
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
    series: [
      {
        data: props.data.map((item) => item.score),
        type: 'line',
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: c.gradientStart },
            { offset: 1, color: c.gradientEnd },
          ]),
        },
        lineStyle: { color: c.primary, width: 3 },
        itemStyle: { color: c.primary },
        symbol: 'circle',
        symbolSize: 8,
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
