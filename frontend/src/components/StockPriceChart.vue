<script setup lang="ts">
import * as echarts from 'echarts'
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

interface PriceItem {
  trade_date: string
  close: number
}

const props = defineProps<{
  prices: PriceItem[]
}>()

// 指向图表容器
const chartRef = ref<HTMLDivElement | null>(null)

let chartInstance: echarts.ECharts | null = null

// 初始化图表
const initChart = () => {
  if (!chartRef.value) {
    return
  }

  chartInstance = echarts.init(chartRef.value)
}

// 根据价格数据画折线图
const renderChart = () => {
  if (!chartInstance) {
    return
  }

  if (!props.prices.length) {
    chartInstance.clear()
    return
  }

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: props.prices.map((item) => item.trade_date),
    },
    yAxis: {
      type: 'value',
      scale: true,
    },
    series: [
      {
        name: '收盘价',
        type: 'line',
        smooth: true,
        data: props.prices.map((item) => item.close),
      },
    ],
  }

  chartInstance.setOption(option)
}

// 浏览器窗口变化时，重新调整图表大小
const resizeChart = () => {
  chartInstance?.resize()
}

// 监听价格数据变化，点击不同股票时图表会更新。
watch(
  () => props.prices,
  () => {
    nextTick(() => {
      renderChart()
    })
  },
  {
    deep: true,
  },
)

onMounted(() => {
  initChart()
  renderChart()
  window.addEventListener('resize', resizeChart)
})

// 销毁图表，避免内存泄漏
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
  chartInstance = null
})
</script>

<template>
  <div ref="chartRef" class="stock-price-chart"></div>
</template>

<style scoped lang="scss">
// 必须有高度，否则图表可能显示不出来。
.stock-price-chart {
  width: 100%;
  height: 280px;
}
</style>
