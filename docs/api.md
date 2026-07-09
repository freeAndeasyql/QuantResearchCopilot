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

### 字段说明

| 字段   | 类型   | 说明         |
| ------ | ------ | ------------ |
| status | string | 后端服务状态 |

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

### 字段说明

| 字段         | 类型   | 说明                              |
| ------------ | ------ | --------------------------------- |
| list         | array  | 股票列表                          |
| total        | number | 筛选后的股票总数                  |
| page         | number | 当前页码                          |
| page_size    | number | 每页数量                          |
| code         | string | 股票代码                          |
| name         | string | 股票名称                          |
| industry     | string | 所属行业                          |
| latest_price | number | 最新价格，优先来自 CSV 最新收盘价 |

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

### 错误示例

```json
{
  "code": 404,
  "message": "股票不存在",
  "data": null
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

### 字段说明

| 字段       | 类型   | 说明     |
| ---------- | ------ | -------- |
| trade_date | string | 交易日期 |
| close      | number | 收盘价   |

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

### 错误示例

```json
{
  "code": 404,
  "message": "该股票没有足够的历史价格数据，无法计算收益指标",
  "data": null
}
```

---

## 9. 行情数据状态接口

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

### 字段说明

| 字段              | 类型    | 说明                                            |
| ----------------- | ------- | ----------------------------------------------- |
| exists            | boolean | CSV 文件是否存在                                |
| source            | string  | 数据来源，例如 `BaoStock`、`AKShare`、`unknown` |
| updated_at        | string  | 数据更新时间                                    |
| start_date        | string  | 数据开始日期                                    |
| end_date          | string  | 数据结束日期                                    |
| latest_trade_date | string  | CSV 中最新交易日                                |
| row_count         | number  | 数据总行数                                      |
| stock_count       | number  | 股票数量                                        |

---

## 10. 行情数据质量检查接口

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

### 字段说明

| 字段                | 类型    | 说明                                             |
| ------------------- | ------- | ------------------------------------------------ |
| has_data            | boolean | 是否存在行情数据                                 |
| status              | string  | 数据质量状态，例如 `normal`、`warning`、`danger` |
| level               | string  | 中文状态说明，例如 `正常`、`警告`、`异常`        |
| summary             | string  | 数据质量整体结论                                 |
| row_count           | number  | 数据总行数                                       |
| missing_value_count | number  | 缺失值数量                                       |
| duplicate_row_count | number  | 重复行数量                                       |
| missing_close_count | number  | 收盘价缺失数量                                   |
| stock_record_counts | array   | 每只股票的数据记录数                             |

### 异常数据示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "has_data": false,
    "status": "danger",
    "level": "异常",
    "summary": "CSV 文件不存在或没有任何行情数据",
    "row_count": 0,
    "missing_value_count": 0,
    "duplicate_row_count": 0,
    "missing_close_count": 0,
    "stock_record_counts": []
  }
}
```

---

## 11. 数据质量 Markdown 报告接口

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

### 字段说明

| 字段   | 类型   | 说明                        |
| ------ | ------ | --------------------------- |
| report | string | Markdown 格式的数据质量报告 |

---

## 12. 前端使用到的主要接口

### 行情页 `/market`

主要使用：

```text
GET /api/stocks
GET /api/industries
GET /api/stocks/{code}
GET /api/stocks/{code}/prices
GET /api/stocks/{code}/metrics
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

## 13. 当前数据文件说明

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

## 14. 后续计划接口

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
