import axios from 'axios'

export const request = axios.create({
  baseURL: 'http://127.0.0.1:8001',
  timeout: 10000,
})

// 响应拦截器
// 后端错误时，优先取后端返回的 message
request.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const message = error.response?.data?.message || error.message || '请求失败'
    return Promise.reject(new Error(message))
  },
)
