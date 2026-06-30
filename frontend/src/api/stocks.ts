import { request } from './request'

export interface StockItem {
  code: string
  name: string
  industry: string
  latest_price: number
}

// 获取股票列表
export const getStocks = () => {
  return request.get<{ data: StockItem[] }>('/api/stocks')
}

// 获取单只股票详情
export const getStockDetail = (code: string) => {
  return request.get<{ data: StockItem }>(`/api/stocks/${code}`)
}