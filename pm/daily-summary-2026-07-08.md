# 2026-07-08 学习总结

## 今日主题

数据质量报告完善、行情数据下载问题排查、后端服务入口修复与备用数据源方案设计。

## 今日完成内容

1. 完成数据质量整体结论功能。
   - 后端 `/api/data/quality` 返回 `status`、`level`、`summary`。
   - 前端状态页展示数据质量整体结论。

2. 完成数据质量 Markdown 报告功能。
   - 新增后端接口 `/api/data/quality/report`。
   - 返回 Markdown 格式的数据质量报告。
   - 前端状态页可以生成并展示 Markdown 报告。

3. 修复后端服务入口文件 `backend/main.py`。
   - 删除误放在 `main.py` 里的 CSV 下载逻辑。
   - 保持 `main.py` 只负责 FastAPI 接口。
   - 修复 `HttpException` 拼写错误，改为 `raise HTTPException`。
   - 后端 `/api/health` 恢复正常。

4. 排查 AKShare / 东方财富行情下载失败问题。
   - 遇到 `ProxyError`，判断为请求仍然走了不可用代理。
   - 尝试清理代理环境变量。
   - 强制 `requests` 不走代理。
   - 代理问题解决后，错误变为 `RemoteDisconnected`。
   - 判断当前问题主要是东方财富接口连接不稳定。

5. 明确数据源方案。
   - 短期继续使用已有 `daily_price.csv`。
   - 不让下载失败影响已有项目功能。
   - 中期新增 BaoStock 备用下载脚本。
   - 后端和前端继续读取同一个 `daily_price.csv`，不需要大改业务代码。

6. 开始增加行情数据源元信息。
   - 设计新增 `data/raw/daily_price_meta.json`。
   - 用于记录数据来源、更新时间、起止日期、股票数量、数据行数。
   - 遇到 `NameError: name 'OUTPUT_DIR' is not defined`。
   - 原因是 `META_FILE` 写在了 `OUTPUT_DIR` 定义之前。
   - 已明确修复顺序：先定义 `PROJECT_ROOT`，再定义 `OUTPUT_DIR`，最后定义 `META_FILE`。

## 今日理解内容

1. `backend/main.py` 是后端服务入口，只应该放接口代码。
2. CSV 下载逻辑应该放在 `backend/scripts/` 目录下的脚本文件中。
3. `if __name__ == "__main__": main()` 适合放在独立脚本里，不适合随便放进 FastAPI 服务文件。
4. `ProxyError` 说明请求走了代理，并且代理不可用。
5. `RemoteDisconnected` 说明远端服务器主动断开连接，不一定是代码写错。
6. 一个稳定的数据系统不能只依赖单一数据源。
7. 下载脚本应该做到：
   - 失败不崩溃；
   - 失败不覆盖旧 CSV；
   - 单只股票失败可以跳过；
   - 后续可以支持备用数据源。
8. Python 是从上往下一行一行执行的，所以变量必须先定义再使用。

## 遇到的问题

1. AKShare 请求东方财富接口不稳定。
2. 代理环境导致请求失败。
3. 东方财富接口出现远端主动断开连接。
4. 下载脚本和后端服务入口文件一度混在一起。
5. `META_FILE` 定义顺序错误导致 `NameError`。

## 当前项目进展

项目目前已经具备：

1. Vue3 + FastAPI 前后端联调。
2. 股票列表、搜索、行业筛选、分页。
3. 股票详情。
4. CSV 行情数据读取。
5. 历史价格走势图。
6. 收益指标计算。
7. 数据状态检查。
8. 数据质量检查。
9. 数据质量整体结论。
10. 数据质量 Markdown 报告。
11. 后端统一响应格式。
12. 后端异常统一处理。
13. 初步具备多数据源容错设计思路。

## 下一步计划

1. 完成 BaoStock 备用行情下载脚本。
2. 成功生成新的 `daily_price.csv`。
3. 生成 `daily_price_meta.json` 数据源元信息文件。
4. 把数据源元信息接入 `/api/data/status`。
5. 前端状态页展示当前数据源、更新时间、起止日期和数据行数。
6. 后续再给 Markdown 报告增加复制按钮。
