from fastapi import FastAPI

app = FastAPI(title='Quant Research Copilot API')

@app.get('/api/health')
def health_check():
    return {'status': 'ok'}