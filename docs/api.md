# Quant Research Copilot API 接口文档

## 1. 文档说明

本文档用于记录 `Quant Research Copilot` 项目的后端接口。

后端技术栈：

- FastAPI
- Python
- pandas
- CSV 行情数据
- BaoStock / AKShare 行情数据源

前端技术栈：

- Vue3
- TypeScript
- Axios
- ECharts
- markdown-it

---

## 2. 基础信息

### 后端服务地址

```text
http://127.0.0.1:8001
```

### 前端服务地址

```text
http://127.0.0.1:5176
```

### 通用响应结构

所有接口统一返回以下结构：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

字段说明：

| 字段    | 类型   | 说明                   |
| ------- | ------ | ---------------------- |
| code    | number | 状态码，成功一般为 200 |
| message | string | 响应信息               |
| data    | any    | 具体业务数据           |

### 通用错误响应结构

```json
{
  "code": 404,
  "message": "股票不存在",
  "data": null
}
```

---

## 3. 健康检查接口

### 接口地址

```http
GET /api/health
```

### 接口说明

用于检查后端服务是否正常运行。

### 请求参数

无。

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "ok"
  }
}
```

---

## 4. 股票列表接口

### 接口地址

```http
GET /api/stocks
```

### 接口说明

获取股票列表，支持关键词搜索、行业筛选和分页。

股票列表中的 `latest_price` 会优先使用 `daily_price.csv` 中的最新收盘价。

### 请求参数

| 参数      | 类型   | 必填 | 默认值   | 说明                     |
| --------- | ------ | ---- | -------- | ------------------------ |
| keyword   | string | 否   | 空字符串 | 股票名称或股票代码关键词 |
| industry  | string | 否   | 空字符串 | 行业名称                 |
| page      | number | 否   | 1        | 当前页码                 |
| page_size | number | 否   | 5        | 每页数量，最大 50        |

### 请求示例

```http
GET /api/stocks?keyword=贵州&page=1&page_size=5
```

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "code": "600519",
        "name": "贵州茅台",
        "industry": "白酒",
        "latest_price": 1500.25
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 5
  }
}
```

---

## 5. 行业列表接口

### 接口地址

```http
GET /api/industries
```

### 接口说明

获取当前股票列表中包含的行业，用于前端行业筛选下拉框。

### 请求参数

无。

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": ["银行", "白酒", "新能源"]
}
```

---

## 6. 股票详情接口

### 接口地址

```http
GET /api/stocks/{code}
```

### 接口说明

根据股票代码获取单只股票详情。

详情中的 `latest_price` 会优先使用 `daily_price.csv` 中的最新收盘价。

### 路径参数

| 参数 | 类型   | 必填 | 说明                    |
| ---- | ------ | ---- | ----------------------- |
| code | string | 是   | 股票代码，例如 `600519` |

### 请求示例

```http
GET /api/stocks/600519
```

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "code": "600519",
    "name": "贵州茅台",
    "industry": "白酒",
    "latest_price": 1500.25
  }
}
```

---

## 7. 股票历史价格接口

### 接口地址

```http
GET /api/stocks/{code}/prices
```

### 接口说明

根据股票代码，从 `daily_price.csv` 中读取最近 30 条历史收盘价。

该接口主要用于前端绘制股票价格走势图。

### 路径参数

| 参数 | 类型   | 必填 | 说明                    |
| ---- | ------ | ---- | ----------------------- |
| code | string | 是   | 股票代码，例如 `600519` |

### 请求示例

```http
GET /api/stocks/600519/prices
```

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "trade_date": "2026-06-01",
      "close": 1480.5
    },
    {
      "trade_date": "2026-06-02",
      "close": 1492.3
    }
  ]
}
```

---

## 8. 股票收益指标接口

### 接口地址

```http
GET /api/stocks/{code}/metrics
```

### 接口说明

根据股票代码，从 `daily_price.csv` 中读取最近 30 条行情数据，计算股票收益指标。

包括：

- 最新交易日
- 最新收盘价
- 前一交易日收盘价
- 涨跌额
- 涨跌幅
- 区间天数
- 区间收益率

### 路径参数

| 参数 | 类型   | 必填 | 说明                    |
| ---- | ------ | ---- | ----------------------- |
| code | string | 是   | 股票代码，例如 `600519` |

### 请求示例

```http
GET /api/stocks/600519/metrics
```

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "latest_trade_date": "2026-07-09",
    "latest_close": 1500.25,
    "previous_close": 1490.8,
    "change_amount": 9.45,
    "change_pct": 0.63,
    "period_days": 30,
    "period_return": 3.25
  }
}
```

### 字段说明

| 字段              | 类型   | 说明             |
| ----------------- | ------ | ---------------- |
| latest_trade_date | string | 最新交易日       |
| latest_close      | number | 最新收盘价       |
| previous_close    | number | 前一交易日收盘价 |
| change_amount     | number | 涨跌额           |
| change_pct        | number | 涨跌幅           |
| period_days       | number | 统计区间天数     |
| period_return     | number | 区间收益率       |

---

## 9. 股票技术指标接口

### 接口地址

```http
GET /api/stocks/{code}/indicators
```

### 接口说明

根据股票代码，从 `daily_price.csv` 中读取最近 120 条行情数据，计算股票技术指标。

当前支持的指标：

- 收盘价
- MA5：5 日移动平均线
- MA10：10 日移动平均线
- MA20：20 日移动平均线

该接口主要用于前端走势图展示收盘价和多条均线。

### 路径参数

| 参数 | 类型   | 必填 | 说明                    |
| ---- | ------ | ---- | ----------------------- |
| code | string | 是   | 股票代码，例如 `600519` |

### 请求示例

```http
GET /api/stocks/600519/indicators
```

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "trade_date": "2026-06-01",
      "close": 1500.25,
      "ma5": 1498.32,
      "ma10": 1495.67,
      "ma20": 1488.21
    }
  ]
}
```

### 字段说明

| 字段       | 类型          | 说明            |
| ---------- | ------------- | --------------- |
| trade_date | string        | 交易日期        |
| close      | number / null | 收盘价          |
| ma5        | number / null | 5 日移动平均线  |
| ma10       | number / null | 10 日移动平均线 |
| ma20       | number / null | 20 日移动平均线 |

### 注意事项

前几条数据的 `ma5`、`ma10`、`ma20` 可能为 `null`。

原因是移动平均线需要足够的历史数据才能计算：

| 指标 | 至少需要数据条数 |
| ---- | ---------------: |
| MA5  |             5 条 |
| MA10 |            10 条 |
| MA20 |            20 条 |

---

## 10. 股票技术指标解读接口

### 接口地址

```http
GET /api/stocks/{code}/indicator-summary
```

### 接口说明

根据股票最新收盘价、MA5、MA10、MA20，生成通俗的趋势解读。

该接口用于前端展示“技术指标解读卡片”。

注意：该接口只基于均线关系做规则判断，用于学习和辅助观察，不构成投资建议。

### 路径参数

| 参数 | 类型   | 必填 | 说明                    |
| ---- | ------ | ---- | ----------------------- |
| code | string | 是   | 股票代码，例如 `600519` |

### 请求示例

```http
GET /api/stocks/600519/indicator-summary
```

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "trade_date": "2026-07-09",
    "close": 1500.25,
    "ma5": 1498.32,
    "ma10": 1495.67,
    "ma20": 1488.21,
    "trend": "偏强",
    "summary": "当前收盘价高于 MA5、MA10、MA20，且短期均线在中期均线上方，走势相对偏强。",
    "signals": [
      "收盘价在 MA5 上方，短期价格表现较强",
      "收盘价在 MA20 上方，价格仍处于近一个月均价上方"
    ]
  }
}
```

### 字段说明

| 字段       | 类型          | 说明                                                  |
| ---------- | ------------- | ----------------------------------------------------- |
| trade_date | string        | 最新交易日                                            |
| close      | number / null | 最新收盘价                                            |
| ma5        | number / null | 5 日移动平均线                                        |
| ma10       | number / null | 10 日移动平均线                                       |
| ma20       | number / null | 20 日移动平均线                                       |
| trend      | string        | 趋势判断，例如 `偏强`、`偏弱`、`震荡偏强`、`震荡偏弱` |
| summary    | string        | 通俗解读文案                                          |
| signals    | string[]      | 关键信号列表                                          |

### 数据不足示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "trade_date": "2026-01-05",
    "close": 10.25,
    "ma5": null,
    "ma10": null,
    "ma20": null,
    "trend": "数据不足",
    "summary": "当前历史数据不足，暂时无法形成完整均线解读。",
    "signals": []
  }
}
```

---

## 11. 行情数据状态接口

### 接口地址

```http
GET /api/data/status
```

### 接口说明

用于查看当前行情 CSV 文件状态。

该接口会读取：

```text
data/raw/daily_price.csv
data/raw/daily_price_meta.json
```

返回内容包括：

- CSV 文件是否存在
- 数据来源
- 数据更新时间
- 数据开始日期
- 数据结束日期
- CSV 中最新交易日
- 数据行数
- 股票数量

### 请求参数

无。

### 请求示例

```http
GET /api/data/status
```

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "exists": true,
    "source": "BaoStock",
    "updated_at": "2026-07-09 10:30:00",
    "start_date": "2026-01-01",
    "end_date": "2026-07-09",
    "latest_trade_date": "2026-07-09",
    "row_count": 600,
    "stock_count": 5
  }
}
```

---

## 12. 行情数据质量检查接口

### 接口地址

```http
GET /api/data/quality
```

### 接口说明

用于检查 `daily_price.csv` 的数据质量。

当前检查内容包括：

- 是否存在行情数据
- 数据总行数
- 缺失值数量
- 重复行数量
- 收盘价缺失数量
- 每只股票的数据记录数
- 整体数据质量结论

### 请求参数

无。

### 请求示例

```http
GET /api/data/quality
```

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "has_data": true,
    "status": "normal",
    "level": "正常",
    "summary": "数据质量正常，暂无缺失值和重复行",
    "row_count": 600,
    "missing_value_count": 0,
    "duplicate_row_count": 0,
    "missing_close_count": 0,
    "stock_record_counts": [
      {
        "stock_code": "000001",
        "record_count": 120
      },
      {
        "stock_code": "600519",
        "record_count": 120
      }
    ]
  }
}
```

---

## 13. 数据质量 Markdown 报告接口

### 接口地址

```http
GET /api/data/quality/report
```

### 接口说明

根据数据质量检查结果，生成 Markdown 格式的数据质量报告。

该报告可用于：

1. 前端页面展示；
2. 一键复制；
3. 下载为 `.md` 文件；
4. 后续交给 AI 进行数据质量解释。

### 请求参数

无。

### 请求示例

```http
GET /api/data/quality/report
```

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "report": "# 数据质量报告\n\n## 总体结论\n\n数据质量正常，暂无缺失值和重复行。\n\n## 核心指标\n\n| 指标 | 数值 |\n|---|---:|\n| 数据状态 | 正常 |\n| 总行数 | 600 |\n| 缺失值数量 | 0 |\n| 重复行数量 | 0 |\n| 收盘价缺失数量 | 0 |"
  }
}
```

---

## 14. 前端使用到的主要接口

### 行情页 `/market`

主要使用：

```text
GET /api/stocks
GET /api/industries
GET /api/stocks/{code}
GET /api/stocks/{code}/prices
GET /api/stocks/{code}/metrics
GET /api/stocks/{code}/indicators
GET /api/stocks/{code}/indicator-summary
```

### 状态页 `/status`

主要使用：

```text
GET /api/health
GET /api/data/status
GET /api/data/quality
GET /api/data/quality/report
```

---

## 15. 当前数据文件说明

### 行情数据文件

```text
data/raw/daily_price.csv
```

主要字段：

| 字段          | 说明     |
| ------------- | -------- |
| stock_code    | 股票代码 |
| trade_date    | 交易日期 |
| open          | 开盘价   |
| close         | 收盘价   |
| high          | 最高价   |
| low           | 最低价   |
| volume        | 成交量   |
| amount        | 成交额   |
| amplitude     | 振幅     |
| change_pct    | 涨跌幅   |
| change_amount | 涨跌额   |
| turnover_rate | 换手率   |

### 数据源元信息文件

```text
data/raw/daily_price_meta.json
```

示例：

```json
{
  "source": "BaoStock",
  "updated_at": "2026-07-09 10:30:00",
  "start_date": "2026-01-01",
  "end_date": "2026-07-09",
  "stock_count": 5,
  "row_count": 600
}
```

字段说明：

| 字段        | 说明         |
| ----------- | ------------ |
| source      | 数据来源     |
| updated_at  | 数据更新时间 |
| start_date  | 数据开始日期 |
| end_date    | 数据结束日期 |
| stock_count | 股票数量     |
| row_count   | 数据行数     |

---

## 16. 当前已完成能力

当前项目已经具备：

1. 股票列表查询；
2. 股票搜索和行业筛选；
3. 股票详情查看；
4. CSV 行情数据读取；
5. 股票历史收盘价展示；
6. 收益指标计算；
7. MA5、MA10、MA20 技术指标计算；
8. 技术指标趋势解读；
9. 行情数据状态检查；
10. 数据质量检查；
11. 数据质量 Markdown 报告生成；
12. Markdown 报告复制；
13. Markdown 报告下载；
14. 前端 Markdown 渲染。

---

## 17. 后续计划接口

后续可能新增：

```text
GET /api/factors
GET /api/stocks/{code}/factors
GET /api/strategy/backtest
GET /api/ai/report
GET /api/ai/stock-summary/{code}
```

计划方向：

1. 增加因子数据接口；
2. 增加简单回测接口；
3. 增加 AI 股票分析报告接口；
4. 增加 RAG 文档问答接口；
5. 增加投资研究报告生成接口。
