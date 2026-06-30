# Day 2 学习日志

## 日期

2026-06-30

## 今日主题

初始化 FastAPI 后端项目。

## 今天完成了什么

1. 在 `backend/` 中创建 Python 虚拟环境。
2. 安装 FastAPI 和 Uvicorn。
3. 创建 `main.py`。
4. 实现 `/api/health` 健康检查接口。
5. 解决 8000 端口被占用问题，改用 8001 端口启动。
6. 成功访问 `http://127.0.0.1:8001/api/health`。

## 今天理解了什么

1. FastAPI 用来开发后端接口。
2. Uvicorn 是运行 FastAPI 的开发服务器。
3. `/api/health` 用来判断后端服务是否正常。
4. 端口被占用时，可以换端口，也可以结束占用进程。

## 遇到的问题

8000 端口被占用，启动时报错：

```text
ERROR: [Errno 48] Address already in use