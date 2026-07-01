import { request } from './request'
import type { ApiResponse } from './stocks'

export interface HealthData {
  status: string
}

// 获取后端健康状态
export const getHealth = () => {
  return request.get<ApiResponse<HealthData>>('/api/health')
}