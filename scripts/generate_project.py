from __future__ import annotations

import json
import textwrap
from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]


def dedent(text: str) -> str:
    return textwrap.dedent(text).strip() + "\n"


def md(text: str):
    return nbf.v4.new_markdown_cell(dedent(text))


def code(text: str):
    return nbf.v4.new_code_cell(dedent(text))


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content), encoding="utf-8")


def write_notebook(path: Path, cells: list) -> None:
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "pygments_lexer": "ipython3",
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, path)


README = r"""
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

`https://github.com/[你的用户名]/dshw-p01`

## Quarto 电子书

完成 GitHub Pages 发布后，将链接替换为：

`https://[你的用户名].github.io/dshw-p01/`

## 如何运行

1. 安装依赖：`pip install -r requirements.txt`
2. 运行 `01_download.ipynb` 下载原始数据，并自动创建目录结构。
3. 运行 `02_clean.ipynb` 清洗、合并并保存 CSV 与 Parquet。
4. 运行 `03_analysis.ipynb` 生成统计表、图形和 CAPM 回归结果。
5. 导出报告：`python -m nbconvert --to html 03_analysis.ipynb --output report.html`
6. 渲染 Quarto：`quarto render`

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
"""


REQS = r"""
akshare>=1.18.0
pandas>=2.2.0
numpy>=1.26.0
matplotlib>=3.8.0
seaborn>=0.13.0
scipy>=1.11.0
statsmodels>=0.14.0
pyarrow>=15.0.0
nbformat>=5.10.0
nbclient>=0.10.0
nbconvert>=7.16.0
ipykernel>=6.29.0
"""


GITIGNORE = r"""
# Raw data can be rebuilt by running 01_download.ipynb
data/stock/
data/index/
data/macro/
data/finance/

# Database files, if SQLite is added later
*.db

# Notebook/runtime cache
.ipynb_checkpoints/
__pycache__/

# System files
.DS_Store
Thumbs.db
"""


QUARTO = r"""
project:
  type: book
  output-dir: docs

book:
  title: "P01 金融数据获取、管理与初步分析"
  author: "请替换为你的姓名"
  chapters:
    - index.qmd

format:
  html:
    theme: cosmo
    toc: true
    number-sections: true
    self-contained: false
"""


INDEX_QMD = r"""
# 项目概览

本电子书整理 P01 金融数据作业的主要流程和结论。完整代码见三个 Notebook，独立分析报告见 [`report.html`](report.html)。

## 数据与方法

- 数据范围：2020-01-01 至运行当日。
- 个股范围：10 只 A 股，覆盖银行、白酒、汽车、能源、通讯 5 个行业。
- 市场基准：沪深 300。
- 宏观变量：CPI 同比增速、M2 同比增速。
- 存储方式：CSV 作为基础格式，Parquet 作为进阶格式。

## 关键输出

统计表、图形和回归结果由 `03_analysis.ipynb` 生成，图形统一保存到 `output/`。

![](output/fig1_normalized_prices.png)

![](output/fig3_return_correlation_heatmap.png)

![](output/fig6_capm_beta.png)

## 运行顺序

```bash
pip install -r requirements.txt
jupyter notebook 01_download.ipynb
jupyter notebook 02_clean.ipynb
jupyter notebook 03_analysis.ipynb
python -m nbconvert --to html 03_analysis.ipynb --output report.html
quarto render
```
"""


WORKFLOW = r"""
name: Render Quarto Book

on:
  push:
    branches: [main, master]
  workflow_dispatch:

permissions:
  contents: write

jobs:
  render:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: quarto-dev/quarto-actions/setup@v2
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Render
        run: quarto render
      - name: Upload docs artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs
"""


RUN_NOTEBOOKS = r"""
from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ["01_download.ipynb", "02_clean.ipynb", "03_analysis.ipynb"]


for name in NOTEBOOKS:
    path = ROOT / name
    print(f"Executing {name} ...")
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(
        nb,
        timeout=900,
        kernel_name="python3",
        resources={"metadata": {"path": str(ROOT)}},
        allow_errors=False,
    )
    client.execute()
    nbformat.write(nb, path)
    print(f"Finished {name}")
"""


EXPORT_REPORT = r"""
from __future__ import annotations

from pathlib import Path

import nbformat
from nbconvert import HTMLExporter


ROOT = Path(__file__).resolve().parents[1]
nb = nbformat.read(ROOT / "03_analysis.ipynb", as_version=4)
html, _ = HTMLExporter().from_notebook_node(nb)
(ROOT / "report.html").write_text(html, encoding="utf-8")
print("Wrote report.html")
"""


NOTEBOOK_01 = [
    md(
        """
        # 01 数据下载

        本 Notebook 完成项目目录创建和四类数据获取：个股行情、市场指数、宏观指标、财务指标。所有下载动作都会写入 `download_log.txt`，便于复现和排错。
        """
    ),
    code(
        r"""
        from pathlib import Path
        from datetime import datetime
        import os
        import time

        import numpy as np
        import pandas as pd

        try:
            import akshare as ak
        except Exception as exc:
            ak = None
            print(f"akshare 不可用，将使用 fallback 数据：{exc}")

        ROOT = Path.cwd()
        START_DATE = "2020-01-01"
        END_DATE = pd.Timestamp.today().normalize()
        END_DATE_STR = END_DATE.strftime("%Y%m%d")

        DIRS = [
            "data/stock", "data/index", "data/macro", "data/finance",
            "data/clean", "data/combined", "output"
        ]
        for directory in DIRS:
            os.makedirs(ROOT / directory, exist_ok=True)

        LOG_PATH = ROOT / "download_log.txt"
        LOG_PATH.write_text("", encoding="utf-8")

        print(f"Project root: {ROOT}")
        print(f"Data window: {START_DATE} to {END_DATE.date()}")
        """
    ),
    md(
        """
        ## 股票池

        按作业要求选择 10 只 A 股，覆盖 5 个行业，每个行业 2 只。选择逻辑同时考虑行业代表性和后续 CAPM/行业比较的可解释性。
        """
    ),
    code(
        r"""
        STOCKS = [
            {"code": "000001", "name": "平安银行", "industry": "银行", "reason": "全国性股份制银行，金融板块代表性强。"},
            {"code": "600036", "name": "招商银行", "industry": "银行", "reason": "零售银行龙头，盈利质量较高。"},
            {"code": "600519", "name": "贵州茅台", "industry": "白酒", "reason": "白酒行业龙头，消费属性突出。"},
            {"code": "000858", "name": "五粮液", "industry": "白酒", "reason": "高端白酒代表，适合行业内比较。"},
            {"code": "002594", "name": "比亚迪", "industry": "汽车", "reason": "新能源汽车龙头，成长性强。"},
            {"code": "601633", "name": "长城汽车", "industry": "汽车", "reason": "自主品牌车企，处于新能源转型阶段。"},
            {"code": "601857", "name": "中国石油", "industry": "能源", "reason": "能源央企代表，受油价和周期影响。"},
            {"code": "600900", "name": "长江电力", "industry": "能源", "reason": "现金流稳定，防御属性较强。"},
            {"code": "600941", "name": "中国移动", "industry": "通讯", "reason": "通讯运营商龙头，稳健和高股息特征明显。"},
            {"code": "000063", "name": "中兴通讯", "industry": "通讯", "reason": "通讯设备代表，技术周期敏感。"},
        ]

        INDEXES = [
            {"code": "000300", "ak_symbol": "sh000300", "name": "沪深300", "role": "CAPM 市场基准"},
            {"code": "000905", "ak_symbol": "sh000905", "name": "中证500", "role": "中盘风格补充"},
        ]

        stock_info = pd.DataFrame(STOCKS)
        stock_info.to_csv(ROOT / "data/stock_list.csv", index=False, encoding="utf-8-sig")
        stock_info
        """
    ),
    md(
        """
        ## 下载工具函数

        函数会优先调用 `akshare`。若网络/API 失败，fallback 数据会显式写入 `source=simulated_fallback`，便于后续检查。
        """
    ),
    code(
        r"""
        def log_event(status: str, item: str, message: str) -> None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            line = f"[{timestamp}] {status:<7} {item:<18} {message}\n"
            with LOG_PATH.open("a", encoding="utf-8") as fh:
                fh.write(line)
            print(line, end="")


        def standardize_ohlcv(df: pd.DataFrame, code: str, name: str, source: str) -> pd.DataFrame:
            rename_map = {
                "日期": "date", "股票代码": "code", "开盘": "open", "开盘价": "open",
                "收盘": "close", "收盘价": "close", "最高": "high", "最高价": "high",
                "最低": "low", "最低价": "low", "成交量": "volume", "成交额": "amount",
            }
            out = df.rename(columns=rename_map).copy()
            required = ["date", "open", "close", "high", "low", "volume", "amount"]
            missing = [col for col in required if col not in out.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}; got {list(df.columns)}")
            out = out[required].copy()
            out["date"] = pd.to_datetime(out["date"])
            out["code"] = code
            out["name"] = name
            out["source"] = source
            for col in ["open", "close", "high", "low", "volume", "amount"]:
                out[col] = pd.to_numeric(out[col], errors="coerce")
            return out[["date", "code", "name", "open", "close", "high", "low", "volume", "amount", "source"]]


        def simulate_ohlcv(code: str, name: str, start: str, end: pd.Timestamp, base: float = 30, beta: float = 1.0) -> pd.DataFrame:
            dates = pd.bdate_range(start=start, end=end)
            seed = int(code) % (2**32 - 1)
            rng = np.random.default_rng(seed)
            n = len(dates)
            market = rng.normal(0.00015, 0.011, n)
            idio = rng.normal(0, 0.012, n)
            returns = 0.00012 + beta * market + idio
            close = base * np.exp(np.cumsum(returns))
            open_ = close * np.exp(rng.normal(0, 0.004, n))
            high = np.maximum(open_, close) * (1 + rng.uniform(0.001, 0.025, n))
            low = np.minimum(open_, close) * (1 - rng.uniform(0.001, 0.025, n))
            volume = rng.integers(200_000, 5_000_000, n)
            amount = volume * close * 100
            return pd.DataFrame({
                "date": dates, "code": code, "name": name, "open": open_,
                "close": close, "high": high, "low": low,
                "volume": volume, "amount": amount, "source": "simulated_fallback",
            })


        def fetch_stock(row: dict) -> pd.DataFrame:
            code = row["code"]
            name = row["name"]
            industry_beta = {"银行": 0.9, "白酒": 0.85, "汽车": 1.25, "能源": 0.95, "通讯": 1.15}
            try:
                if ak is None:
                    raise RuntimeError("akshare not imported")
                raw = ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=START_DATE.replace("-", ""),
                    end_date=END_DATE_STR,
                    adjust="hfq",
                )
                data = standardize_ohlcv(raw, code, name, "akshare")
                if data.empty:
                    raise ValueError("No data returned")
                log_event("SUCCESS", f"stock_{code}", f"shape={data.shape}")
                return data
            except Exception as exc:
                data = simulate_ohlcv(
                    code, name, START_DATE, END_DATE,
                    base=20 + (int(code[-2:]) % 60),
                    beta=industry_beta.get(row["industry"], 1.0),
                )
                log_event("FAILED", f"stock_{code}", f"{type(exc).__name__}: {exc}; fallback shape={data.shape}")
                return data
        """
    ),
    md(
        """
        ## 下载 10 只股票后复权日度行情
        """
    ),
    code(
        r"""
        stock_frames = []
        for row in STOCKS:
            df = fetch_stock(row)
            stock_frames.append(df)
            df.to_csv(ROOT / f"data/stock/stock_{row['code']}.csv", index=False, encoding="utf-8-sig")
            time.sleep(0.2)

        pd.concat(stock_frames, ignore_index=True).head()
        """
    ),
    md(
        """
        ## 下载市场指数

        沪深 300 用于 CAPM 市场组合，中证 500 用于和中盘风格进行补充对比。
        """
    ),
    code(
        r"""
        def fetch_index(item: dict) -> pd.DataFrame:
            try:
                if ak is None:
                    raise RuntimeError("akshare not imported")
                raw = ak.stock_zh_index_daily_em(symbol=item["ak_symbol"])
                raw = raw.rename(columns={"date": "date", "open": "open", "close": "close", "high": "high", "low": "low", "volume": "volume", "amount": "amount"})
                raw["date"] = pd.to_datetime(raw["date"])
                raw = raw[(raw["date"] >= START_DATE) & (raw["date"] <= END_DATE)]
                out = raw[["date", "open", "close", "high", "low", "volume", "amount"]].copy()
                out["code"] = item["code"]
                out["name"] = item["name"]
                out["source"] = "akshare"
                out = out[["date", "code", "name", "open", "close", "high", "low", "volume", "amount", "source"]]
                if out.empty:
                    raise ValueError("No data returned")
                log_event("SUCCESS", f"index_{item['code']}", f"shape={out.shape}")
                return out
            except Exception as exc:
                out = simulate_ohlcv(item["code"], item["name"], START_DATE, END_DATE, base=4000, beta=1.0)
                log_event("FAILED", f"index_{item['code']}", f"{type(exc).__name__}: {exc}; fallback shape={out.shape}")
                return out


        index_frames = []
        for item in INDEXES:
            df = fetch_index(item)
            index_frames.append(df)
            df.to_csv(ROOT / f"data/index/index_{item['code']}.csv", index=False, encoding="utf-8-sig")
            time.sleep(0.2)

        pd.concat(index_frames, ignore_index=True).head()
        """
    ),
    md(
        """
        ## 下载宏观指标

        CPI 反映通胀环境，M2 反映流动性环境。后续清洗时会将月度数据映射到对应月份的交易日。
        """
    ),
    code(
        r"""
        def standardize_macro(raw: pd.DataFrame, indicator: str, source: str) -> pd.DataFrame:
            out = raw.rename(columns={"日期": "date", "今值": "value"}).copy()
            if "date" not in out.columns or "value" not in out.columns:
                raise ValueError(f"Unexpected macro columns: {list(raw.columns)}")
            out = out[["date", "value"]].copy()
            out["date"] = pd.to_datetime(out["date"])
            out["value"] = pd.to_numeric(out["value"], errors="coerce")
            out = out[out["date"] >= START_DATE].dropna(subset=["value"])
            out["indicator"] = indicator
            out["source"] = source
            return out[["date", "indicator", "value", "source"]]


        def simulate_macro(indicator: str) -> pd.DataFrame:
            dates = pd.date_range(START_DATE, END_DATE, freq="MS")
            rng = np.random.default_rng(abs(hash(indicator)) % (2**32 - 1))
            base = 1.5 if indicator == "cpi" else 8.5
            values = base + np.cumsum(rng.normal(0, 0.08, len(dates)))
            return pd.DataFrame({"date": dates, "indicator": indicator, "value": values, "source": "simulated_fallback"})


        macro_specs = [
            ("cpi", "macro_china_cpi_yearly"),
            ("m2", "macro_china_m2_yearly"),
        ]

        macro_frames = []
        for indicator, func_name in macro_specs:
            try:
                if ak is None:
                    raise RuntimeError("akshare not imported")
                raw = getattr(ak, func_name)()
                df = standardize_macro(raw, indicator, "akshare")
                if df.empty:
                    raise ValueError("No data returned")
                log_event("SUCCESS", f"macro_{indicator}", f"shape={df.shape}")
            except Exception as exc:
                df = simulate_macro(indicator)
                log_event("FAILED", f"macro_{indicator}", f"{type(exc).__name__}: {exc}; fallback shape={df.shape}")
            macro_frames.append(df)
            df.to_csv(ROOT / f"data/macro/macro_{indicator}.csv", index=False, encoding="utf-8-sig")
            time.sleep(0.2)

        macro_data = pd.concat(macro_frames, ignore_index=True)
        macro_data.head()
        """
    ),
    md(
        """
        ## 下载财务指标

        财务数据整理为长格式：每行是一只股票某年度某指标的观测值。
        """
    ),
    code(
        r"""
        def simulate_finance(row: dict) -> pd.DataFrame:
            years = list(range(max(2020, END_DATE.year - 5), END_DATE.year))
            rng = np.random.default_rng(int(row["code"]) % (2**32 - 1))
            industry_roe = {"银行": 10, "白酒": 22, "汽车": 8, "能源": 9, "通讯": 11}
            records = []
            for year in years[-5:]:
                roe = industry_roe.get(row["industry"], 10) + rng.normal(0, 2)
                debt = {"银行": 91, "白酒": 28, "汽车": 60, "能源": 52, "通讯": 42}.get(row["industry"], 50) + rng.normal(0, 4)
                records.extend([
                    {"code": row["code"], "name": row["name"], "industry": row["industry"], "year": year, "indicator": "roe", "value": roe, "source": "simulated_fallback"},
                    {"code": row["code"], "name": row["name"], "industry": row["industry"], "year": year, "indicator": "debt_to_asset", "value": debt, "source": "simulated_fallback"},
                ])
            return pd.DataFrame(records)


        def fetch_finance(row: dict) -> pd.DataFrame:
            try:
                if ak is None:
                    raise RuntimeError("akshare not imported")
                raw = ak.stock_financial_analysis_indicator(symbol=row["code"], start_year="2020")
                if raw.empty:
                    raise ValueError("No data returned")
                raw["date"] = pd.to_datetime(raw["日期"])
                annual = raw[raw["date"].dt.month == 12].copy()
                if annual.empty:
                    annual = raw.sort_values("date").groupby(raw["date"].dt.year).tail(1).copy()
                annual["year"] = annual["date"].dt.year
                annual = annual.sort_values("year").tail(5)

                metric_candidates = {
                    "roe": ["净资产收益率(%)", "加权净资产收益率(%)"],
                    "debt_to_asset": ["资产负债率(%)"],
                }
                records = []
                for _, item in annual.iterrows():
                    for indicator, candidates in metric_candidates.items():
                        col = next((c for c in candidates if c in annual.columns), None)
                        if col is None:
                            continue
                        value = pd.to_numeric(item[col], errors="coerce")
                        if pd.notna(value):
                            records.append({
                                "code": row["code"], "name": row["name"], "industry": row["industry"],
                                "year": int(item["year"]), "indicator": indicator, "value": float(value),
                                "source": "akshare",
                            })
                out = pd.DataFrame(records)
                if out.empty:
                    raise ValueError("No usable finance metrics")
                log_event("SUCCESS", f"finance_{row['code']}", f"shape={out.shape}")
                return out
            except Exception as exc:
                out = simulate_finance(row)
                log_event("FAILED", f"finance_{row['code']}", f"{type(exc).__name__}: {exc}; fallback shape={out.shape}")
                return out


        finance_frames = []
        for row in STOCKS:
            finance_frames.append(fetch_finance(row))
            time.sleep(0.2)

        finance_data = pd.concat(finance_frames, ignore_index=True)
        finance_data.to_csv(ROOT / "data/finance/finance_ratios.csv", index=False, encoding="utf-8-sig")
        finance_data.head(12)
        """
    ),
    md(
        """
        ## 下载结果检查

        若 `source` 出现 `simulated_fallback`，说明对应接口在本次运行中不可用。正式提交前可联网重新运行本 Notebook。
        """
    ),
    code(
        r"""
        summary = {
            "stock_files": len(list((ROOT / "data/stock").glob("stock_*.csv"))),
            "index_files": len(list((ROOT / "data/index").glob("index_*.csv"))),
            "macro_files": len(list((ROOT / "data/macro").glob("macro_*.csv"))),
            "finance_rows": len(finance_data),
        }
        print(summary)
        print(LOG_PATH.read_text(encoding="utf-8"))
        """
    ),
]


NOTEBOOK_02 = [
    md(
        """
        # 02 数据清洗与存储管理

        本 Notebook 完成单表清洗、宽表/长表转换、多表合并，并额外保存 Parquet 格式用于和 CSV 对比。
        """
    ),
    code(
        r"""
        from pathlib import Path
        import os
        import time

        import numpy as np
        import pandas as pd
        import pyarrow.parquet as pq

        ROOT = Path.cwd()
        for directory in ["data/clean", "data/combined", "output"]:
            os.makedirs(ROOT / directory, exist_ok=True)

        stock_info = pd.read_csv(ROOT / "data/stock_list.csv")
        stock_info
        """
    ),
    md(
        """
        ## 3.1 单表清洗

        对每只股票分别检查缺失值、日期格式、数值类型、重复记录，并标注单日收益率超过 ±20% 的极端波动。
        """
    ),
    code(
        r"""
        def missing_profile(df: pd.DataFrame, code: str) -> pd.DataFrame:
            return pd.DataFrame({
                "code": code,
                "column": df.columns,
                "missing_count": df.isna().sum().values,
                "missing_pct": (df.isna().mean().values * 100).round(4),
            })


        def clean_stock_file(path: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
            code = path.stem.replace("stock_", "")
            raw = pd.read_csv(path)
            before_rows = len(raw)
            missing = missing_profile(raw, code)

            df = raw.copy()
            df["date"] = pd.to_datetime(df["date"])
            numeric_cols = ["open", "close", "high", "low", "volume", "amount"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            duplicate_count = df.duplicated(subset=["date", "code"]).sum()
            df = df.drop_duplicates(subset=["date", "code"], keep="last").sort_values("date")
            df[numeric_cols] = df[numeric_cols].ffill()
            df["return"] = np.log(df["close"] / df["close"].shift(1))
            df["is_extreme"] = df["return"].abs() > 0.20
            df = df.merge(stock_info[["code", "industry"]], on="code", how="left")
            audit = {
                "code": code,
                "before_rows": before_rows,
                "after_rows": len(df),
                "duplicates_removed": int(duplicate_count),
                "extreme_rows": int(df["is_extreme"].sum()),
            }
            return df, missing, audit


        clean_frames = []
        missing_frames = []
        audit_records = []

        for path in sorted((ROOT / "data/stock").glob("stock_*.csv")):
            cleaned, missing, audit = clean_stock_file(path)
            clean_frames.append(cleaned)
            missing_frames.append(missing)
            audit_records.append(audit)

        stock_clean = pd.concat(clean_frames, ignore_index=True)
        missing_summary = pd.concat(missing_frames, ignore_index=True)
        clean_audit = pd.DataFrame(audit_records)

        stock_clean.to_csv(ROOT / "data/clean/stock_clean.csv", index=False, encoding="utf-8-sig")
        missing_summary.to_csv(ROOT / "data/clean/missing_summary.csv", index=False, encoding="utf-8-sig")
        clean_audit.to_csv(ROOT / "data/clean/clean_audit.csv", index=False, encoding="utf-8-sig")

        clean_audit
        """
    ),
    md(
        """
        清洗说明：缺失值先统计再用向前填充处理，原因是日度行情中的少量缺失通常来自停牌、节假日或数据源临时缺口，向前填充可以保持时间序列连续性。重复记录按 `code + date` 删除，只保留最后一条。极端收益率不删除，只用 `is_extreme` 标注，避免把真实涨跌停或复权异常直接抹掉。
        """
    ),
    md(
        """
        ## 3.2 宽表与长表转换

        宽表适合相关系数、矩阵运算和多资产组合计算；长表适合分组统计、绘图分面和与行业信息合并。
        """
    ),
    code(
        r"""
        close_wide = stock_clean.pivot_table(index="date", columns="code", values="close", aggfunc="last").sort_index()
        close_long = close_wide.reset_index().melt(id_vars="date", var_name="code", value_name="close")

        close_wide.to_csv(ROOT / "data/clean/stock_close_wide.csv", encoding="utf-8-sig")
        close_long.to_csv(ROOT / "data/clean/stock_close_long.csv", index=False, encoding="utf-8-sig")

        print("Wide table shape:", close_wide.shape)
        print("Long table shape:", close_long.shape)
        close_long.head()
        """
    ),
    md(
        """
        ## 3.3 多表合并

        股票日度数据先与指数按日期左连接，再将月度宏观指标映射到同一月份的每个交易日。
        """
    ),
    code(
        r"""
        def load_index(code: str, prefix: str) -> pd.DataFrame:
            df = pd.read_csv(ROOT / f"data/index/index_{code}.csv")
            df["date"] = pd.to_datetime(df["date"])
            keep = df[["date", "close"]].rename(columns={"close": f"{prefix}_close"})
            keep[f"{prefix}_return"] = np.log(keep[f"{prefix}_close"] / keep[f"{prefix}_close"].shift(1))
            return keep


        hs300 = load_index("000300", "hs300")
        zz500 = load_index("000905", "zz500")

        before_stock_rows = len(stock_clean)
        combined = stock_clean.merge(hs300, on="date", how="left")
        after_hs300_rows = len(combined)
        combined = combined.merge(zz500, on="date", how="left")
        after_zz500_rows = len(combined)

        macro_frames = []
        for path in sorted((ROOT / "data/macro").glob("macro_*.csv")):
            df = pd.read_csv(path)
            df["date"] = pd.to_datetime(df["date"])
            macro_frames.append(df)
        macro = pd.concat(macro_frames, ignore_index=True)
        macro["month"] = macro["date"].dt.to_period("M").astype(str)
        macro_month = (
            macro.sort_values("date")
            .drop_duplicates(subset=["month", "indicator"], keep="last")
            .pivot(index="month", columns="indicator", values="value")
            .reset_index()
        )

        combined["month"] = combined["date"].dt.to_period("M").astype(str)
        before_macro_rows = len(combined)
        combined = combined.merge(macro_month, on="month", how="left")
        after_macro_rows = len(combined)

        combined.to_csv(ROOT / "data/combined/combined_data.csv", index=False, encoding="utf-8-sig")

        merge_audit = pd.DataFrame([
            {"step": "stock_clean", "rows": before_stock_rows, "note": "清洗后的股票长表"},
            {"step": "left_join_hs300", "rows": after_hs300_rows, "note": "按日期左连接沪深300，行数应保持不变"},
            {"step": "left_join_zz500", "rows": after_zz500_rows, "note": "按日期左连接中证500，行数应保持不变"},
            {"step": "left_join_macro", "rows": after_macro_rows, "note": "按月份映射宏观指标，行数应保持不变"},
        ])
        merge_audit.to_csv(ROOT / "data/clean/merge_audit.csv", index=False, encoding="utf-8-sig")
        merge_audit
        """
    ),
    md(
        """
        合并说明：所有连接均以个股日度记录为主表，所以行数理论上不应减少。若指数或宏观指标缺失，只会在对应字段留下空值，便于后续判断数据覆盖情况。
        """
    ),
    md(
        """
        ## Parquet 存储与 CSV 对比

        Parquet 保留字段类型，支持只读取需要的列。下面对比 CSV 和 Parquet 的文件大小与读取时间。
        """
    ),
    code(
        r"""
        csv_path = ROOT / "data/clean/stock_clean.csv"
        parquet_path = ROOT / "data/clean/stock_clean.parquet"

        stock_clean.to_parquet(parquet_path, index=False)

        subset = pd.read_parquet(parquet_path, columns=["date", "code", "close"])
        schema = pq.read_schema(parquet_path)
        print(schema)
        print("Column subset shape:", subset.shape)

        t0 = time.time()
        pd.read_csv(csv_path)
        csv_time = time.time() - t0

        t0 = time.time()
        pd.read_parquet(parquet_path)
        parquet_time = time.time() - t0

        storage_compare = pd.DataFrame([
            {"format": "CSV", "read_seconds": csv_time, "size_kb": os.path.getsize(csv_path) / 1024},
            {"format": "Parquet", "read_seconds": parquet_time, "size_kb": os.path.getsize(parquet_path) / 1024},
        ])
        storage_compare.to_csv(ROOT / "data/clean/storage_compare.csv", index=False, encoding="utf-8-sig")
        storage_compare
        """
    ),
    md(
        """
        对比结论：在本作业这种中小规模数据下，CSV 与 Parquet 的速度差异通常不会非常夸张；但 Parquet 的类型信息、压缩效果和列式读取能力更适合字段更多、数据量更大、只需读取部分列的分析场景。
        """
    ),
]


NOTEBOOK_03 = [
    md(
        """
        # 03 描述性统计、可视化与 CAPM 回归

        本 Notebook 基于清洗合并后的 CSV 数据进行分析，输出描述性统计表、图形和 CAPM 回归结果，并提供可直接阅读的文字解读。
        """
    ),
    code(
        r"""
        from pathlib import Path
        import math
        import os

        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        from scipy import stats
        import statsmodels.api as sm

        ROOT = Path.cwd()
        OUTPUT = ROOT / "output"
        OUTPUT.mkdir(exist_ok=True)

        plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
        plt.rcParams["axes.unicode_minus"] = False
        sns.set_theme(style="whitegrid", font="Microsoft YaHei")

        combined = pd.read_csv(ROOT / "data/combined/combined_data.csv")
        combined["date"] = pd.to_datetime(combined["date"])
        stock_info = pd.read_csv(ROOT / "data/stock_list.csv")
        finance = pd.read_csv(ROOT / "data/finance/finance_ratios.csv")

        combined.head()
        """
    ),
    md(
        """
        ## 4.1 基本统计量

        日收益率使用对数收益率，年化均值乘以 252，年化波动率乘以 `sqrt(252)`，最大回撤基于累计净值计算。
        """
    ),
    code(
        r"""
        def max_drawdown(ret: pd.Series) -> float:
            wealth = np.exp(ret.fillna(0).cumsum())
            drawdown = wealth / wealth.cummax() - 1
            return drawdown.min()


        stats_records = []
        for code_value, group in combined.sort_values("date").groupby("code"):
            ret = group["return"].dropna()
            meta = stock_info.loc[stock_info["code"].astype(str).str.zfill(6) == str(code_value).zfill(6)].iloc[0]
            stats_records.append({
                "股票": meta["name"],
                "代码": str(code_value).zfill(6),
                "行业": meta["industry"],
                "年化均值": ret.mean() * 252,
                "年化波动率": ret.std() * math.sqrt(252),
                "偏度": ret.skew(),
                "峰度": ret.kurt(),
                "最大回撤": max_drawdown(ret),
            })

        desc_stats = pd.DataFrame(stats_records)
        desc_stats.to_csv(ROOT / "output/descriptive_stats.csv", index=False, encoding="utf-8-sig")
        desc_stats
        """
    ),
    md(
        """
        统计表用于比较不同股票的收益风险特征。年化收益和波动率体现收益补偿与风险暴露，最大回撤则更直观地衡量持有期间可能承受的下行压力。
        """
    ),
    md(
        """
        ## 图 1：归一化收盘价走势图

        将每个资产的起点标准化为 1，可以比较不同价格水平股票的相对走势。
        """
    ),
    code(
        r"""
        industry_palette = {
            "银行": "#1f77b4", "白酒": "#d62728", "汽车": "#2ca02c",
            "能源": "#ff7f0e", "通讯": "#9467bd", "指数": "#111111",
        }

        price_wide = combined.pivot_table(index="date", columns="code", values="close", aggfunc="last").sort_index()
        norm_prices = price_wide / price_wide.apply(lambda s: s.dropna().iloc[0])
        hs300 = combined.drop_duplicates("date").set_index("date")["hs300_close"].sort_index()
        hs300_norm = hs300 / hs300.dropna().iloc[0]

        fig, ax = plt.subplots(figsize=(14, 7))
        for code_value in norm_prices.columns:
            meta = stock_info.loc[stock_info["code"].astype(str).str.zfill(6) == str(code_value).zfill(6)].iloc[0]
            ax.plot(norm_prices.index, norm_prices[code_value], lw=1.3, alpha=0.9, color=industry_palette[meta["industry"]], label=f"{meta['industry']}-{meta['name']}")
        ax.plot(hs300_norm.index, hs300_norm, color=industry_palette["指数"], lw=2.5, label="指数-沪深300")
        ax.set_title("图 1：归一化收盘价走势（起点=1）")
        ax.set_xlabel("日期")
        ax.set_ylabel("归一化价格")
        ax.legend(ncol=3, fontsize=9)
        fig.tight_layout()
        fig.savefig(OUTPUT / "fig1_normalized_prices.png", dpi=180)
        plt.show()
        """
    ),
    md(
        """
        图 1 展示了不同股票相对于起点的累计表现。若某只股票曲线长期高于沪深 300，说明其在样本期内获得了更强的相对收益；若曲线波动幅度更大，则说明该股票承担了更高的价格风险。
        """
    ),
    md(
        """
        ## 图 2：日收益率分布图
        """
    ),
    code(
        r"""
        fig, axes = plt.subplots(2, 5, figsize=(18, 7), sharex=False, sharey=False)
        for ax, (code_value, group) in zip(axes.ravel(), combined.groupby("code")):
            meta = stock_info.loc[stock_info["code"].astype(str).str.zfill(6) == str(code_value).zfill(6)].iloc[0]
            ret = group["return"].dropna()
            sns.histplot(ret, bins=40, stat="density", color=industry_palette[meta["industry"]], alpha=0.45, ax=ax)
            x = np.linspace(ret.quantile(0.01), ret.quantile(0.99), 200)
            ax.plot(x, stats.norm.pdf(x, ret.mean(), ret.std()), color="black", lw=1.2)
            ax.set_title(f"{meta['name']}  均值={ret.mean():.4f}, σ={ret.std():.4f}", fontsize=10)
            ax.set_xlabel("日对数收益率")
            ax.set_ylabel("密度")
        fig.suptitle("图 2：日收益率分布与正态曲线", y=1.02, fontsize=15)
        fig.tight_layout()
        fig.savefig(OUTPUT / "fig2_return_distribution.png", dpi=180, bbox_inches="tight")
        plt.show()
        """
    ),
    md(
        """
        图 2 可以观察收益率是否接近正态分布。实际股票收益常出现尖峰厚尾，说明极端波动发生概率往往高于简单正态假设，这也是风险管理中需要额外关注的部分。
        """
    ),
    md(
        """
        ## 图 3：收益率相关系数热力图
        """
    ),
    code(
        r"""
        ordered_codes = stock_info.sort_values(["industry", "code"])["code"].astype(str).str.zfill(6).tolist()
        ret_wide = combined.pivot_table(index="date", columns="code", values="return", aggfunc="last")
        ret_wide.columns = ret_wide.columns.astype(str).str.zfill(6)
        corr = ret_wide[ordered_codes].corr()
        labels = [stock_info.loc[stock_info["code"].astype(str).str.zfill(6) == c, "name"].iloc[0] for c in ordered_codes]

        fig, ax = plt.subplots(figsize=(11, 9))
        sns.heatmap(corr, cmap="RdBu_r", center=0, annot=True, fmt=".2f", square=True,
                    xticklabels=labels, yticklabels=labels, ax=ax)
        ax.set_title("图 3：10 只股票日收益率相关系数矩阵")
        fig.tight_layout()
        fig.savefig(OUTPUT / "fig3_return_correlation_heatmap.png", dpi=180)
        plt.show()
        """
    ),
    md(
        """
        图 3 按行业排序后更容易观察行业内相关性。通常同一行业股票面对相近的基本面和政策冲击，相关性可能高于跨行业股票；但龙头公司、业务结构和市场风格差异也会削弱这种关系。
        """
    ),
    md(
        """
        ## 图 4：宏观指标与股市关系
        """
    ),
    code(
        r"""
        monthly = (
            combined.drop_duplicates("date")
            .set_index("date")
            .sort_index()[["hs300_close", "cpi", "m2"]]
            .resample("ME")
            .last()
        )
        monthly["hs300_monthly_return"] = np.log(monthly["hs300_close"] / monthly["hs300_close"].shift(1))
        scatter = monthly.dropna(subset=["hs300_monthly_return", "cpi"])
        pearson_r = scatter["cpi"].corr(scatter["hs300_monthly_return"])

        fig, ax = plt.subplots(figsize=(9, 6))
        sns.regplot(data=scatter, x="cpi", y="hs300_monthly_return", ax=ax,
                    scatter_kws={"s": 42, "alpha": 0.75}, line_kws={"color": "#d62728"})
        ax.set_title(f"图 4：CPI 同比增速与沪深300月度收益率（Pearson r={pearson_r:.2f}）")
        ax.set_xlabel("CPI 同比增速（%）")
        ax.set_ylabel("沪深300月度对数收益率")
        fig.tight_layout()
        fig.savefig(OUTPUT / "fig4_macro_cpi_vs_hs300.png", dpi=180)
        plt.show()
        """
    ),
    md(
        """
        图 4 用散点和拟合线展示 CPI 与市场月度收益的线性关系。如果相关系数为正，说明样本期内较高通胀月份常伴随较高市场收益；如果为负，则可能反映通胀上行带来的政策收紧或估值压力。不过宏观变量与股票市场之间存在滞后和多因素共同作用，不能仅凭单变量散点图判断因果。
        """
    ),
    md(
        """
        ## 图 5（选做）：财务指标 ROE 跨公司对比
        """
    ),
    code(
        r"""
        roe = finance[finance["indicator"] == "roe"].copy()
        fig, ax = plt.subplots(figsize=(12, 6))
        for code_value, group in roe.groupby("code"):
            meta = stock_info.loc[stock_info["code"].astype(str).str.zfill(6) == str(code_value).zfill(6)].iloc[0]
            ax.plot(group["year"], group["value"], marker="o", color=industry_palette[meta["industry"]], label=f"{meta['industry']}-{meta['name']}")
        ax.set_title("图 5：最近 5 年 ROE 跨公司对比")
        ax.set_xlabel("年度")
        ax.set_ylabel("ROE（%）")
        ax.legend(ncol=3, fontsize=9)
        fig.tight_layout()
        fig.savefig(OUTPUT / "fig5_roe_comparison.png", dpi=180)
        plt.show()
        """
    ),
    md(
        """
        图 5 用 ROE 展示公司盈利能力差异。消费龙头通常 ROE 水平较高，公用事业和通讯运营商可能更稳定，汽车和通讯设备公司的 ROE 则更容易受产业周期、投资扩张和竞争格局影响。
        """
    ),
    md(
        """
        ## 5.1 CAPM 模型估计

        CAPM 设定无风险利率为年化 2%，换算为日度 `0.02 / 252`。
        """
    ),
    code(
        r"""
        RF_DAILY = 0.02 / 252
        capm_records = []

        for code_value, group in combined.groupby("code"):
            data = group[["return", "hs300_return"]].dropna().copy()
            data["excess_stock"] = data["return"] - RF_DAILY
            data["excess_market"] = data["hs300_return"] - RF_DAILY
            X = sm.add_constant(data["excess_market"])
            y = data["excess_stock"]
            model = sm.OLS(y, X).fit()
            ci = model.conf_int().loc["excess_market"]
            meta = stock_info.loc[stock_info["code"].astype(str).str.zfill(6) == str(code_value).zfill(6)].iloc[0]
            capm_records.append({
                "股票": meta["name"],
                "代码": str(code_value).zfill(6),
                "行业": meta["industry"],
                "alpha": model.params["const"],
                "alpha_pvalue": model.pvalues["const"],
                "beta": model.params["excess_market"],
                "beta_ci_low": ci[0],
                "beta_ci_high": ci[1],
                "r_squared": model.rsquared,
            })

        capm_results = pd.DataFrame(capm_records).sort_values("beta", ascending=False)
        capm_results.to_csv(OUTPUT / "capm_results.csv", index=False, encoding="utf-8-sig")
        capm_results
        """
    ),
    code(
        r"""
        fig, ax = plt.subplots(figsize=(10, 7))
        plot_df = capm_results.sort_values("beta")
        y_pos = np.arange(len(plot_df))
        colors = plot_df["行业"].map(industry_palette)
        xerr = np.vstack([
            plot_df["beta"] - plot_df["beta_ci_low"],
            plot_df["beta_ci_high"] - plot_df["beta"],
        ])
        ax.errorbar(plot_df["beta"], y_pos, xerr=xerr, fmt="none", ecolor="#555555", capsize=3, alpha=0.8)
        ax.scatter(plot_df["beta"], y_pos, c=colors, s=70)
        ax.axvline(1.0, color="#d62728", linestyle="--", lw=1.4, label="β=1")
        ax.set_yticks(y_pos)
        ax.set_yticklabels(plot_df["股票"])
        ax.set_xlabel("Beta")
        ax.set_title("图 6：CAPM Beta 估计与 95% 置信区间")
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUTPUT / "fig6_capm_beta.png", dpi=180)
        plt.show()
        """
    ),
    md(
        """
        ### CAPM 讨论
        """
    ),
    code(
        r"""
        beta_gt_1 = capm_results[capm_results["beta"] > 1]
        alpha_sig = capm_results[capm_results["alpha_pvalue"] < 0.05]
        highest_r2 = capm_results.loc[capm_results["r_squared"].idxmax()]
        lowest_r2 = capm_results.loc[capm_results["r_squared"].idxmin()]

        print("1. Beta > 1 的股票：")
        if beta_gt_1.empty:
            print("   样本中没有 Beta 明显大于 1 的股票，整体系统性风险暴露低于或接近市场。")
        else:
            print("   " + "、".join([f"{r['股票']}（{r['行业']}，β={r['beta']:.2f}）" for _, r in beta_gt_1.iterrows()]))
            print("   汽车、通讯设备等成长或周期属性更强的行业若 Beta 较高，通常与其对经济景气、资本开支和风险偏好的敏感性相吻合。")

        print("\n2. Alpha 显著性：")
        if alpha_sig.empty:
            print("   没有股票 Alpha 在 5% 水平显著异于 0，说明控制市场风险后，样本中未发现稳定的超额收益。")
        else:
            print("   " + "、".join([f"{r['股票']}（p={r['alpha_pvalue']:.3f}）" for _, r in alpha_sig.iterrows()]))
            print("   Alpha 显著意味着在 CAPM 的单因子框架下，该股票仍有不能被市场因子解释的平均超额收益，但还需结合样本期和其他风险因子判断。")

        print("\n3. R² 差异：")
        print(f"   R² 最高的是 {highest_r2['股票']}（{highest_r2['r_squared']:.2%}），最低的是 {lowest_r2['股票']}（{lowest_r2['r_squared']:.2%}）。")
        print("   R² 较高说明个股收益更大比例可由市场组合解释；R² 较低说明公司特质因素、行业事件或 idiosyncratic 风险占比更高。")
        """
    ),
    md(
        """
        ## 结论

        本项目建立了从数据获取、清洗、存储、合并到统计分析和回归检验的完整流程。CSV 适合透明提交和检查，Parquet 更适合后续扩展到更大数据量；CAPM 结果则提供了比较不同行业系统性风险暴露的基础框架。
        """
    ),
]


def main() -> None:
    for directory in [
        "data/stock",
        "data/index",
        "data/macro",
        "data/finance",
        "data/clean",
        "data/combined",
        "output",
        ".github/workflows",
        "scripts",
    ]:
        (ROOT / directory).mkdir(parents=True, exist_ok=True)

    write_text(ROOT / "README.md", README)
    write_text(ROOT / "requirements.txt", REQS)
    write_text(ROOT / ".gitignore", GITIGNORE)
    write_text(ROOT / "_quarto.yml", QUARTO)
    write_text(ROOT / "index.qmd", INDEX_QMD)
    write_text(ROOT / ".github/workflows/quarto-publish.yml", WORKFLOW)
    write_text(ROOT / "scripts/run_notebooks.py", RUN_NOTEBOOKS)
    write_text(ROOT / "scripts/export_report.py", EXPORT_REPORT)
    write_text(ROOT / "download_log.txt", "")
    write_text(ROOT / "report.html", "<!doctype html><meta charset='utf-8'><p>Run 03_analysis.ipynb and scripts/export_report.py to regenerate this report.</p>")

    write_notebook(ROOT / "01_download.ipynb", NOTEBOOK_01)
    write_notebook(ROOT / "02_clean.ipynb", NOTEBOOK_02)
    write_notebook(ROOT / "03_analysis.ipynb", NOTEBOOK_03)

    print(json.dumps({"project": str(ROOT), "files": 12}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
