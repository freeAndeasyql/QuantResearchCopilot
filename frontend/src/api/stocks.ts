import { request } from './request'

export interface StockItem {
  code: string
  name: string
  industry: string
  latest_price: number
}

export const getStocks = () => {
  return request.get<{ data: StockItem[] }>('/api/stocks')
}