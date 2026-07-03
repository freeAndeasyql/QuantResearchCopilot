<script setup lang="ts">
import { ref } from 'vue'
import { getHealth } from '../api/health'
import { getDataStatus, getDataQuality, type DataStatus, type DataQuality } from '../api/stocks'

const status = ref('未检查')
const loading = ref(false)
const error = ref('')

const dataStatus = ref<DataStatus | null>(null)
const dataStatusLoading = ref(false)
const dataStatusError = ref('')

//数据质量检查
const dataQuality = ref<DataQuality | null>(null)
const dataQualityLoading = ref(false)
const dataQualityError = ref('')
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

// 获取行情数据质量报告
const checkDataQuality = async () => {
  dataQualityLoading.value = true
  dataQualityError.value = ''

  try {
    const res = await getDataQuality()
    dataQuality.value = res.data.data
  } catch (err) {
    dataQualityError.value = err instanceof Error ? err.message : '获取数据质量报告失败'
  } finally {
    dataQualityLoading.value = false
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

    <div class="status-card">
      <h2>数据质量报告</h2>

      <button @click="checkDataQuality">检查数据质量</button>

      <p v-if="dataQualityLoading">检查中...</p>
      <p v-if="dataQualityError" class="error">{{ dataQualityError }}</p>

      <div v-if="dataQuality" class="status-list">
        <p>是否有数据：{{ dataQuality.has_data ? '是' : '否' }}</p>
        <p>总行数：{{ dataQuality.row_count }}</p>
        <p>缺失值数量：{{ dataQuality.missing_value_count }}</p>
        <p>重复行数量：{{ dataQuality.duplicate_row_count }}</p>
        <p>收盘价缺失数量：{{ dataQuality.missing_close_count }}</p>

        <h3>每只股票记录数</h3>

        <table class="quality-table">
          <thead>
            <tr>
              <th>股票代码</th>
              <th>记录数</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="item in dataQuality.stock_record_counts" :key="item.stock_code">
              <td>{{ item.stock_code }}</td>
              <td>{{ item.record_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.quality-table {
  width: 100%;
  margin-top: 12px;
  border-collapse: collapse;

  th,
  td {
    padding: 8px;
    border: 1px solid #e5e7eb;
    text-align: left;
  }

  th {
    background: #f8fafc;
  }
}
</style>
