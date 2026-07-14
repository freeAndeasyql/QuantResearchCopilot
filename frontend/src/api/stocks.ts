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

export interface DataStatus {
  exists: boolean
  source: string
  updated_at: string
  start_date: string
  end_date: string
  latest_trade_date: string
  row_count: number
  stock_count: number
}

// 获取行情数据状态
export const getDataStatus = () => {
  return request.get<ApiResponse<DataStatus>>('/api/data/status')
}

export interface StockRecordCount {
  stock_code: string
  record_count: number
}

export interface DataQuality {
  has_data: boolean
  status: string
  level: string
  summary: string
  row_count: number
  missing_value_count: number
  duplicate_row_count: number
  missing_close_count: number
  stock_record_counts: StockRecordCount[]
}

// 获取行情数据质量报告
export const getDataQuality = () => {
  return request.get<ApiResponse<DataQuality>>('/api/data/quality')
}

export interface DataQualityReport {
  report: string
}

// 获取数据质量 Markdown 报告
export const getDataQualityReport = () => {
  return request.get<ApiResponse<DataQualityReport>>('/api/data/quality/report')
}

// 技术指标类型和接口
export interface StockIndicatorItem {
  trade_date: string
  close: number | null
  ma5: number | null
  ma10: number | null
  ma20: number | null
  volume: number | null
}

// 获取股票技术指标
export const getStockIndicators = (code: string) => {
  return request.get<ApiResponse<StockIndicatorItem[]>>(`/api/stocks/${code}/indicators`)
}

// 获取股票技术指标解读
export interface StockIndicatorSummary {
  trade_date: string
  close: number | null
  ma5: number | null
  ma10: number | null
  ma20: number | null
  trend: string
  summary: string
  signals: string[]
}

export const getStockIndicatorSummary = (code: string) => {
  return request.get<ApiResponse<StockIndicatorSummary>>(`/api/stocks/${code}/indicator-summary`)
}

// 股票成交量解读
export interface StockVolumeSummary {
  trade_date: string
  signal: string
  price_status: string
  volume_status: string
  summary: string
  latest_close: number | null
  previous_close: number | null
  change_pct: number | null
  latest_volume: number | null
  average_volume_5d: number | null
  volume_ratio: number | null
}

// 获取股票成交量解读
export const getStockVolumeSummary = (code: string) => {
  return request.get<ApiResponse<StockVolumeSummary>>(`/api/stocks/${code}/volume-summary`)
}

// 综合分析中的单项评分依据
export interface StockAnalysisScoreDetail {
  dimension: string
  value: string | number | null
  score: number
}

// 股票综合分析结果
export interface StockAnalysisSummary {
  stock_code: string
  stock_name: string
  industry: string
  trade_date: string
  overall_view: string
  score: number
  summary: string
  highlights: string[]
  risks: string[]
  score_details: StockAnalysisScoreDetail[]
  disclaimer: string
}

// 获取股票综合分析
export const getStockAnalysisSummary = (code: string) => {
  return request.get<ApiResponse<StockAnalysisSummary>>(`/api/stocks/${code}/analysis-summary`)
}
