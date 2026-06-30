<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getStocks, type StockItem } from '../api/stocks'

const stocks = ref<StockItem[]>([])
const keyword = ref('')
const selectedIndustry = ref('')
const loading = ref(false)
const error = ref('')

const industries = computed(() => {
  return Array.from(new Set(stocks.value.map((stock) => stock.industry)))
})

const filteredStocks = computed(() => {
  const value = keyword.value.trim().toLowerCase()

  return stocks.value.filter((stock) => {
    const matchKeyword =
      !value ||
      stock.code.toLowerCase().includes(value) ||
      stock.name.toLowerCase().includes(value) ||
      stock.industry.toLowerCase().includes(value)

    const matchIndustry = !selectedIndustry.value || stock.industry === selectedIndustry.value

    return matchKeyword && matchIndustry
  })
})

const hasFilter = computed(() => {
  return Boolean(keyword.value || selectedIndustry.value)
})

const fetchStocks = async () => {
  loading.value = true
  error.value = ''

  try {
    const res = await getStocks()
    stocks.value = res.data.data
  } catch (err) {
    error.value = '获取股票列表失败'
  } finally {
    loading.value = false
  }
}

const clearFilter = () => {
  keyword.value = ''
  selectedIndustry.value = ''
}

onMounted(() => {
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

    <p class="summary">当前显示 {{ filteredStocks.length }} / {{ stocks.length }} 只股票</p>

    <p v-if="loading">加载中...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <table v-if="!loading && filteredStocks.length" class="stock-table">
      <thead>
        <tr>
          <th>股票代码</th>
          <th>股票名称</th>
          <th>行业</th>
          <th>最新价</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="stock in filteredStocks" :key="stock.code">
          <td>{{ stock.code }}</td>
          <td>{{ stock.name }}</td>
          <td>{{ stock.industry }}</td>
          <td>{{ stock.latest_price }}</td>
        </tr>
      </tbody>
    </table>

    <p v-if="!loading && !filteredStocks.length" class="empty">暂无匹配股票</p>
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
  }
}
</style>