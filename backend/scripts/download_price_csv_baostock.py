import json
import os
from datetime import datetime
from pathlib import Path

import baostock as bs
import pandas as pd




# 当前脚本路径：
# backend/scripts/download_price_csv_baostock.py
# parents[2] 可以回到项目根目录 quant-research-copilot
PROJECT_ROOT = Path(__file__).resolve().parents[2]



# 输出目录：data/raw
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw"

# 输出文件：data/raw/daily_price.csv
OUTPUT_FILE = OUTPUT_DIR / "daily_price.csv"

# 临时文件：下载成功后再替换正式 CSV，避免失败时覆盖旧数据
TEMP_OUTPUT_FILE = OUTPUT_DIR / "daily_price_temp.csv"

# 元信息文件：记录 daily_price.csv 是什么时候、通过什么数据源生成的
META_FILE = OUTPUT_DIR / "daily_price_meta.json"
OUTPUT_FILE = OUTPUT_DIR / "daily_price.csv"
TEMP_OUTPUT_FILE = OUTPUT_DIR / "daily_price_temp.csv"
META_FILE = OUTPUT_DIR / "daily_price_meta.json"


# 股票代码列表
# 这里继续使用你项目里已有的 5 只股票
STOCK_CODES = ["000001", "600519", "000858", "600036", "300750"]

# 开始日期
START_DATE = "2026-01-01"

# 结束日期：自动取今天
END_DATE = datetime.now().strftime("%Y-%m-%d")


# 把普通股票代码转换成 BaoStock 要求的格式
# 上海股票一般以 6 开头：sh.600519
# 深圳股票一般以 0 或 3 开头：sz.000001
def convert_to_baostock_code(stock_code: str) -> str:
    if stock_code.startswith("6"):
        return f"sh.{stock_code}"

    return f"sz.{stock_code}"


# 下载单只股票的历史行情
def download_stock_price(stock_code: str) -> pd.DataFrame:
    baostock_code = convert_to_baostock_code(stock_code)

    print(f"正在下载股票：{stock_code}，BaoStock代码：{baostock_code}")

    # BaoStock 历史 K 线接口
    # frequency="d" 表示日线
    # adjustflag="3" 表示不复权
    rs = bs.query_history_k_data_plus(
        baostock_code,
        "date,code,open,high,low,close,preclose,volume,amount,pctChg,turn",
        start_date=START_DATE,
        end_date=END_DATE,
        frequency="d",
        adjustflag="3",
    )

    # 如果接口返回错误，直接抛出异常，让 main 捕获
    if rs.error_code != "0":
        raise RuntimeError(f"BaoStock下载失败：{rs.error_msg}")

    data_list = []

    # BaoStock 需要用 rs.next() 一行一行读取结果
    while rs.next():
        data_list.append(rs.get_row_data())

    df = pd.DataFrame(data_list, columns=rs.fields)

    # 如果没有数据，直接返回空表
    if df.empty:
        return df

    # BaoStock 返回的 code 是 sh.600519 / sz.000001
    # 我们项目里统一使用 600519 / 000001
    df["stock_code"] = df["code"].str[-6:]

    # 字段重命名，统一成我们项目已有的 CSV 字段
    df = df.rename(
        columns={
            "date": "trade_date",
            "pctChg": "change_pct",
            "turn": "turnover_rate",
        }
    )

    # 这些字段从字符串转成数字，方便后端计算
    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "preclose",
        "volume",
        "amount",
        "change_pct",
        "turnover_rate",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    # 涨跌额 = 收盘价 - 前收盘价
    df["change_amount"] = df["close"] - df["preclose"]

    # 振幅 = (最高价 - 最低价) / 前收盘价 * 100
    # 如果前收盘价为空或为 0，就先记为 0，避免除法报错
    df["amplitude"] = 0.0

    valid_preclose = df["preclose"].notna() & (df["preclose"] != 0)

    df.loc[valid_preclose, "amplitude"] = (
        (df.loc[valid_preclose, "high"] - df.loc[valid_preclose, "low"])
        / df.loc[valid_preclose, "preclose"]
        * 100
    )

    # 保留项目目前需要的字段
    result_df = df[
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

    return result_df


# 主函数：批量下载并保存 CSV
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_data = []

    # 登录 BaoStock
    login_result = bs.login()

    print(f"BaoStock登录状态：{login_result.error_code}，{login_result.error_msg}")

    if login_result.error_code != "0":
        print("BaoStock 登录失败，停止下载")
        return

    try:
        for stock_code in STOCK_CODES:
            try:
                stock_df = download_stock_price(stock_code)

                if stock_df.empty:
                    print(f"股票 {stock_code} 没有下载到数据，已跳过")
                    continue

                all_data.append(stock_df)

                print(f"股票 {stock_code} 下载成功，数据行数：{len(stock_df)}")

            except Exception as error:
                print(f"股票 {stock_code} 下载失败：{error}")

        # 如果全部失败，不覆盖原来的 daily_price.csv
        if not all_data:
            print("本次没有下载到任何行情数据，保留原来的 daily_price.csv")
            return

        result_df = pd.concat(all_data, ignore_index=True)

        # 先写临时文件
        result_df.to_csv(TEMP_OUTPUT_FILE, index=False, encoding="utf-8-sig")

        # 临时文件写成功后，再替换正式文件
        os.replace(TEMP_OUTPUT_FILE, OUTPUT_FILE)

        # 写入数据源元信息
        # 这个文件可以让后端知道 daily_price.csv 来自哪个数据源
        meta_data = {
            "source": "BaoStock",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "start_date": START_DATE,
            "end_date": END_DATE,
            "stock_count": len(STOCK_CODES),
            "row_count": len(result_df),
        }

        with open(META_FILE, "w", encoding="utf-8") as meta_file:
            json.dump(meta_data, meta_file, ensure_ascii=False, indent=2)

        print(f"CSV 生成成功：{OUTPUT_FILE}")
        print(f"数据行数：{len(result_df)}")
        print(f"开始日期：{START_DATE}")
        print(f"结束日期：{END_DATE}")

    finally:
        # 无论成功失败，最后都登出
        bs.logout()
        print("BaoStock 已登出")


if __name__ == "__main__":
    main()