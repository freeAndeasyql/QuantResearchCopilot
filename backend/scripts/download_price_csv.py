import os
import time
from datetime import datetime

import pandas as pd
import requests

# 清理终端里的代理环境变量
# 这些变量如果存在，requests 会自动走代理
for proxy_key in [
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "http_proxy",
    "https_proxy",
    "ALL_PROXY",
    "all_proxy",
]:
    os.environ.pop(proxy_key, None)

# 明确告诉程序：所有地址都不要走代理
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

# 创建一个专用 session
# trust_env = False 表示不要读取系统代理、终端代理、conda 代理等环境配置
_no_proxy_session = requests.Session()
_no_proxy_session.trust_env = False

# 替换 requests.get
# 因为 AKShare 内部也是调用 requests.get
# 所以我们在 import akshare 之前先把 requests.get 改掉
def safe_get(url, *args, **kwargs):
    headers = kwargs.pop("headers", {}) or {}

    headers.update(
        {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://quote.eastmoney.com/",
            "Connection": "close",
        }
    )

    kwargs["headers"] = headers
    kwargs["timeout"] = kwargs.get("timeout", 20)

    # 关键：强制不使用任何代理
    kwargs["proxies"] = {
        "http": None,
        "https": None,
    }

    return _no_proxy_session.get(url, *args, **kwargs)


requests.get = safe_get

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
# 主函数：批量下载股票行情并保存 CSV
def main():
    # 确保 data/raw 目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 用来保存所有成功下载的股票数据
    all_data = []

    for stock_code in STOCK_CODES:
        # 先准备一个空 DataFrame
        # 如果后面下载失败，就保持为空
        stock_df = pd.DataFrame()

        # 每只股票最多重试 3 次
        for retry_index in range(3):
            try:
                stock_df = download_stock_price(stock_code)

                # 如果成功下载，就跳出重试循环
                break

            except Exception as error:
                # 捕获 AKShare / requests / 东方财富连接错误
                # 这里不要让整个脚本崩掉
                print(f"股票 {stock_code} 第 {retry_index + 1} 次下载失败：{error}")

                # 失败后等 2 秒再重试
                time.sleep(2)

        # 如果这只股票最终下载成功，就加入总数据
        if not stock_df.empty:
            all_data.append(stock_df)
            print(f"股票 {stock_code} 下载成功，数据行数：{len(stock_df)}")
        else:
            print(f"股票 {stock_code} 最终下载失败，已跳过")

        # 每只股票之间暂停一下，避免请求过快
        time.sleep(1)

    # 如果所有股票都下载失败，不覆盖旧的 daily_price.csv
    if not all_data:
        print("本次没有下载到任何行情数据，保留原来的 daily_price.csv")
        return

    # 合并多只股票数据
    result_df = pd.concat(all_data, ignore_index=True)

    # 先写入临时文件
    temp_output_file = os.path.join(OUTPUT_DIR, "daily_price_temp.csv")
    result_df.to_csv(temp_output_file, index=False, encoding="utf-8-sig")

    # 临时文件写成功后，再替换正式 CSV
    os.replace(temp_output_file, OUTPUT_FILE)

    print(f"CSV 生成成功：{OUTPUT_FILE}")
    print(f"数据行数：{len(result_df)}")


if __name__ == "__main__":
    main()