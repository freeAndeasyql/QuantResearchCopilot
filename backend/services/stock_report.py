from typing import Any, Dict


# 安全读取字典字段
# 当字段不存在或数据为空时，返回默认值
def get_value(data: Dict[str, Any], key: str, default=None):
    if not data:
        return default

    return data.get(key, default)


# 格式化数字
# 例如 12.3456 -> 12.35
def format_number(value, digits: int = 2) -> str:
    if value is None:
        return "暂无"

    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


# 格式化百分比
# 正数自动增加加号
def format_percentage(value) -> str:
    if value is None:
        return "暂无"

    try:
        number = float(value)
        prefix = "+" if number > 0 else ""

        return f"{prefix}{number:.2f}%"
    except (TypeError, ValueError):
        return str(value)


# 格式化评分
# 正分自动增加加号
def format_score(score) -> str:
    if score is None:
        return "0"

    try:
        number = int(score)
        prefix = "+" if number > 0 else ""

        return f"{prefix}{number}"
    except (TypeError, ValueError):
        return str(score)


# 将字符串列表转换成 Markdown 列表
def build_markdown_list(items, empty_text: str) -> str:
    if not items:
        return f"- {empty_text}"

    return "\n".join(f"- {item}" for item in items)


# 生成股票研究 Markdown 报告
def generate_stock_analysis_report(
    stock: Dict[str, Any],
    analysis: Dict[str, Any],
) -> str:
    # 股票基本信息
    stock_code = stock.get("code", "")
    stock_name = stock.get("name", "")
    industry = stock.get("industry", "暂无")

    # 综合分析信息
    trade_date = analysis.get("trade_date", "暂无")
    overall_view = analysis.get("overall_view", "暂无")
    total_score = analysis.get("score", 0)
    summary = analysis.get("summary", "暂无综合分析结论。")
    disclaimer = analysis.get(
        "disclaimer",
        "本报告仅用于学习和辅助观察，不构成投资建议。",
    )

    # 积极信号和风险提示
    highlights_markdown = build_markdown_list(
        analysis.get("highlights", []),
        "当前暂未识别出特别明显的积极信号。",
    )

    risks_markdown = build_markdown_list(
        analysis.get("risks", []),
        "当前暂未识别出特别明显的风险信号。",
    )

    # 三个分析维度的完整数据
    dimensions = analysis.get("dimensions", {})

    metrics = dimensions.get("metrics") or {}
    indicator_summary = dimensions.get("indicator_summary") or {}
    volume_summary = dimensions.get("volume_summary") or {}

    # 收益指标
    period_days = get_value(metrics, "period_days", "暂无")
    period_return = format_percentage(
        get_value(metrics, "period_return")
    )
    latest_close = format_number(
        get_value(metrics, "latest_close")
    )
    previous_close = format_number(
        get_value(metrics, "previous_close")
    )
    change_amount = format_number(
        get_value(metrics, "change_amount")
    )
    change_pct = format_percentage(
        get_value(metrics, "change_pct")
    )

    # 均线指标
    indicator_trend = get_value(
        indicator_summary,
        "trend",
        "暂无",
    )
    indicator_text = get_value(
        indicator_summary,
        "summary",
        "暂无均线解读。",
    )

    ma5 = format_number(get_value(indicator_summary, "ma5"))
    ma10 = format_number(get_value(indicator_summary, "ma10"))
    ma20 = format_number(get_value(indicator_summary, "ma20"))

    indicator_signals_markdown = build_markdown_list(
        indicator_summary.get("signals", []),
        "暂无均线关键信号。",
    )

    # 成交量指标
    volume_signal = get_value(
        volume_summary,
        "signal",
        "暂无",
    )
    volume_text = get_value(
        volume_summary,
        "summary",
        "暂无成交量解读。",
    )

    price_status = get_value(
        volume_summary,
        "price_status",
        "暂无",
    )
    volume_status = get_value(
        volume_summary,
        "volume_status",
        "暂无",
    )

    latest_volume = format_number(
        get_value(volume_summary, "latest_volume"),
        digits=0,
    )
    average_volume_5d = format_number(
        get_value(volume_summary, "average_volume_5d"),
        digits=0,
    )
    volume_ratio = format_number(
        get_value(volume_summary, "volume_ratio"),
    )

    # 评分依据表格
    score_rows = []

    for item in analysis.get("score_details", []):
        dimension = item.get("dimension", "暂无")
        value = item.get("value")

        # 区间收益需要显示百分号
        if dimension == "区间收益":
            display_value = format_percentage(value)
        else:
            display_value = "暂无" if value is None else str(value)

        score_rows.append(
            f"| {dimension} | {display_value} | "
            f"{format_score(item.get('score', 0))} |"
        )

    score_table = (
        "\n".join(score_rows)
        if score_rows
        else "| 暂无 | 暂无 | 0 |"
    )

    report = f"""# 股票研究报告

## 一、股票基本信息

| 项目 | 内容 |
|---|---|
| 股票名称 | {stock_name} |
| 股票代码 | {stock_code} |
| 所属行业 | {industry} |
| 分析日期 | {trade_date} |

## 二、综合观察

**综合观点：{overall_view}**

**综合评分：{format_score(total_score)} 分**

{summary}

## 三、评分依据

| 分析维度 | 当前状态 | 得分 |
|---|---|---:|
{score_table}

## 四、近期收益表现

| 指标 | 数值 |
|---|---:|
| 最新收盘价 | {latest_close} |
| 前一交易日收盘价 | {previous_close} |
| 当日涨跌额 | {change_amount} |
| 当日涨跌幅 | {change_pct} |
| 统计区间 | 最近 {period_days} 个交易日 |
| 区间收益率 | {period_return} |

## 五、均线趋势分析

**趋势判断：{indicator_trend}**

{indicator_text}

### 均线数值

| 指标 | 数值 |
|---|---:|
| MA5 | {ma5} |
| MA10 | {ma10} |
| MA20 | {ma20} |

### 均线关键信号

{indicator_signals_markdown}

## 六、成交量与量价关系

**量价信号：{volume_signal}**

{volume_text}

| 指标 | 数值 |
|---|---:|
| 价格状态 | {price_status} |
| 成交量状态 | {volume_status} |
| 最新成交量 | {latest_volume} |
| 前 5 日平均成交量 | {average_volume_5d} |
| 成交量比值 | {volume_ratio} 倍 |

## 七、积极信号

{highlights_markdown}

## 八、风险提示

{risks_markdown}

## 九、分析说明

本报告当前采用规则分析方式生成，主要依据：

1. 最近 30 个交易日的区间收益；
2. 收盘价与 MA5、MA10、MA20 的位置关系；
3. 最新成交量与前 5 个交易日平均成交量的关系；
4. 项目内部定义的基础评分规则。

## 十、免责声明

{disclaimer}
"""

    return report