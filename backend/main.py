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
    {
        "code": "000001",
        "name": "平安银行",
        "industry": "银行",
        "latest_price": 10.25,
    },
    {
        "code": "000002",
        "name": "万科A",
        "industry": "房地产",
        "latest_price": 7.86,
    },
    {
        "code": "600519",
        "name": "贵州茅台",
        "industry": "食品饮料",
        "latest_price": 1520.5,
    },
]

@app.get('/api/health')
def health_check():
    return {'status': 'ok'}

@app.get('/api/stocks')
def get_stocks():
    return {"data": stocks}