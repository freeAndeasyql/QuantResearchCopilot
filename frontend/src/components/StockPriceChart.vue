<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { StockIndicatorItem, StockPriceItem } from '@/api/stocks'

const props = defineProps<{
  prices: StockPriceItem[]
  indicators: StockIndicatorItem[]
}>()

let chartInstance: echarts.ECharts | null = null

// 格式化成交量
// 例如 125000 显示为 12.5万
const formatVolume = (value: number) => {
  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(1)}亿`
  }

  if (value >= 10000) {
    return `${(value / 10000).toFixed(1)}万`
  }

  return String(value)
}

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

// 更新走势图
const updateChart = () => {
  if (!chartInstance) {
    return
  }

  // indicators 中同时包含价格、均线和成交量
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

  // 清除上一只股票残留的图表配置
  chartInstance.clear()

  chartInstance.setOption(
    {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
        },
      },

      // 让上下两个图表的十字指示线联动
      axisPointer: {
        link: [
          {
            xAxisIndex: [0, 1],
          },
        ],
      },

      legend: {
        top: 0,
        data: ['收盘价', 'MA5', 'MA10', 'MA20', '成交量'],
      },

      // 上面是价格走势图，下面是成交量
      grid: [
        {
          top: 50,
          left: 60,
          right: 30,
          height: '56%',
        },
        {
          top: '74%',
          left: 60,
          right: 30,
          height: '15%',
        },
      ],

      // 上下两个图表分别使用一个 X 轴
      xAxis: [
        {
          type: 'category',
          gridIndex: 0,
          data: tradeDates,
          boundaryGap: false,
          axisLabel: {
            show: false,
          },
        },
        {
          type: 'category',
          gridIndex: 1,
          data: tradeDates,
          boundaryGap: true,
        },
      ],

      // 上面显示价格，下面显示成交量
      yAxis: [
        {
          type: 'value',
          gridIndex: 0,
          scale: true,
          name: '价格',
        },
        {
          type: 'value',
          gridIndex: 1,
          name: '成交量',
          axisLabel: {
            formatter: (value: number) => formatVolume(value),
          },
        },
      ],

      // 支持鼠标滚轮缩放和底部拖动选择时间范围
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: 0,
          end: 100,
        },
        {
          type: 'slider',
          xAxisIndex: [0, 1],
          bottom: 4,
          start: 0,
          end: 100,
        },
      ],

      series: [
        {
          name: '收盘价',
          type: 'line',
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: closeList,
          smooth: true,
          showSymbol: false,
        },
        {
          name: 'MA5',
          type: 'line',
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: ma5List,
          smooth: true,
          showSymbol: false,
        },
        {
          name: 'MA10',
          type: 'line',
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: ma10List,
          smooth: true,
          showSymbol: false,
        },
        {
          name: 'MA20',
          type: 'line',
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: ma20List,
          smooth: true,
          showSymbol: false,
        },
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumeList,
        },
      ],
    },
    true,
  )
}

// 浏览器窗口变化时，让图表自动适配
const resizeChart = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

// 点击不同股票后，重新绘制图表
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
  height: 520px;
}
</style>
