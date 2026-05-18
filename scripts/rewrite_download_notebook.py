from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]


nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "pygments_lexer": "ipython3"},
}

nb["cells"] = [
    nbf.v4.new_markdown_cell(
        """# 01 数据下载

本 Notebook 完成项目目录创建和四类数据获取：个股行情、市场指数、宏观指标、财务指标。具体下载函数集中在 `scripts/download_data.py`，优先使用 `akshare` 东方财富接口，失败时自动切换到新浪接口；只有两个真实接口都失败时才使用明确标记的 fallback。"""
    ),
    nbf.v4.new_markdown_cell(
        """## 股票池与数据来源

股票池覆盖银行、白酒、汽车、能源、通讯五个行业。股票行情使用后复权日度数据，市场指数包括沪深 300 和中证 500，宏观指标包括 CPI 与 M2，财务指标包括 ROE 和资产负债率。"""
    ),
    nbf.v4.new_code_cell(
        """from pathlib import Path
import pandas as pd

ROOT = Path.cwd()
print(ROOT)"""
    ),
    nbf.v4.new_code_cell("%run scripts/download_data.py"),
    nbf.v4.new_markdown_cell(
        """## 下载结果检查

下面检查日志、原始数据文件数量和数据源分布。正式提交时应尽量看到 `SUCCESS`，且 `source` 应为 `akshare` 或 `akshare_sina`。"""
    ),
    nbf.v4.new_code_cell(
        """from pathlib import Path
import pandas as pd

ROOT = Path.cwd()
print((ROOT / "download_log.txt").read_text(encoding="utf-8"))

source_summary = {
    "stock": pd.concat([pd.read_csv(p, usecols=["source"]) for p in (ROOT / "data/stock").glob("stock_*.csv")])["source"].value_counts().to_dict(),
    "index": pd.concat([pd.read_csv(p, usecols=["source"]) for p in (ROOT / "data/index").glob("index_*.csv")])["source"].value_counts().to_dict(),
    "macro": pd.concat([pd.read_csv(p, usecols=["source"]) for p in (ROOT / "data/macro").glob("macro_*.csv")])["source"].value_counts().to_dict(),
    "finance": pd.read_csv(ROOT / "data/finance/finance_ratios.csv")["source"].value_counts().to_dict(),
}
source_summary"""
    ),
]

nbf.write(nb, ROOT / "01_download.ipynb")
print("Rewrote 01_download.ipynb")
