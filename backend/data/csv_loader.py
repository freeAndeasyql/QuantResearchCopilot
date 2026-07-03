from pathlib import Path

import pandas as pd


# 当前文件位置：
# backend/data/csv_loader.py
#
# parents[0] = backend/data
# parents[1] = backend
# parents[2] = 项目根目录 quant-research-copilot
PROJECT_ROOT = Path(__file__).resolve().parents[2]


# 拼出稳定的 CSV 绝对路径
# 这样不管在哪个目录启动 uvicorn，都能找到 data/raw/daily_price.csv
DAILY_PRICE_FILE = PROJECT_ROOT / "data" / "raw" / "daily_price.csv"


# 读取日线行情 CSV
def load_daily_price():
    # 如果 CSV 文件不存在，返回空表
    if not DAILY_PRICE_FILE.exists():
        print(f"CSV 文件不存在：{DAILY_PRICE_FILE}")
        return pd.DataFrame()

    # 读取 CSV
    # dtype={"stock_code": str} 用来保留 000001 这种前导 0
    df = pd.read_csv(
        DAILY_PRICE_FILE,
        dtype={"stock_code": str},
        encoding="utf-8-sig",
    )

    # 统一把股票代码补齐成 6 位
    # 防止 000001 被错误读成 1
    df["stock_code"] = df["stock_code"].astype(str).str.zfill(6)

    return df


# 根据股票代码获取最近 N 条价格
def get_recent_prices_by_code(stock_code: str, limit: int = 30):
    df = load_daily_price()

    # 如果 CSV 为空，返回空列表
    if df.empty:
        return []

    # 把传入的股票代码也统一补齐成 6 位
    code = stock_code.zfill(6)

    # 筛选指定股票
    stock_df = df[df["stock_code"] == code].copy()

    # 如果没有该股票行情，返回空列表
    if stock_df.empty:
        return []

    # 按日期升序排序
    stock_df = stock_df.sort_values("trade_date")

    # 取最近 limit 条
    stock_df = stock_df.tail(limit)

    # 只返回前端画图需要的字段
    return stock_df[["trade_date", "close"]].to_dict(orient="records")

# 根据股票代码计算基础收益指标
def get_stock_metrics_by_code(stock_code: str, limit: int = 30):
    df = load_daily_price()

    # 如果 CSV 为空，返回空字典
    if df.empty:
        return {}

    # 把传入的股票代码也统一补齐成 6 位
    code = stock_code.zfill(6)

    # 筛选指定股票
    stock_df = df[df["stock_code"] == code].copy()

    # 如果没有该股票行情
    if stock_df.empty:
        return None

    # 按日期升序排序
    stock_df = stock_df.sort_values("trade_date")

    # 取最近 limit 条
    recent_df = stock_df.tail(limit)

    if len(recent_df) < 2:
        # 如果数据不足两条，无法计算收益指标
        return None

    # 最新一条行情
    latest = recent_df.iloc[-1]

   # 前一个交易日行情
    previous = recent_df.iloc[-2]

    # 最新收盘价
    latest_close = float(latest["close"])

    # 前一交易日收盘价
    previous_close = float(previous["close"])
    # 涨跌额
    change_amount = latest_close - previous_close
    # 涨跌幅（百分比）
    change_pct = (change_amount / previous_close) * 100 if previous_close  else 0

    # 最近N日收益率
    first_close = float(recent_df.iloc[0]["close"])
    period_return = (latest_close - first_close) / first_close * 100 if first_close else 0

    # 返回指标数据
    return {
        "stock_code": code,
        "latest_trade_date": latest["trade_date"],
        "latest_close": round(latest_close, 2),
        "previous_close": round(previous_close, 2),
        "change_amount": round(change_amount, 2),
        "change_pct": round(change_pct, 2),
        "period_days": len(recent_df),
        "period_return": round(period_return, 2),
    }

# 获取单只股票的最新收盘价
def get_latest_close_by_code(stock_code: str):
    df = load_daily_price()

    if df.empty:
        return None

    code = stock_code.zfill(6)
    stock_df = df[df["stock_code"] == code].copy()

    if stock_df.empty:
        return None

    # 按照交易日期生序排序
    stock_df = stock_df.sort_values("trade_date")

    latest = stock_df.iloc[-1]
    return round(float(latest["close"]), 2)

# 批量获取所有股票的最新收盘价
def get_latest_close_map():
    df = load_daily_price()

    if df.empty:
        return {}

    # 按股票代码和交易日期排序
    sorted_df = df.sort_values(["stock_code", "trade_date"])

    # 每只股票取最后一条记录
    latest_df = sorted_df.groupby("stock_code").tail(1)

    # 转成字典：
    # {
    #   "600519": 1520.5,
    #   "000001": 10.25
    # }
    latest_close_map = {}

    for _, row in latest_df.iterrows():
      stock_code = str(row["stock_code"]).zfill(6)
      latest_close_map[stock_code] = round(float(row["close"]), 2)

    return latest_close_map


# 获取 CSV 数据状态
def get_daily_price_status():
    df = load_daily_price()

    # 如果 CSV 没有数据，返回空状态
    if df.empty:
        return {
            "source": "daily_price.csv",
            "exists": False,
            "latest_trade_date": None,
            "row_count": 0,
            "stock_count": 0,
        }

    # 获取最新交易日
    latest_trade_date = df["trade_date"].max()

    # 获取数据总行数
    row_count = len(df)

    # 获取股票数量
    stock_count = df["stock_code"].nunique()

    return {
        "source": "daily_price.csv",
        "exists": True,
        "latest_trade_date": latest_trade_date,
        "row_count": row_count,
        "stock_count": stock_count,
    }

# 检查 CSV 数据质量
def check_daily_price_quality():
    df = load_daily_price()

    # 如果 CSV 没有数据，返回空质量报告
    if df.empty:
        return {
            "has_data": False,
            "row_count": 0,
            "missing_value_count": 0,
            "duplicate_row_count": 0,
            "missing_close_count": 0,
            "stock_record_counts": [],
        }

    # 缺失值总数
    missing_value_count = int(df.isna().sum().sum())

    # 重复行数量
    duplicate_row_count = int(df.duplicated().sum())

    # 收盘价缺失数量
    missing_close_count = int(df["close"].isna().sum()) if "close" in df.columns else 0

    # 每只股票的数据行数
    stock_record_counts = (
        df.groupby("stock_code")
        .size()
        .reset_index(name="record_count")
        .sort_values("stock_code")
        .to_dict(orient="records")
    )

    return {
        "has_data": True,
        "row_count": len(df),
        "missing_value_count": missing_value_count,
        "duplicate_row_count": duplicate_row_count,
        "missing_close_count": missing_close_count,
        "stock_record_counts": stock_record_counts,
    }