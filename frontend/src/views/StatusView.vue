<script setup lang="ts">
import { ref } from 'vue'
import { getHealth } from '../api/health'
import { getDataStatus, type DataStatus } from '../api/stocks'

const status = ref('未检查')
const loading = ref(false)
const error = ref('')

const dataStatus = ref<DataStatus | null>(null)
const dataStatusLoading = ref(false)
const dataStatusError = ref('')
const checkHealth = async () => {
  loading.value = true
  error.value = ''

  try {
    const res = await getHealth()
    status.value = res.data.data.status
  } catch (err) {
    error.value = '请求后端失败'
  } finally {
    loading.value = false
  }
}

// 获取行情数据状态
const checkDataStatus = async () => {
  dataStatusLoading.value = true
  dataStatusError.value = ''

  try {
    const res = await getDataStatus()
    dataStatus.value = res.data.data
  } catch (err) {
    dataStatusError.value = err instanceof Error ? err.message : '获取数据状态失败'
  } finally {
    dataStatusLoading.value = false
  }
}
</script>

<template>
  <div class="status-page">
    <h1>项目状态</h1>

    <button @click="checkHealth">检查后端状态</button>

    <p v-if="loading">请求中...</p>
    <p v-else>后端状态：{{ status }}</p>
    <p v-if="error">{{ error }}</p>

    <div class="status-card">
      <h2>行情数据状态</h2>

      <button @click="checkDataStatus">检查数据状态</button>

      <p v-if="dataStatusLoading">检查中...</p>
      <p v-if="dataStatusError" class="error">{{ dataStatusError }}</p>

      <div v-if="dataStatus" class="status-list">
        <p>数据来源：{{ dataStatus.source }}</p>
        <p>文件状态：{{ dataStatus.exists ? '已存在' : '不存在' }}</p>
        <p>最新交易日：{{ dataStatus.latest_trade_date || '暂无' }}</p>
        <p>数据行数：{{ dataStatus.row_count }}</p>
        <p>股票数量：{{ dataStatus.stock_count }}</p>
      </div>
    </div>
  </div>
</template>
