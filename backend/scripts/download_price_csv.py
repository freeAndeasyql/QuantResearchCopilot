import os
import time
from datetime import datetime


import akshare as ak
import pandas as pd



# 要下载的股票代码
STOCK_CODES = ["000001", "600519", "000858", "600036", "300750"]


# CSV 保存目录
# 注意：这个路径相对于项目根目录
OUTPUT_DIR = "data/raw"


# CSV 保存文件路径
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "daily_price.csv")


# AKShare 中文字段和项目英文字段的映射
COLUMN_MAP = {
    "日期": "trade_date",
    "股票代码": "stock_code_from_source",
    "开盘": "open",
    "收盘": "close",
    "最高": "high",
    "最低": "low",
    "成交量": "volume",
    "成交额": "amount",
    "振幅": "amplitude",
    "涨跌幅": "change_pct",
    "涨跌额": "change_amount",
    "换手率": "turnover_rate",
}

# 下载起始日期
START_DATE = "20260101"
# 下载结束日期：自动使用今天
END_DATE = datetime.now().strftime("%Y%m%d")
# 下载单只股票的日线行情
def download_stock_price(stock_code: str):
    print(f"正在下载股票：{stock_code}")

    # 调用 AKShare 获取 A 股历史行情
    df = ak.stock_zh_a_hist(
        symbol=stock_code,
        period="daily",
        start_date=START_DATE,
        end_date=END_DATE,
        adjust="",
    )

    # 如果没有下载到数据，直接返回空表
    if df.empty:
        print(f"股票 {stock_code} 没有下载到数据")
        return df

    # 先把 AKShare 返回的中文字段改成项目统一英文字段
    df = df.rename(columns=COLUMN_MAP)

    # 添加项目统一使用的股票代码字段
    df["stock_code"] = stock_code

    # 只保留项目当前需要的字段
    df = df[
        [
            "stock_code",
            "trade_date",
            "open",
            "close",
            "high",
            "low",
            "volume",
            "amount",
            "amplitude",
            "change_pct",
            "change_amount",
            "turnover_rate",
        ]
    ]

    return df


# 主函数：批量下载并保存 CSV
def main():
    # 确保 data/raw 目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_data = []

    for stock_code in STOCK_CODES:
        stock_df = download_stock_price(stock_code)

        if not stock_df.empty:
            all_data.append(stock_df)

        # 稍微暂停，避免请求过快
        time.sleep(0.5)

    # 如果没有下载到任何数据，就不生成 CSV
    if not all_data:
        print("没有下载到任何行情数据")
        return

    # 合并多只股票数据
    result_df = pd.concat(all_data, ignore_index=True)

    # 保存 CSV
    # utf-8-sig 方便 Excel 打开
    result_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

    print(f"CSV 生成成功：{OUTPUT_FILE}")
    print(f"数据行数：{len(result_df)}")


if __name__ == "__main__":
    main()