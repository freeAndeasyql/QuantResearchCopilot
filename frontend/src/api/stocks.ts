import { request } from './request'

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface StockItem {
  code: string
  name: string
  industry: string
  latest_price: number
}

export interface StockListParams {
  keyword?: string
  industry?: string
  page?: number
  page_size?: number
}

export interface StockPageData {
  list: StockItem[]
  total: number
  page: number
  page_size: number
}

// 获取股票列表
// 后端会返回统一结构：{ code, message, data }
export const getStocks = (params: StockListParams) => {
  return request.get<ApiResponse<StockPageData>>('/api/stocks', { params })
}

// 获取单只股票详情
export const getStockDetail = (code: string) => {
  return request.get<ApiResponse<StockItem>>(`/api/stocks/${code}`)
}

// 获取行业列表
export const getIndustries = () => {
  return request.get<ApiResponse<string[]>>('/api/industries')
}