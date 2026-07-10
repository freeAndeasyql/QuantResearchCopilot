<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { StockIndicatorItem, StockPriceItem } from '@/api/stocks'

const props = defineProps<{
  prices: StockPriceItem[]
  indicators: StockIndicatorItem[]
}>()

let chartInstance: echarts.ECharts | null = null

// 初始化图表
const initChart = async () => {
  await nextTick()

  const chartDom = document.getElementById('stock-price-chart')

  if (!chartDom) {
    return
  }

  chartInstance = echarts.init(chartDom)

  updateChart()
}

// 更新图表
const updateChart = () => {
  if (!chartInstance) {
    return
  }

  // 优先使用技术指标接口数据
  // 因为 indicators 里面同时有 close、ma5、ma10、ma20
  const chartData = props.indicators

  if (!chartData.length) {
    chartInstance.clear()
    return
  }

  const tradeDates = chartData.map((item) => item.trade_date)
  const closeList = chartData.map((item) => item.close)
  const ma5List = chartData.map((item) => item.ma5)
  const ma10List = chartData.map((item) => item.ma10)
  const ma20List = chartData.map((item) => item.ma20)
  const volumeList = chartData.map((item) => item.volume)

  // clear 可以避免 ECharts 继续保留旧的单线配置
  chartInstance.clear()

  chartInstance.setOption(
    {
      tooltip: {
        trigger: 'axis',
      },
      legend: {
        top: 0,
        data: ['收盘价', 'MA5', 'MA10', 'MA20', '成交量'],
      },
      grid: {
        top: 48,
        left: 56,
        right: 56,
        bottom: 40,
      },
      xAxis: {
        type: 'category',
        data: tradeDates,
      },
      yAxis: [
        {
          type: 'value',
          scale: true,
          name: '价格',
        },
        {
          type: 'value',
          name: '成交量',
        },
      ],
      series: [
        {
          name: '收盘价',
          type: 'line',
          data: closeList,
          smooth: true,
          showSymbol: false,
        },
        {
          name: 'MA5',
          type: 'line',
          data: ma5List,
          smooth: true,
          showSymbol: false,
        },
        {
          name: 'MA10',
          type: 'line',
          data: ma10List,
          smooth: true,
          showSymbol: false,
        },
        {
          name: 'MA20',
          type: 'line',
          data: ma20List,
          smooth: true,
          showSymbol: false,
        },
        {
          name: '成交量',
          type: 'bar',
          yAxisIndex: 1,
          data: volumeList,
        },
      ],
    },
    true,
  )
}

// 页面尺寸变化时，重新适配图表大小
const resizeChart = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

// 监听技术指标数据变化
// 点击不同股票后，indicators 会变化，图表要重新渲染
watch(
  () => props.indicators,
  () => {
    updateChart()
  },
  {
    deep: true,
  },
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})
</script>

<template>
  <div class="chart-wrapper">
    <div id="stock-price-chart" class="stock-price-chart"></div>
  </div>
</template>

<style scoped lang="scss">
.chart-wrapper {
  width: 100%;
  margin-top: 16px;
}

.stock-price-chart {
  width: 100%;
  height: 360px;
}
</style>
