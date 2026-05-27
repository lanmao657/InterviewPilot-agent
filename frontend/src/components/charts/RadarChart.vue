<template>
  <div ref="chartRef" class="w-full h-80"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import * as echarts from 'echarts'

interface Props {
  data: {
    clarity: number
    structure: number
    evidence: number
    reflection: number
  }
}

const props = defineProps<Props>()
const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chart) return

  const option = {
    radar: {
      indicator: [
        { name: '表达清晰度', max: 100 },
        { name: '结构化程度', max: 100 },
        { name: '证据充分度', max: 100 },
        { name: '复盘深度', max: 100 },
      ],
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
            areaStyle: {
              color: 'rgba(59, 130, 246, 0.3)',
            },
            lineStyle: {
              color: '#3b82f6',
              width: 2,
            },
            itemStyle: {
              color: '#3b82f6',
            },
          },
        ],
      },
    ],
  }

  chart.setOption(option)
}

const handleResize = () => {
  chart?.resize()
}

watch(() => props.data, updateChart, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
  chart = null
})
</script>
