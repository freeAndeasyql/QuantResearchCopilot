from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data.stocks import (
    filter_stocks,
    find_stock_by_code,
    list_industries,
    paginate_stocks,
)

app = FastAPI(title="Quant Research Copilot API")

# 配置 CORS
# 因为前端运行在 5173，后端运行在 8001
# 浏览器默认不允许跨端口请求，所以这里要允许前端访问后端
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


# 健康检查接口
# 用来确认后端服务是否正常运行
@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# 股票列表接口
# 支持搜索、行业筛选、分页
@app.get("/api/stocks")
def get_stocks(
    keyword: str = "",
    industry: str = "",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=5, ge=1, le=50),
):
    # 第一步：根据 keyword 和 industry 筛选股票
    filtered_stocks = filter_stocks(keyword=keyword, industry=industry)

    # 第二步：对筛选后的结果进行分页
    paged_stocks = paginate_stocks(
        stocks=filtered_stocks,
        page=page,
        page_size=page_size,
    )

    # 第三步：返回前端需要的数据
    # data：当前页数据
    # total：筛选后的总数量
    # page：当前页
    # page_size：每页数量
    return {
        "data": paged_stocks,
        "total": len(filtered_stocks),
        "page": page,
        "page_size": page_size,
    }


# 行业列表接口
# 前端行业下拉框会用这个接口
@app.get("/api/industries")
def get_industries():
    return {"data": list_industries()}


# 股票详情接口
# 根据股票代码查询单只股票
@app.get("/api/stocks/{code}")
def get_stock_detail(code: str):
    stock = find_stock_by_code(code)

    # 如果没有找到股票，就返回 404
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")

    return {"data": stock}