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

export interface StockPriceItem {
  trade_date: string
  close: number
}

// 获取单只股票历史价格
export const getStockPrices = (code: string) => {
  return request.get<ApiResponse<StockPriceItem[]>>(`/api/stocks/${code}/prices`)
}

export interface StockMetrics {
  stock_code: string
  latest_trade_date: string
  latest_close: number
  previous_close: number
  change_amount: number
  change_pct: number
  period_days: number
  period_return: number
}

// 获取股票收益指标
export const getStockMetrics = (code: string) => {
  return request.get<ApiResponse<StockMetrics>>(`/api/stocks/${code}/metrics`)
}
