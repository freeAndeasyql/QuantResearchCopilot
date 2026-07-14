from pathlib import Path

import pandas as pd
import json


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

# 行情数据元信息文件
# 用来记录 daily_price.csv 来自哪个数据源、什么时候更新
DAILY_PRICE_META_FILE = PROJECT_ROOT / "data" / "raw" / "daily_price_meta.json"


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
# 1. 先读取 daily_price_meta.json
# 2. 再读取 daily_price.csv
# 3. 如果元信息文件不存在，也不会报错
# 4. 接口统一返回 source、updated_at、start_date、end_date
# 获取 daily_price.csv 当前状态
def get_daily_price_status():
    # 先读取数据源元信息
    meta = load_daily_price_meta()

    # 如果 CSV 文件不存在，返回基础状态
    if not DAILY_PRICE_FILE.exists():
        return {
            "exists": False,
            "source": meta.get("source", "unknown"),
            "updated_at": meta.get("updated_at", ""),
            "start_date": meta.get("start_date", ""),
            "end_date": meta.get("end_date", ""),
            "latest_trade_date": "",
            "row_count": 0,
            "stock_count": 0,
        }

    df = load_daily_price()

    # 如果 CSV 存在但没有数据
    if df.empty:
        return {
            "exists": True,
            "source": meta.get("source", "unknown"),
            "updated_at": meta.get("updated_at", ""),
            "start_date": meta.get("start_date", ""),
            "end_date": meta.get("end_date", ""),
            "latest_trade_date": "",
            "row_count": 0,
            "stock_count": 0,
        }

    latest_trade_date = ""

    if "trade_date" in df.columns:
        latest_trade_date = str(df["trade_date"].max())

    stock_count = 0

    if "stock_code" in df.columns:
        stock_count = int(df["stock_code"].nunique())

    return {
        "exists": True,
        "source": meta.get("source", "unknown"),
        "updated_at": meta.get("updated_at", ""),
        "start_date": meta.get("start_date", ""),
        "end_date": meta.get("end_date", ""),
        "latest_trade_date": latest_trade_date,
        "row_count": len(df),
        "stock_count": stock_count,
    }

# 检查 CSV 数据质量
def check_daily_price_quality():
    df = load_daily_price()

    # 如果 CSV 没有数据，返回异常结论
    if df.empty:
        return {
            "has_data": False,
            "status": "danger",
            "level": "异常",
            "summary": "CSV 文件不存在或没有任何行情数据",
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

    # 根据数据质量指标生成整体结论
    has_warning = (
        missing_value_count > 0
        or duplicate_row_count > 0
        or missing_close_count > 0
    )

    if has_warning:
        status = "warning"
        level = "警告"
        summary = "数据存在缺失值、重复行或收盘价缺失，请检查 CSV 数据"
    else:
        status = "normal"
        level = "正常"
        summary = "数据质量正常，暂无缺失值和重复行"

    return {
        "has_data": True,
        "status": status,
        "level": level,
        "summary": summary,
        "row_count": len(df),
        "missing_value_count": missing_value_count,
        "duplicate_row_count": duplicate_row_count,
        "missing_close_count": missing_close_count,
        "stock_record_counts": stock_record_counts,
    }

# 生成数据质量 Markdown 报告
def generate_daily_price_quality_report():
    quality = check_daily_price_quality()

    # 用来生成每只股票记录数表格。
    stock_rows = []

    for item in quality["stock_record_counts"]:
        stock_rows.append(
            f'| {item["stock_code"]} | {item["record_count"]} |'
        )

    stock_table = "\n".join(stock_rows) if stock_rows else "| 暂无 | 0 |"

    report = f"""# 数据质量报告

## 总体结论

{quality["summary"]}

## 核心指标

| 指标 | 数值 |
|---|---:|
| 数据状态 | {quality["level"]} |
| 总行数 | {quality["row_count"]} |
| 缺失值数量 | {quality["missing_value_count"]} |
| 重复行数量 | {quality["duplicate_row_count"]} |
| 收盘价缺失数量 | {quality["missing_close_count"]} |

## 每只股票记录数

| 股票代码 | 记录数 |
|---|---:|
{stock_table}
"""

    return report


# 读取行情数据元信息
def load_daily_price_meta():
    # 如果元信息文件不存在，返回默认值
    if not DAILY_PRICE_META_FILE.exists():
        return {
            "source": "unknown",
            "updated_at": "",
            "start_date": "",
            "end_date": "",
        }

    try:
        with open(DAILY_PRICE_META_FILE, "r", encoding="utf-8") as meta_file:
            return json.load(meta_file)

    except Exception:
        # 如果 JSON 文件格式坏了，也不要让接口崩掉
        return {
            "source": "unknown",
            "updated_at": "",
            "start_date": "",
            "end_date": "",
        }

# 根据股票代码计算技术指标
# 当前先计算最基础的移动平均线：MA5、MA10、MA20
def get_stock_indicators_by_code(stock_code: str, limit: int = 120):
    df = load_daily_price()

    # 如果 CSV 没有数据，直接返回空列表
    if df.empty:
        return []

    # 如果缺少必要字段，也返回空列表
    if "stock_code" not in df.columns or "trade_date" not in df.columns or "close" not in df.columns:
        return []

    # 只筛选当前股票的数据
    stock_df = df[df["stock_code"] == stock_code].copy()

    # 如果当前股票没有行情数据，返回空列表
    if stock_df.empty:
        return []

    # 按交易日期升序排列
    # 移动平均线必须按时间顺序计算
    stock_df = stock_df.sort_values("trade_date")

    # 确保收盘价是数字类型
    stock_df["close"] = pd.to_numeric(stock_df["close"], errors="coerce")

    # 确保成交量是数字类型
    # 如果 CSV 中没有 volume 字段，就补充为空值
    if "volume" in stock_df.columns:
        stock_df["volume"] = pd.to_numeric(
            stock_df["volume"],
            errors="coerce",
        )
    else:
        stock_df["volume"] = pd.NA


    # 确保成交量是数字类型
    # 如果 CSV 中没有 volume 字段，就补一个空值列
    if "volume" in stock_df.columns:
        stock_df["volume"] = pd.to_numeric(stock_df["volume"], errors="coerce")
    else:
        stock_df["volume"] = None

    # 计算移动平均线
    # rolling(window=5) 表示每 5 条数据计算一次平均值
    stock_df["ma5"] = stock_df["close"].rolling(window=5).mean()
    stock_df["ma10"] = stock_df["close"].rolling(window=10).mean()
    stock_df["ma20"] = stock_df["close"].rolling(window=20).mean()

    # 只取最近 limit 条
    stock_df = stock_df.tail(limit)

    result = []

    for _, row in stock_df.iterrows():
        result.append(
        {
            "trade_date": row["trade_date"],
            "close": (
                None
                if pd.isna(row["close"])
                else round(float(row["close"]), 2)
            ),
            "ma5": (
                None
                if pd.isna(row["ma5"])
                else round(float(row["ma5"]), 2)
            ),
            "ma10": (
                None
                if pd.isna(row["ma10"])
                else round(float(row["ma10"]), 2)
            ),
            "ma20": (
                None
                if pd.isna(row["ma20"])
                else round(float(row["ma20"]), 2)
            ),
            "volume": (
                None
                if pd.isna(row["volume"])
                else int(float(row["volume"]))
            ),
    }
)

    return result

# 根据 MA5、MA10、MA20 生成通俗解读
def get_stock_indicator_summary_by_code(stock_code: str):
    indicators = get_stock_indicators_by_code(stock_code, limit=120)

    # 如果没有技术指标数据，返回空结果
    if not indicators:
        return None

    # 取最近一个交易日的数据
    latest = indicators[-1]

    close = latest.get("close")
    ma5 = latest.get("ma5")
    ma10 = latest.get("ma10")
    ma20 = latest.get("ma20")

    # 如果均线还没计算出来，说明数据不够
    if close is None or ma5 is None or ma10 is None or ma20 is None:
        return {
            "trade_date": latest.get("trade_date"),
            "close": close,
            "ma5": ma5,
            "ma10": ma10,
            "ma20": ma20,
            "trend": "数据不足",
            "summary": "当前历史数据不足，暂时无法形成完整均线解读。",
            "signals": [],
        }

    signals = []

    # 判断收盘价和均线的位置关系
    if close > ma5:
        signals.append("收盘价在 MA5 上方，短期价格表现较强")
    else:
        signals.append("收盘价在 MA5 下方，短期价格表现偏弱")

    if close > ma20:
        signals.append("收盘价在 MA20 上方，价格仍处于近一个月均价上方")
    else:
        signals.append("收盘价在 MA20 下方，价格低于近一个月均价")

    # 判断均线排列
    if close > ma5 > ma10 > ma20:
        trend = "偏强"
        summary = "当前收盘价高于 MA5、MA10、MA20，且短期均线在中期均线上方，走势相对偏强。"
    elif close < ma5 < ma10 < ma20:
        trend = "偏弱"
        summary = "当前收盘价低于 MA5、MA10、MA20，且短期均线在中期均线下方，走势相对偏弱。"
    elif close > ma20:
        trend = "震荡偏强"
        summary = "当前收盘价位于 MA20 上方，但均线排列不完全强势，说明走势可能处于震荡偏强状态。"
    elif close < ma20:
        trend = "震荡偏弱"
        summary = "当前收盘价位于 MA20 下方，但均线排列不完全弱势，说明走势可能处于震荡偏弱状态。"
    else:
        trend = "震荡"
        summary = "当前价格与均线关系不明显，走势暂时偏震荡。"

    return {
        "trade_date": latest.get("trade_date"),
        "close": close,
        "ma5": ma5,
        "ma10": ma10,
        "ma20": ma20,
        "trend": trend,
        "summary": summary,
        "signals": signals,
    }