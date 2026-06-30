from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title='Quant Research Copilot API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ]
)

stocks = [
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

@app.get('/api/health')
def health_check():
    return {'status': 'ok'}

@app.get('/api/stocks')
def get_stocks():
    return {"data": stocks}