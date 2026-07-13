import { describe, expect, it } from 'vitest'

import radarSource from './RadarChart.vue?raw'
import trendSource from './TrendChart.vue?raw'

const chartSources = [radarSource, trendSource]

describe('chart imports', () => {
  it('uses ECharts core imports instead of the full bundle', () => {
    for (const source of chartSources) {
      expect(source).not.toContain("from 'echarts'")
      expect(source).toContain("from 'echarts/core'")
    }
  })
})
