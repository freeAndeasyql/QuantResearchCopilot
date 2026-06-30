<script setup lang="ts">
import { ref } from 'vue'
import { getHealth } from './api/health'

const status = ref('未检查')
const loading = ref(false)
const error = ref('')

const checkHealth = async () => {
  loading.value = true
  error.value = ''

  try {
    const res = await getHealth()
    status.value = res.data.status
  } catch (err) {
    error.value = '请求后端失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="app">
   <h1>Quant Research Copilot</h1>

    <button @click="checkHealth">
      检查后端状态
    </button>

    <p v-if="loading">请求中...</p>
    <p v-else>后端状态：{{ status }}</p>
    <p v-if="error">{{ error }}</p>

  </div>
</template>

<style scoped>

</style>