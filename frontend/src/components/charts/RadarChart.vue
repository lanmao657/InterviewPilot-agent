<template>
  <div ref="chartRef" class="w-full h-80"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import { RadarChart } from 'echarts/charts'
import { LegendComponent, TooltipComponent } from 'echarts/components'
import * as echarts from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import type { ECharts } from 'echarts/core'

import { useThemeStore } from '@/stores/theme'

echarts.use([RadarChart, TooltipComponent, LegendComponent, CanvasRenderer])

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
let chart: ECharts | null = null

const isDark = computed(() => theme.resolved === 'dark')

const colors = computed(() => ({
  primary: isDark.value ? '#f08b70' : '#9f432f',
  primaryAlpha: isDark.value ? 'rgba(240, 139, 112, 0.18)' : 'rgba(159, 67, 47, 0.14)',
  text: isDark.value ? '#f2ede5' : '#292621',
  textSecondary: isDark.value ? '#c1b9ad' : '#5f5a52',
  splitLine: isDark.value ? '#443e36' : '#d8d0c4',
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
