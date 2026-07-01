# API 文档

## 1. 通用响应结构

后端接口统一返回以下结构：

### 成功响应

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 错误响应

```json
{
  "code": 404,
  "message": "股票不存在",
  "data": null
}
```

## 2. 健康检查

### GET /api/health

用于检查后端服务是否正常运行。

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

## 3. 股票列表

### GET /api/stocks

用于获取股票列表，支持搜索、行业筛选和分页。

### 请求参数

| 参数      | 类型   | 必填 | 说明                      |
| --------- | ------ | ---- | ------------------------- |
| keyword   | string | 否   | 搜索股票代码、名称、行业  |
| industry  | string | 否   | 行业筛选                  |
| page      | number | 否   | 当前页，默认 1            |
| page_size | number | 否   | 每页数量，默认 5，最大 50 |

### 请求示例

```text
/api/stocks?keyword=银行&industry=银行&page=1&page_size=5
```

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "code": "000001",
        "name": "平安银行",
        "industry": "银行",
        "latest_price": 10.25
      }
    ],
    "total": 3,
    "page": 1,
    "page_size": 5
  }
}
```

## 4. 行业列表

### GET /api/industries

用于获取行业筛选下拉框选项。

### 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": ["银行", "食品饮料", "家电"]
}
```

## 5. 股票详情

### GET /api/stocks/{code}

根据股票代码获取单只股票详情。

### 路径参数

| 参数 | 类型   | 必填 | 说明     |
| ---- | ------ | ---- | -------- |
| code | string | 是   | 股票代码 |

### 请求示例

```text
/api/stocks/600519
```

### 成功响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "code": "600519",
    "name": "贵州茅台",
    "industry": "食品饮料",
    "latest_price": 1520.5
  }
}
```

### 错误响应示例

```json
{
  "code": 404,
  "message": "股票不存在",
  "data": null
}
```

## 6. 股票历史价格

### GET /api/stocks/{code}/prices

根据股票代码获取历史收盘价，用于前端绘制价格走势图。

### 路径参数

| 参数 | 类型   | 必填 | 说明     |
| ---- | ------ | ---- | -------- |
| code | string | 是   | 股票代码 |

### 请求示例

```text
/api/stocks/600519/prices
```

### 成功响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "trade_date": "2026-06-24",
      "close": 1512.0
    },
    {
      "trade_date": "2026-06-25",
      "close": 1518.5
    }
  ]
}
```

### 错误响应示例

```json
{
  "code": 404,
  "message": "股票不存在",
  "data": null
}
```
