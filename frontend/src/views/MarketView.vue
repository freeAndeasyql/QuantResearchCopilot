<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import StockPriceChart from '../components/StockPriceChart.vue'

import {
  getIndustries,
  getStockDetail,
  getStockPrices,
  getStocks,
  getStockMetrics,
  getStockIndicators,
  getStockIndicatorSummary,
  getStockVolumeSummary,
  getStockAnalysisSummary,
  type StockAnalysisSummary,
  type StockVolumeSummary,
  type StockIndicatorSummary,
  type StockIndicatorItem,
  type StockItem,
  type StockPriceItem,
  type StockMetrics,
} from '../api/stocks'

const stocks = ref<StockItem[]>([])
const industries = ref<string[]>([])
// 选取股票
const selectedStock = ref<StockItem | null>(null)

// 选取股票涨跌幅
const stockMetrics = ref<StockMetrics | null>(null)

const keyword = ref('')
const selectedIndustry = ref('')
const currentPage = ref(1)
const total = ref(0)

const pageSize = 5

const loading = ref(false)
const detailLoading = ref(false)
const error = ref('')
const detailError = ref('')

const totalPages = computed(() => {
  return Math.max(1, Math.ceil(total.value / pageSize))
})

const hasFilter = computed(() => {
  return Boolean(keyword.value || selectedIndustry.value)
})

// 价格状态
const stockPrices = ref<StockPriceItem[]>([])

// 股票技术指标数据：收盘价、MA5、MA10、MA20
const stockIndicators = ref<StockIndicatorItem[]>([])

// 技术指标解读数据
const indicatorSummary = ref<StockIndicatorSummary | null>(null)

// 当前股票的成交量解读
const volumeSummary = ref<StockVolumeSummary | null>(null)

// 当前股票的综合分析结果
const analysisSummary = ref<StockAnalysisSummary | null>(null)

// 增加防抖
let searchTimer: number | undefined

// 获取股票列表
// 现在搜索、行业筛选、分页都交给后端处理
const fetchStocks = async () => {
  loading.value = true
  error.value = ''

  try {
    const res = await getStocks({
      keyword: keyword.value,
      industry: selectedIndustry.value,
      page: currentPage.value,
      page_size: pageSize,
    })

    stocks.value = res.data.data.list
    total.value = res.data.data.total
    selectedStock.value = null
  } catch (err) {
    error.value = err instanceof Error ? err.message : '获取股票列表失败'
  } finally {
    loading.value = false
  }
}

// 获取行业列表
// 行业下拉框的数据来自后端 /api/industries
const fetchIndustries = async () => {
  try {
    const res = await getIndustries()
    industries.value = res.data.data
  } catch (err) {
    error.value = err instanceof Error ? err.message : '获取行业列表失败'
  }
}

// 格式化成交量，避免直接展示很长的数字
const formatVolume = (value: number | null) => {
  if (value === null) {
    return '暂无'
  }

  if (value >= 100000000) {
    return `${(value / 100000000).toFixed(2)} 亿`
  }

  if (value >= 10000) {
    return `${(value / 10000).toFixed(2)} 万`
  }

  return String(value)
}

// 格式化涨跌幅
const formatPercentage = (value: number | null) => {
  if (value === null) {
    return '暂无'
  }

  const prefix = value > 0 ? '+' : ''

  return `${prefix}${value.toFixed(2)}%`
}

// 根据综合分数返回带正负号的显示文本
const formatAnalysisScore = (score: number) => {
  return score > 0 ? `+${score}` : String(score)
}

// 根据评分返回对应的样式名称
const getScoreClass = (score: number) => {
  if (score > 0) {
    return 'is-positive'
  }

  if (score < 0) {
    return 'is-negative'
  }

  return 'is-neutral'
}

// 区间收益的 value 是数字，展示时补充百分号
const formatScoreDetailValue = (detail: { dimension: string; value: string | number | null }) => {
  if (detail.value === null || detail.value === '') {
    return '暂无'
  }

  if (detail.dimension === '区间收益' && typeof detail.value === 'number') {
    const prefix = detail.value > 0 ? '+' : ''

    return `${prefix}${detail.value.toFixed(2)}%`
  }

  return String(detail.value)
}

// 点击表格行时调用
// 获取单只股票详情、历史价格、收益指标、技术指标和技术指标解读

const selectStock = async (code: string) => {
  detailLoading.value = true
  detailError.value = ''

  // 清空上一只股票的数据，避免切换股票时展示旧内容
  stockPrices.value = []
  stockMetrics.value = null
  stockIndicators.value = []
  indicatorSummary.value = null
  volumeSummary.value = null
  analysisSummary.value = null

  try {
    // 同时请求股票详情和各项分析数据
    const [
      detailRes,
      pricesRes,
      metricsRes,
      indicatorsRes,
      indicatorSummaryRes,
      volumeSummaryRes,
      analysisSummaryRes,
    ] = await Promise.all([
      getStockDetail(code),
      getStockPrices(code),
      getStockMetrics(code),
      getStockIndicators(code),
      getStockIndicatorSummary(code),
      getStockVolumeSummary(code),
      getStockAnalysisSummary(code),
    ])

    selectedStock.value = detailRes.data.data
    stockPrices.value = pricesRes.data.data
    stockMetrics.value = metricsRes.data.data
    stockIndicators.value = indicatorsRes.data.data
    indicatorSummary.value = indicatorSummaryRes.data.data
    volumeSummary.value = volumeSummaryRes.data.data
    analysisSummary.value = analysisSummaryRes.data.data
  } catch (err) {
    detailError.value = err instanceof Error ? err.message : '获取股票详情失败'
  } finally {
    detailLoading.value = false
  }
}

// 格式化普通数字
// 例如 1.2 -> 1.20
const formatNumber = (value: number) => {
  return value.toFixed(2)
}

// 格式化涨跌数字
// 正数前面加 +，负数保留 -，0 不加符号
const formatChange = (value: number) => {
  const formattedValue = value.toFixed(2)

  if (value > 0) {
    return `+${formattedValue}`
  }

  return formattedValue
}

// 根据涨跌值返回样式类名
// A 股习惯：上涨红色，下跌绿色
const getChangeClass = (value: number) => {
  if (value > 0) {
    return 'is-up'
  }

  if (value < 0) {
    return 'is-down'
  }

  return 'is-flat'
}

// 清空搜索和行业筛选
const clearFilter = () => {
  keyword.value = ''
  selectedIndustry.value = ''
}

// 上一页
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value -= 1
  }
}

// 下一页
const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value += 1
  }
}

// 搜索词或行业变化时，回到第一页并重新请求后端
const resetPageAndFetch = () => {
  if (currentPage.value === 1) {
    fetchStocks()
    return
  }

  currentPage.value = 1
}

// 监听搜索和行业变化
// 输入搜索词时做 300ms 防抖，避免每输入一个字就请求后端
watch([keyword, selectedIndustry], () => {
  window.clearTimeout(searchTimer)

  searchTimer = window.setTimeout(() => {
    resetPageAndFetch()
  }, 300)
})

// 监听页码变化
watch(currentPage, () => {
  fetchStocks()
})

onMounted(() => {
  fetchIndustries()
  fetchStocks()
})
</script>

<template>
  <div class="market-page">
    <h1>股票行情</h1>

    <div class="toolbar">
      <input v-model="keyword" class="search-input" placeholder="搜索股票代码、名称或行业" />

      <select v-model="selectedIndustry" class="industry-select">
        <option value="">全部行业</option>
        <option v-for="industry in industries" :key="industry" :value="industry">
          {{ industry }}
        </option>
      </select>

      <button v-if="hasFilter" class="clear-button" @click="clearFilter">清空筛选</button>
    </div>

    <p class="summary">
      当前显示 {{ stocks.length }} / {{ total }} 只股票
      <span v-if="loading">，正在更新...</span>
    </p>

    <p v-if="loading">加载中...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <table v-if="!loading && stocks.length" class="stock-table">
      <thead>
        <tr>
          <th>股票代码</th>
          <th>股票名称</th>
          <th>行业</th>
          <th>最新价</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="stock in stocks" :key="stock.code" @click="selectStock(stock.code)">
          <td>{{ stock.code }}</td>
          <td>{{ stock.name }}</td>
          <td>{{ stock.industry }}</td>
          <td>{{ stock.latest_price }}</td>
        </tr>
      </tbody>
    </table>

    <div v-if="!loading && total > 0" class="pagination">
      <button :disabled="currentPage === 1" @click="prevPage">上一页</button>

      <span>第 {{ currentPage }} / {{ totalPages }} 页</span>

      <button :disabled="currentPage === totalPages" @click="nextPage">下一页</button>
    </div>

    <p v-if="!loading && !stocks.length" class="empty">暂无匹配股票</p>

    <div class="detail-card">
      <h2>股票详情</h2>

      <p v-if="detailLoading">详情加载中...</p>
      <p v-if="detailError" class="error">{{ detailError }}</p>

      <div v-if="selectedStock && !detailLoading" class="detail-content">
        <p>股票代码：{{ selectedStock.code }}</p>
        <p>股票名称：{{ selectedStock.name }}</p>
        <p>所属行业：{{ selectedStock.industry }}</p>
        <p>最新价格：{{ selectedStock.latest_price }}</p>
      </div>

      <p v-if="!selectedStock && !detailLoading" class="empty">点击表格中的股票查看详情</p>
    </div>

    <!-- 股票收益指标 -->
    <div v-if="stockMetrics" class="metrics-grid">
      <div class="metric-item">
        <span>最新交易日</span>
        <strong>{{ stockMetrics.latest_trade_date }}</strong>
      </div>

      <div class="metric-item">
        <span>最新收盘价</span>
        <strong>{{ formatNumber(stockMetrics.latest_close) }}</strong>
      </div>

      <div class="metric-item">
        <span>涨跌额</span>
        <strong :class="getChangeClass(stockMetrics.change_amount)">
          {{ formatChange(stockMetrics.change_amount) }}
        </strong>
      </div>

      <div class="metric-item">
        <span>涨跌幅</span>
        <strong :class="getChangeClass(stockMetrics.change_pct)">
          {{ formatChange(stockMetrics.change_pct) }}%
        </strong>
      </div>

      <div class="metric-item">
        <span>{{ stockMetrics.period_days }} 日收益率</span>
        <strong :class="getChangeClass(stockMetrics.period_return)">
          {{ formatChange(stockMetrics.period_return) }}%
        </strong>
      </div>
    </div>
    <!-- 股票综合分析 -->
    <div v-if="analysisSummary" class="analysis-summary-card">
      <div class="analysis-summary-header">
        <div>
          <h3>股票综合分析</h3>

          <p>
            {{ analysisSummary.stock_name }}
            ·
            {{ analysisSummary.stock_code }}
            ·
            {{ analysisSummary.industry }}
          </p>
        </div>

        <div class="analysis-overview">
          <span class="analysis-view-tag">
            {{ analysisSummary.overall_view }}
          </span>

          <strong :class="getScoreClass(analysisSummary.score)">
            {{ formatAnalysisScore(analysisSummary.score) }} 分
          </strong>
        </div>
      </div>

      <p class="analysis-date">分析日期：{{ analysisSummary.trade_date || '暂无' }}</p>

      <p class="analysis-summary-text">
        {{ analysisSummary.summary }}
      </p>

      <div class="analysis-score-section">
        <h4>评分依据</h4>

        <div class="analysis-score-grid">
          <div
            v-for="detail in analysisSummary.score_details"
            :key="detail.dimension"
            class="analysis-score-item"
          >
            <span>{{ detail.dimension }}</span>

            <strong>
              {{ formatScoreDetailValue(detail) }}
            </strong>

            <em :class="getScoreClass(detail.score)">
              {{ formatAnalysisScore(detail.score) }} 分
            </em>
          </div>
        </div>
      </div>

      <div class="analysis-message-grid">
        <div class="analysis-message-box highlight-box">
          <h4>积极信号</h4>

          <ul>
            <li v-for="highlight in analysisSummary.highlights" :key="highlight">
              {{ highlight }}
            </li>
          </ul>
        </div>

        <div class="analysis-message-box risk-box">
          <h4>风险提示</h4>

          <ul>
            <li v-for="risk in analysisSummary.risks" :key="risk">
              {{ risk }}
            </li>
          </ul>
        </div>
      </div>

      <p class="analysis-disclaimer">
        {{ analysisSummary.disclaimer }}
      </p>
    </div>

    <!-- 技术指标解读 -->
    <div v-if="indicatorSummary" class="indicator-summary-card">
      <div class="indicator-summary-header">
        <h3>技术指标解读</h3>
        <span class="trend-tag">{{ indicatorSummary.trend }}</span>
      </div>

      <p class="summary-text">
        {{ indicatorSummary.summary }}
      </p>

      <div class="indicator-values">
        <div class="indicator-value-item">
          <span>交易日</span>
          <strong>{{ indicatorSummary.trade_date }}</strong>
        </div>

        <div class="indicator-value-item">
          <span>收盘价</span>
          <strong>{{ indicatorSummary.close ?? '暂无' }}</strong>
        </div>

        <div class="indicator-value-item">
          <span>MA5</span>
          <strong>{{ indicatorSummary.ma5 ?? '暂无' }}</strong>
        </div>

        <div class="indicator-value-item">
          <span>MA10</span>
          <strong>{{ indicatorSummary.ma10 ?? '暂无' }}</strong>
        </div>

        <div class="indicator-value-item">
          <span>MA20</span>
          <strong>{{ indicatorSummary.ma20 ?? '暂无' }}</strong>
        </div>
      </div>

      <div class="signal-list">
        <h4>关键信号</h4>

        <ul>
          <li v-for="signal in indicatorSummary.signals" :key="signal">
            {{ signal }}
          </li>
        </ul>
      </div>

      <p class="risk-tip">说明：该解读仅基于均线关系生成，用于学习和辅助观察，不构成投资建议。</p>
    </div>
    <!-- 成交量解读 -->
    <div v-if="volumeSummary" class="volume-summary-card">
      <div class="volume-summary-header">
        <div>
          <h3>成交量解读</h3>
          <p>{{ volumeSummary.trade_date }}</p>
        </div>

        <span
          class="volume-signal-tag"
          :class="{
            'is-up': volumeSummary.price_status === '上涨',
            'is-down': volumeSummary.price_status === '下跌',
            'is-flat': volumeSummary.price_status === '平盘',
          }"
        >
          {{ volumeSummary.signal }}
        </span>
      </div>

      <p class="volume-summary-text">
        {{ volumeSummary.summary }}
      </p>

      <div class="volume-summary-values">
        <div class="volume-value-item">
          <span>价格状态</span>
          <strong>{{ volumeSummary.price_status }}</strong>
        </div>

        <div class="volume-value-item">
          <span>成交量状态</span>
          <strong>{{ volumeSummary.volume_status }}</strong>
        </div>

        <div class="volume-value-item">
          <span>当日涨跌幅</span>
          <strong
            :class="{
              'value-up': (volumeSummary.change_pct ?? 0) > 0,
              'value-down': (volumeSummary.change_pct ?? 0) < 0,
            }"
          >
            {{ formatPercentage(volumeSummary.change_pct) }}
          </strong>
        </div>

        <div class="volume-value-item">
          <span>最新成交量</span>
          <strong>{{ formatVolume(volumeSummary.latest_volume) }}</strong>
        </div>

        <div class="volume-value-item">
          <span>前 5 日平均成交量</span>
          <strong>{{ formatVolume(volumeSummary.average_volume_5d) }}</strong>
        </div>

        <div class="volume-value-item">
          <span>量比</span>
          <strong>
            {{
              volumeSummary.volume_ratio === null
                ? '暂无'
                : `${volumeSummary.volume_ratio.toFixed(2)} 倍`
            }}
          </strong>
        </div>
      </div>

      <div class="volume-knowledge">
        <strong>如何理解：</strong>
        <span>
          量比表示最新成交量相当于前 5 个交易日平均成交量的多少倍。 大于 1.2 倍视为放量，小于 0.8
          倍视为缩量。
        </span>
      </div>

      <p class="risk-tip">
        说明：该结果只根据最近价格和成交量变化生成，用于学习和辅助观察，不构成投资建议。
      </p>
    </div>
    <!-- 价格走势 -->
    <div v-if="stockPrices.length" class="price-chart-section">
      <h3>价格走势</h3>
      <StockPriceChart :prices="stockPrices" :indicators="stockIndicators" />
    </div>

    <!-- 暂无数据 -->
    <p v-if="selectedStock && !stockPrices.length && !detailLoading" class="empty">
      暂无历史价格数据
    </p>
  </div>
</template>

<style scoped lang="scss">
.market-page {
  padding: 24px;

  .toolbar {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin: 16px 0;
  }

  .search-input,
  .industry-select {
    height: 36px;
    padding: 0 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    outline: none;

    &:focus {
      border-color: #2563eb;
    }
  }

  .search-input {
    width: 320px;
    max-width: 100%;
  }

  .industry-select {
    width: 140px;
  }

  .clear-button {
    height: 36px;
    padding: 0 14px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background: #fff;
    cursor: pointer;

    &:hover {
      background: #f9fafb;
    }
  }

  .summary {
    color: #4b5563;
  }

  .error {
    color: #dc2626;
  }

  .empty {
    color: #6b7280;
  }

  .stock-table {
    width: 100%;
    margin-top: 16px;
    border-collapse: collapse;

    th,
    td {
      padding: 12px;
      border: 1px solid #e5e7eb;
      text-align: left;
    }

    th {
      background: #f8fafc;
      font-weight: 700;
    }

    tr {
      cursor: pointer;

      &:hover {
        background: #f9fafb;
      }
    }
  }

  .pagination {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 16px;

    button {
      height: 32px;
      padding: 0 12px;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      background: #fff;
      cursor: pointer;

      &:disabled {
        color: #9ca3af;
        cursor: not-allowed;
        background: #f3f4f6;
      }
    }
  }

  .detail-card {
    margin-top: 24px;
    padding: 16px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background: #ffffff;

    h2 {
      margin: 0 0 12px;
      font-size: 18px;
    }

    .detail-content {
      display: grid;
      gap: 8px;
    }

    p {
      margin: 0;
    }
  }

  .price-chart-section {
    margin-top: 16px;

    h3 {
      margin: 0 0 8px;
      font-size: 16px;
    }
  }

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(5, minmax(120px, 1fr));
    gap: 12px;
    margin-top: 16px;

    .metric-item {
      padding: 12px;
      border: 1px solid #e5e7eb;
      border-radius: 6px;
      background: #f8fafc;

      span {
        display: block;
        margin-bottom: 6px;
        color: #6b7280;
        font-size: 13px;
      }

      strong {
        color: #111827;
        font-size: 16px;
      }
      .is-up {
        color: #dc2626;
      }

      .is-down {
        color: #16a34a;
      }

      .is-flat {
        color: #6b7280;
      }
    }
  }
}

.indicator-summary-card {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #f8fafc;
}

.indicator-summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;

  h3 {
    margin: 0;
    font-size: 18px;
  }
}

.trend-tag {
  padding: 4px 12px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 14px;
  font-weight: 600;
}

.summary-text {
  margin: 12px 0;
  color: #374151;
  line-height: 1.7;
}

.indicator-values {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.indicator-value-item {
  padding: 12px;
  border-radius: 8px;
  background: #ffffff;

  span {
    display: block;
    margin-bottom: 6px;
    color: #6b7280;
    font-size: 13px;
  }

  strong {
    color: #111827;
    font-size: 16px;
  }
}

.signal-list {
  margin-top: 16px;

  h4 {
    margin: 0 0 8px;
  }

  ul {
    margin: 0;
    padding-left: 20px;
  }

  li {
    margin-bottom: 6px;
    color: #374151;
    line-height: 1.6;
  }
}

.risk-tip {
  margin: 12px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.volume-summary-card {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #f8fafc;
}

.volume-summary-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;

  h3 {
    margin: 0;
    font-size: 18px;
  }

  p {
    margin: 6px 0 0;
    color: #6b7280;
    font-size: 13px;
  }
}

.volume-signal-tag {
  padding: 4px 12px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 600;

  &.is-up {
    color: #b91c1c;
    background: #fee2e2;
  }

  &.is-down {
    color: #15803d;
    background: #dcfce7;
  }

  &.is-flat {
    color: #4b5563;
    background: #e5e7eb;
  }
}

.volume-summary-text {
  margin: 14px 0;
  color: #374151;
  line-height: 1.7;
}

.volume-summary-values {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.volume-value-item {
  padding: 12px;
  border-radius: 8px;
  background: #ffffff;

  span {
    display: block;
    margin-bottom: 6px;
    color: #6b7280;
    font-size: 13px;
  }

  strong {
    color: #111827;
    font-size: 16px;
  }

  .value-up {
    color: #dc2626;
  }

  .value-down {
    color: #16a34a;
  }
}

.volume-knowledge {
  margin-top: 16px;
  padding: 12px;
  border-radius: 8px;
  background: #eff6ff;
  color: #374151;
  font-size: 14px;
  line-height: 1.7;

  strong {
    color: #1d4ed8;
  }
}

@media (max-width: 900px) {
  .volume-summary-values {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 900px) {
  .indicator-values {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.analysis-summary-card {
  margin-top: 16px;
  padding: 20px;
  border: 1px solid #dbeafe;
  border-radius: 14px;
  background: #f8fafc;
}

.analysis-summary-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;

  h3 {
    margin: 0;
    font-size: 20px;
  }

  p {
    margin: 6px 0 0;
    color: #6b7280;
    font-size: 14px;
  }
}

.analysis-overview {
  display: flex;
  align-items: center;
  gap: 10px;

  strong {
    font-size: 18px;
  }
}

.analysis-view-tag {
  padding: 5px 14px;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 14px;
  font-weight: 600;
}

.analysis-date {
  margin: 14px 0 0;
  color: #6b7280;
  font-size: 13px;
}

.analysis-summary-text {
  margin: 12px 0 0;
  color: #374151;
  line-height: 1.8;
}

.analysis-score-section {
  margin-top: 20px;

  h4 {
    margin: 0 0 10px;
  }
}

.analysis-score-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.analysis-score-item {
  padding: 14px;
  border-radius: 10px;
  background: #ffffff;

  span,
  strong,
  em {
    display: block;
  }

  span {
    color: #6b7280;
    font-size: 13px;
  }

  strong {
    margin-top: 8px;
    color: #111827;
    font-size: 16px;
  }

  em {
    margin-top: 6px;
    font-size: 13px;
    font-style: normal;
    font-weight: 600;
  }
}

.analysis-message-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 18px;
}

.analysis-message-box {
  padding: 14px;
  border-radius: 10px;

  h4 {
    margin: 0 0 10px;
  }

  ul {
    margin: 0;
    padding-left: 20px;
  }

  li {
    margin-bottom: 8px;
    color: #374151;
    line-height: 1.7;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

.highlight-box {
  background: #f0fdf4;
}

.risk-box {
  background: #fff7ed;
}

.analysis-disclaimer {
  margin: 16px 0 0;
  padding-top: 14px;
  border-top: 1px solid #e5e7eb;
  color: #6b7280;
  font-size: 13px;
  line-height: 1.6;
}

.is-positive {
  color: #dc2626;
}

.is-negative {
  color: #16a34a;
}

.is-neutral {
  color: #4b5563;
}

@media (max-width: 900px) {
  .analysis-summary-header {
    flex-direction: column;
  }

  .analysis-score-grid {
    grid-template-columns: 1fr;
  }

  .analysis-message-grid {
    grid-template-columns: 1fr;
  }
}
</style>
