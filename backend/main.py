from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from data.stocks import (
    filter_stocks,
    find_stock_by_code,
    list_industries,
    paginate_stocks,
    list_stock_prices
)
from utils.response import error_response, success_response


app = FastAPI(title="Quant Research Copilot API")

# 配置 CORS
# 前端运行在 5173，后端运行在 8001
# 因为端口不同，浏览器会认为是跨域请求，所以后端要允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5176",
        "http://127.0.0.1:5176",
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

    # 第二步：对筛选后的股票进行分页
    paged_stocks = paginate_stocks(
        stocks=filtered_stocks,
        page=page,
        page_size=page_size,
    )

    # 第三步：把分页信息和列表一起返回给前端
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

    return success_response(data=stock)

# 股票历史价格接口
# 根据股票代码查询该股票最近几天的收盘价
@app.get("/api/stocks/{code}/prices")
def get_stock_prices(code: str):
    # 根据股票代码查找股票
    stock = find_stock_by_code(code)

    # 如果没找到，就返回 404
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")

    # 查询该股票的历史价格
    prices = list_stock_prices(code)

    return success_response(data=prices)