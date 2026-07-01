MOCK_STOCKS = [
    {"code": "000001", "name": "平安银行", "industry": "银行", "latest_price": 10.25},
    {"code": "000002", "name": "万科A", "industry": "房地产", "latest_price": 7.86},
    {"code": "000063", "name": "中兴通讯", "industry": "通信", "latest_price": 31.42},
    {"code": "000333", "name": "美的集团", "industry": "家电", "latest_price": 68.15},
    {"code": "000651", "name": "格力电器", "industry": "家电", "latest_price": 39.82},
    {"code": "000858", "name": "五粮液", "industry": "食品饮料", "latest_price": 128.36},
    {"code": "002415", "name": "海康威视", "industry": "电子", "latest_price": 33.67},
    {"code": "002594", "name": "比亚迪", "industry": "汽车", "latest_price": 246.8},
    {"code": "300750", "name": "宁德时代", "industry": "电力设备", "latest_price": 192.45},
    {"code": "600000", "name": "浦发银行", "industry": "银行", "latest_price": 8.91},
    {"code": "600036", "name": "招商银行", "industry": "银行", "latest_price": 36.28},
    {"code": "600276", "name": "恒瑞医药", "industry": "医药生物", "latest_price": 42.19},
    {"code": "600519", "name": "贵州茅台", "industry": "食品饮料", "latest_price": 1520.5},
    {"code": "600887", "name": "伊利股份", "industry": "食品饮料", "latest_price": 27.34},
    {"code": "601318", "name": "中国平安", "industry": "非银金融", "latest_price": 48.76},
]

def list_stocks():
    return MOCK_STOCKS

# 根据股票代码查单只股票
def find_stock_by_code(code: str):
    return next((stock for stock in MOCK_STOCKS if stock["code"] == code), None)

# 根据关键字和行业筛选股票
def filter_stocks(keyword: str = None, industry: str = None):
    value = keyword.strip().lower()
    result = MOCK_STOCKS
    if value:
        result = [stock for stock in result if value in stock["name"].lower() or value in stock["code"] or value in stock["industry"].lower()]
    if industry:
        result = [stock for stock in result if stock["industry"].lower() == industry.strip().lower()]
    return result

# 对股票列表进行分页
def paginate_stocks(stocks, page: int = 1, page_size: int = 10):
    start = (page - 1) * page_size
    end = start + page_size
    return stocks[start:end]

# 获取所有行业选项
def list_industries():
    # set 用来去重
    # sorted 用来排序，让返回结果更稳定
    return sorted(set(stock["industry"] for stock in MOCK_STOCKS))

# 股票历史价格 Mock 数据
# key 是股票代码，value 是该股票最近几天的价格
MOCK_STOCK_PRICES = {
    "600519": [
        {"trade_date": "2026-06-24", "close": 1512.0},
        {"trade_date": "2026-06-25", "close": 1518.5},
        {"trade_date": "2026-06-26", "close": 1525.0},
        {"trade_date": "2026-06-29", "close": 1519.2},
        {"trade_date": "2026-06-30", "close": 1520.5},
    ],
    "000001": [
        {"trade_date": "2026-06-24", "close": 10.12},
        {"trade_date": "2026-06-25", "close": 10.18},
        {"trade_date": "2026-06-26", "close": 10.22},
        {"trade_date": "2026-06-29", "close": 10.2},
        {"trade_date": "2026-06-30", "close": 10.25},
    ],
}


# 根据股票代码查询历史价格
# 如果没有该股票的历史价格，就返回空列表
def list_stock_prices(code: str):
    return MOCK_STOCK_PRICES.get(code, [])