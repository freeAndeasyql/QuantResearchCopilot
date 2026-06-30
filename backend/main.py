from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data.stocks import find_stock_by_code, list_stocks

app = FastAPI(title='Quant Research Copilot API')

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



@app.get('/api/health')
def health_check():
    return {'status': 'ok'}

@app.get("/api/stocks")
def get_stocks():
    return {"data": list_stocks()}

# 返回单只股票详情
@app.get("/api/stocks/{code}")
def get_stock_details(code: str):
    stock = find_stock_by_code(code)
    if not stock:
        raise HTTPException(status_code=404, detail="股票不存在")
    return {"data": stock}