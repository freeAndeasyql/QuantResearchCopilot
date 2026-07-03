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

// 根据是否正常返回状态文字
const getQualityStatusText = (isNormal: boolean) => {
  return isNormal ? '正常' : '警告'
}

// 根据是否正常返回状态样式
const getQualityStatusClass = (isNormal: boolean) => {
  return isNormal ? 'is-success' : 'is-warning'
}

// 根据数据是否存在返回整体状态
const getDataStatusText = (hasData: boolean) => {
  return hasData ? '正常' : '异常'
}

// 根据数据是否存在返回整体状态样式
const getDataStatusClass = (hasData: boolean) => {
  return hasData ? 'is-success' : 'is-danger'
}
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

      <div v-if="dataQuality" class="quality-report">
        <div class="quality-conclusion">
          <strong :class="`is-${dataQuality.status}`">
            {{ dataQuality.level }}
          </strong>
          <span>{{ dataQuality.summary }}</span>
        </div>
        <div class="quality-summary">
          <div class="quality-item">
            <span>数据状态</span>
            <strong :class="getDataStatusClass(dataQuality.has_data)">
              {{ getDataStatusText(dataQuality.has_data) }}
            </strong>
          </div>

          <div class="quality-item">
            <span>总行数</span>
            <strong>{{ dataQuality.row_count }}</strong>
          </div>

          <div class="quality-item">
            <span>缺失值</span>
            <strong>{{ dataQuality.missing_value_count }}</strong>
            <em :class="getQualityStatusClass(dataQuality.missing_value_count === 0)">
              {{ getQualityStatusText(dataQuality.missing_value_count === 0) }}
            </em>
          </div>

          <div class="quality-item">
            <span>重复行</span>
            <strong>{{ dataQuality.duplicate_row_count }}</strong>
            <em :class="getQualityStatusClass(dataQuality.duplicate_row_count === 0)">
              {{ getQualityStatusText(dataQuality.duplicate_row_count === 0) }}
            </em>
          </div>

          <div class="quality-item">
            <span>收盘价缺失</span>
            <strong>{{ dataQuality.missing_close_count }}</strong>
            <em :class="getQualityStatusClass(dataQuality.missing_close_count === 0)">
              {{ getQualityStatusText(dataQuality.missing_close_count === 0) }}
            </em>
          </div>
        </div>

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
.quality-report {
  margin-top: 12px;

  h3 {
    margin: 20px 0 12px;
    font-size: 16px;
  }
}

.quality-conclusion {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f8fafc;

  strong {
    padding: 2px 10px;
    border-radius: 999px;
  }

  span {
    color: #374151;
  }
}

.is-normal {
  color: #15803d;
  background: #dcfce7;
}

.is-danger {
  color: #b91c1c;
  background: #fee2e2;
}

.quality-summary {
  display: grid;
  grid-template-columns: repeat(5, minmax(120px, 1fr));
  gap: 12px;
}

.quality-item {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #f8fafc;

  span {
    display: block;
    margin-bottom: 6px;
    color: #6b7280;
    font-size: 13px;
  }

  strong {
    display: block;
    color: #111827;
    font-size: 18px;
  }

  em {
    display: inline-block;
    margin-top: 8px;
    padding: 2px 8px;
    border-radius: 999px;
    font-style: normal;
    font-size: 12px;
  }
}

.is-success {
  color: #15803d;
  background: #dcfce7;
}

.is-warning {
  color: #b45309;
  background: #fef3c7;
}

.is-danger {
  color: #b91c1c;
  background: #fee2e2;
}

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
