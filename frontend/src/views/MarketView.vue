<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import StockPriceChart from '../components/StockPriceChart.vue'

import {
  getIndustries,
  getStockDetail,
  getStockPrices,
  getStocks,
  type StockItem,
  type StockPriceItem,
} from '../api/stocks'

const stocks = ref<StockItem[]>([])
const industries = ref<string[]>([])
const selectedStock = ref<StockItem | null>(null)

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

// 获取单只股票详情和历史价格
// 点击表格行时调用
const selectStock = async (code: string) => {
  detailLoading.value = true
  detailError.value = ''
  stockPrices.value = []

  try {
    // 同时请求详情和价格。
    const [detailRes, pricesRes] = await Promise.all([getStockDetail(code), getStockPrices(code)])

    selectedStock.value = detailRes.data.data
    stockPrices.value = pricesRes.data.data
  } catch (err) {
    detailError.value = err instanceof Error ? err.message : '获取股票详情失败'
  } finally {
    detailLoading.value = false
  }
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
    <div v-if="stockPrices.length" class="price-chart-section">
      <h3>价格走势</h3>
      <StockPriceChart :prices="stockPrices" />
    </div>

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
}
</style>
