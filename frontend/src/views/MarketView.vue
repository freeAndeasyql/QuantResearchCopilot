<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getStocks, type StockItem } from '../api/stocks'

const stocks = ref<StockItem[]>([])
const loading = ref(false)
const error = ref('')

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
        <tr v-for="stock in stocks" :key="stock.code">
          <td>{{ stock.code }}</td>
          <td>{{ stock.name }}</td>
          <td>{{ stock.industry }}</td>
          <td>{{ stock.latest_price }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped lang="scss">
.market-page {
  padding: 24px;

  .error {
    color: #dc2626;
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