<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { getStocks, type StockItem } from '../api/stocks'

const stocks = ref<StockItem[]>([])
const keyword = ref('')
const loading = ref(false)
const error = ref('')

const filteredStocks = computed(() => {
  const value = keyword.value.trim().toLowerCase()

  if (!value) {
    return stocks.value
  }

  return stocks.value.filter((stock) => {
    return (
      stock.code.toLowerCase().includes(value) ||
      stock.name.toLowerCase().includes(value) ||
      stock.industry.toLowerCase().includes(value)
    )
  })
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

onMounted(() => {
  fetchStocks()
})
</script>

<template>
  <div class="market-page">
    <h1>股票行情</h1>

    <div class="toolbar">
      <input
        v-model="keyword"
        class="search-input"
        placeholder="搜索股票代码、名称或行业"
      />
    </div>

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

    <p v-if="!loading && !filteredStocks.length" class="empty">
      暂无匹配股票
    </p>
  </div>
</template>

<style scoped lang="scss">
.market-page {
  padding: 24px;

  .toolbar {
    margin: 16px 0;
  }

  .search-input {
    width: 320px;
    max-width: 100%;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    outline: none;

    &:focus {
      border-color: #2563eb;
    }
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