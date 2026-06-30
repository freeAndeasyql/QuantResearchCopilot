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
    <nav class="nav">
      <RouterLink to="/">首页</RouterLink>
      <RouterLink to="/market">股票行情</RouterLink>
      <RouterLink to="/status">项目状态</RouterLink>
    </nav>

    <RouterView />
  </div>
   
</template>

<style scoped>
.app {
  min-height: 100vh;
}

.nav {
  display: flex;
  gap: 16px;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.nav a {
  color: #2563eb;
  text-decoration: none;
}

.nav a.router-link-active {
  font-weight: 700;
}
</style>