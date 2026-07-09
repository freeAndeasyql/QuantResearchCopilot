from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from data.csv_loader import (
    check_daily_price_quality,
    generate_daily_price_quality_report,
    get_daily_price_status,
    get_latest_close_by_code,
    get_latest_close_map,
    get_recent_prices_by_code,
    get_stock_metrics_by_code,
    get_stock_indicators_by_code,
    get_stock_indicator_summary_by_code
)

from data.stocks import (
    filter_stocks,
    find_stock_by_code,
    list_industries,
    paginate_stocks,
)

from utils.response import error_response, success_response


app = FastAPI(title="Quant Research Copilot API")


# 配置 CORS
# 前端和后端端口不同，所以需要允许前端访问后端接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 统一处理 HTTPException
# 例如 raise HTTPException(status_code=404, detail="股票不存在")
# 会被转换成 { code: 404, message: "股票不存在", data: None }
@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code=exc.status_code, message=exc.detail),
    )


# 健康检查接口
# 用来确认后端服务是否正常运行
@app.get("/api/health")
def health_check():
    return success_response(data={"status": "ok"})


# 股票列表接口
# 支持搜索、行业筛选、分页
@app.get("/api/stocks")
def get_stocks(
    keyword: str = "",
    industry: str = "",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=5, ge=1, le=50),
):
    # 第一步：根据搜索词和行业筛选股票
    filtered_stocks = filter_stocks(keyword=keyword, industry=industry)

    # 第二步：从 CSV 中获取每只股票最新收盘价
    latest_close_map = get_latest_close_map()

    # 第三步：用 CSV 最新收盘价覆盖 Mock 数据里的 latest_price
    enriched_stocks = []

    for stock in filtered_stocks:
        stock_code = stock["code"]
        latest_price = latest_close_map.get(stock_code, stock["latest_price"])

        enriched_stocks.append(
            {
                **stock,
                "latest_price": latest_price,
            }
        )

    # 第四步：对增强后的股票列表进行分页
    paged_stocks = paginate_stocks(
        stocks=enriched_stocks,
        page=page,
        page_size=page_size,
    )

    return success_response(
        data={
            "list": paged_stocks,
            "total": len(filtered_stocks),
            "page": page,
            "page_size": page_size,
        }
    )


# 行业列表接口
# 前端行业下拉框会用这个接口
@app.get("/api/industries")
def get_industries():
    return success_response(data=list_industries())


# 股票详情接口
# 根据股票代码查询单只股票
@app.get("/api/stocks/{code}")
def get_stock_detail(code: str):
    # 根据股票代码查找股票
    stock = find_stock_by_code(code)

    # 如果没找到，就返回 404
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")

    # 从 CSV 中获取该股票最新收盘价
    latest_close = get_latest_close_by_code(code)

    # 如果 CSV 中有最新收盘价，就覆盖 Mock 数据里的 latest_price
    latest_price = latest_close if latest_close is not None else stock["latest_price"]

    # 返回增强后的股票详情
    enriched_stock = {
        **stock,
        "latest_price": latest_price,
    }

    return success_response(data=enriched_stock)


# 股票历史价格接口
# 根据股票代码从 CSV 中查询最近 30 条收盘价
@app.get("/api/stocks/{code}/prices")
def get_stock_prices(code: str):
    # 根据股票代码查找股票
    stock = find_stock_by_code(code)

    # 如果没找到，就返回 404
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")

    # 从 daily_price.csv 读取该股票最近 30 条价格
    prices = get_recent_prices_by_code(code, limit=30)

    return success_response(data=prices)


# 股票收益指标接口
# 根据股票代码从 CSV 中计算涨跌幅和区间收益率
@app.get("/api/stocks/{code}/metrics")
def get_stock_metrics(code: str):
    # 根据股票代码查找股票
    stock = find_stock_by_code(code)

    # 如果没找到，就返回 404
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")

    # 从 daily_price.csv 计算该股票的收益指标
    metrics = get_stock_metrics_by_code(code, limit=30)

    # 如果没有足够数据，返回 404
    if not metrics:
        raise HTTPException(
            status_code=404,
            detail="该股票没有足够的历史价格数据，无法计算收益指标",
        )

    return success_response(data=metrics)

# 股票技术指标接口
# 根据股票代码从 CSV 中计算 MA5、MA10、MA20
@app.get("/api/stocks/{code}/indicators")
def get_stock_indicators(code: str):
    # 根据股票代码查找股票
    stock = find_stock_by_code(code)

    # 如果股票不存在，返回 404
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")

    # 从 daily_price.csv 计算技术指标
    indicators = get_stock_indicators_by_code(code, limit=120)

    # 如果没有指标数据，返回空列表
    return success_response(data=indicators)

# 股票技术指标解读接口
# 根据最新收盘价、MA5、MA10、MA20 生成通俗趋势解读
@app.get("/api/stocks/{code}/indicator-summary")
def get_stock_indicator_summary(code: str):
    stock = find_stock_by_code(code)

    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")

    summary = get_stock_indicator_summary_by_code(code)

    if not summary:
        raise HTTPException(status_code=404, detail="该股票没有足够的技术指标数据")

    return success_response(data=summary)


# CSV 数据状态接口
# 用来查看当前行情数据文件是否存在、最新交易日、数据行数和股票数量
@app.get("/api/data/status")
def get_data_status():
    status = get_daily_price_status()

    return success_response(data=status)


# CSV 数据质量检查接口
# 用来检查行情数据是否有缺失值、重复行、收盘价缺失等问题
@app.get("/api/data/quality")
def get_data_quality():
    quality = check_daily_price_quality()

    return success_response(data=quality)


# 数据质量 Markdown 报告接口
# 返回一段可直接展示或保存的 Markdown 文本
@app.get("/api/data/quality/report")
def get_data_quality_report():
    report = generate_daily_price_quality_report()

    return success_response(data={"report": report})