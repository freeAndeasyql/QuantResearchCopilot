import { request } from './request'

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

export interface StockListResponse {
  data: StockItem[]
  total: number
  page: number
  page_size: number
}

// 获取股票列表
// 支持 keyword、industry、page、page_size 参数
export const getStocks = (params: StockListParams) => {
  return request.get<StockListResponse>('/api/stocks', { params })
}

// 获取单只股票详情
export const getStockDetail = (code: string) => {
  return request.get<{ data: StockItem }>(`/api/stocks/${code}`)
}

// 获取行业列表
// 用于股票行情页的行业下拉框
export const getIndustries = () => {
  return request.get<{ data: string[] }>('/api/industries')
}