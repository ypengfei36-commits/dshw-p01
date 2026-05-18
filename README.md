# P01：金融数据获取、管理与初步分析

本项目完成 P01 金融数据作业：获取 A 股个股、市场指数、宏观经济指标和财务指标，完成数据清洗、存储格式对比、描述性统计、可视化、CAPM 回归，并导出独立 HTML 报告。

> 说明：Notebook 默认使用 `akshare` 获取真实数据。如果当前网络或数据源接口临时失败，下载 Notebook 会生成带 `source=simulated_fallback` 标记的替代数据，以保证流程可复现；正式提交前建议在联网环境重新运行 `01_download.ipynb`，确认数据源为 `akshare`。

## 股票列表

| 代码 | 名称 | 行业 | 选股理由 |
|---|---|---|---|
| 000001 | 平安银行 | 银行 | 全国性股份制银行，金融板块代表性强。 |
| 600036 | 招商银行 | 银行 | 零售银行龙头，盈利质量较高，适合与平安银行对比。 |
| 600519 | 贵州茅台 | 白酒 | 白酒行业龙头，消费属性和高盈利能力突出。 |
| 000858 | 五粮液 | 白酒 | 高端白酒代表，可与贵州茅台形成行业内比较。 |
| 002594 | 比亚迪 | 汽车 | 新能源汽车龙头，成长性和市场关注度高。 |
| 601633 | 长城汽车 | 汽车 | 自主品牌车企，覆盖传统车和新能源转型。 |
| 601857 | 中国石油 | 能源 | 能源央企代表，受油价和宏观周期影响明显。 |
| 600900 | 长江电力 | 能源 | 公用事业属性强，现金流稳定，防御性较强。 |
| 600941 | 中国移动 | 通讯 | 通讯运营商龙头，股息和稳健经营特征明显。 |
| 000063 | 中兴通讯 | 通讯 | 通讯设备代表，技术周期和外部环境敏感度较高。 |

## 数据来源

- 股票行情：`akshare.stock_zh_a_hist()`，后复权，日度，时间范围为 2020-01-01 至运行当日。
- 市场指数：`akshare.stock_zh_index_daily_em()`，沪深 300（`000300`）作为 CAPM 市场基准；中证 500（`000905`）作为中盘风格补充。
- 宏观指标：CPI 同比增速（必选）和 M2 同比增速（自选），来源为 `akshare.macro_china_cpi_yearly()` 与 `akshare.macro_china_m2_yearly()`。CPI 反映通胀环境，M2 反映货币流动性，二者都可能影响估值和市场风险偏好。
- 财务数据：`akshare.stock_financial_analysis_indicator()`，提取最近 5 个年度的净资产收益率和资产负债率，并整理为长格式。

## 存储方式

- 基础方式 A：CSV。原始股票、指数、宏观和财务数据分别保存在 `data/stock/`、`data/index/`、`data/macro/`、`data/finance/`，合并数据保存为 `data/combined/combined_data.csv`。
- 进阶方式 B：Parquet。清洗后的股票数据额外保存为 `data/clean/stock_clean.parquet`，并在 `02_clean.ipynb` 中展示列式读取、Schema、读取速度和文件体积对比。
- CSV 的优点是通用、可读、便于提交和检查；缺点是缺少类型契约、体积较大、按列读取效率较低。Parquet 更适合列式分析、大数据量和需要保留字段类型的场景。

## GitHub 仓库

请在个人 GitHub 下创建公开仓库并替换为你的实际链接：

`https://github.com/ypengfei36-commits/dshw-p01`

## Quarto 电子书

完成 GitHub Pages 发布后，将链接替换为：

`https://ypengfei36-commits.github.io/dshw-p01/`

## 如何运行

1. 安装依赖：`pip install -r requirements.txt`
2. 运行 `01_download.ipynb` 下载原始数据，并自动创建目录结构。
3. 运行 `02_clean.ipynb` 清洗、合并并保存 CSV 与 Parquet。
4. 运行 `03_analysis.ipynb` 生成统计表、图形和 CAPM 回归结果。
5. 导出报告：`python -m nbconvert --to html 03_analysis.ipynb --output report.html`
6. 渲染 Quarto：`quarto render`

如 Notebook 内核遇到网络代理问题，也可先运行 `python scripts/download_data.py` 重新下载原始数据，再运行第 2、3 个 Notebook。

## 目录结构

```text
dshw-p01/
├── README.md
├── report.html
├── requirements.txt
├── .gitignore
├── 01_download.ipynb
├── 02_clean.ipynb
├── 03_analysis.ipynb
├── data/
│   ├── stock/
│   ├── index/
│   ├── macro/
│   ├── finance/
│   ├── clean/
│   └── combined/
├── output/
└── download_log.txt
```
