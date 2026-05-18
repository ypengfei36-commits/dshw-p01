from __future__ import annotations

import os
import time
from datetime import datetime
from pathlib import Path

import akshare as ak
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
START_DATE = "2020-01-01"
END_DATE = pd.Timestamp.today().normalize()
END_DATE_STR = END_DATE.strftime("%Y%m%d")
LOG_PATH = ROOT / "download_log.txt"

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


def log_event(status: str, item: str, message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {status:<7} {item:<18} {message}\n"
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(line)
    print(line, end="")


def standardize_ohlcv(df: pd.DataFrame, code: str, name: str, source: str) -> pd.DataFrame:
    rename_map = {
        "日期": "date",
        "股票代码": "code",
        "开盘": "open",
        "开盘价": "open",
        "收盘": "close",
        "收盘价": "close",
        "最高": "high",
        "最高价": "high",
        "最低": "low",
        "最低价": "low",
        "成交量": "volume",
        "成交额": "amount",
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


def simulate_ohlcv(code: str, name: str, base: float = 30, beta: float = 1.0) -> pd.DataFrame:
    dates = pd.bdate_range(start=START_DATE, end=END_DATE)
    rng = np.random.default_rng(int(code) % (2**32 - 1))
    returns = 0.00012 + beta * rng.normal(0.00015, 0.011, len(dates)) + rng.normal(0, 0.012, len(dates))
    close = base * np.exp(np.cumsum(returns))
    open_ = close * np.exp(rng.normal(0, 0.004, len(dates)))
    high = np.maximum(open_, close) * (1 + rng.uniform(0.001, 0.025, len(dates)))
    low = np.minimum(open_, close) * (1 - rng.uniform(0.001, 0.025, len(dates)))
    volume = rng.integers(200_000, 5_000_000, len(dates))
    return pd.DataFrame(
        {
            "date": dates,
            "code": code,
            "name": name,
            "open": open_,
            "close": close,
            "high": high,
            "low": low,
            "volume": volume,
            "amount": volume * close * 100,
            "source": "simulated_fallback",
        }
    )


def fetch_stock(row: dict) -> pd.DataFrame:
    industry_beta = {"银行": 0.9, "白酒": 0.85, "汽车": 1.25, "能源": 0.95, "通讯": 1.15}
    errors: list[str] = []
    try:
        raw = ak.stock_zh_a_hist(
            symbol=row["code"],
            period="daily",
            start_date=START_DATE.replace("-", ""),
            end_date=END_DATE_STR,
            adjust="hfq",
            timeout=20,
        )
        data = standardize_ohlcv(raw, row["code"], row["name"], "akshare")
        if data.empty:
            raise ValueError("No data returned")
        log_event("SUCCESS", f"stock_{row['code']}", f"shape={data.shape}")
        return data
    except Exception as exc:
        errors.append(f"eastmoney={type(exc).__name__}: {exc}")
    try:
        market_prefix = "sh" if row["code"].startswith("6") else "sz"
        raw = ak.stock_zh_a_daily(
            symbol=f"{market_prefix}{row['code']}",
            start_date=START_DATE.replace("-", ""),
            end_date=END_DATE_STR,
            adjust="hfq",
        )
        data = standardize_ohlcv(raw, row["code"], row["name"], "akshare_sina")
        if data.empty:
            raise ValueError("No data returned")
        log_event("SUCCESS", f"stock_{row['code']}", f"shape={data.shape}; provider=sina")
        return data
    except Exception as exc:
        errors.append(f"sina={type(exc).__name__}: {exc}")
        data = simulate_ohlcv(row["code"], row["name"], base=20 + (int(row["code"][-2:]) % 60), beta=industry_beta.get(row["industry"], 1.0))
        log_event("FAILED", f"stock_{row['code']}", f"{' | '.join(errors)}; fallback shape={data.shape}")
        return data


def fetch_index(item: dict) -> pd.DataFrame:
    errors: list[str] = []
    try:
        raw = ak.stock_zh_index_daily_em(symbol=item["ak_symbol"])
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
        errors.append(f"eastmoney={type(exc).__name__}: {exc}")
    try:
        raw = ak.stock_zh_index_daily(symbol=item["ak_symbol"])
        raw["date"] = pd.to_datetime(raw["date"])
        raw = raw[(raw["date"] >= START_DATE) & (raw["date"] <= END_DATE)]
        out = raw[["date", "open", "close", "high", "low", "volume"]].copy()
        out["amount"] = np.nan
        out["code"] = item["code"]
        out["name"] = item["name"]
        out["source"] = "akshare_sina"
        out = out[["date", "code", "name", "open", "close", "high", "low", "volume", "amount", "source"]]
        if out.empty:
            raise ValueError("No data returned")
        log_event("SUCCESS", f"index_{item['code']}", f"shape={out.shape}; provider=sina")
        return out
    except Exception as exc:
        errors.append(f"sina={type(exc).__name__}: {exc}")
        data = simulate_ohlcv(item["code"], item["name"], base=4000, beta=1.0)
        log_event("FAILED", f"index_{item['code']}", f"{' | '.join(errors)}; fallback shape={data.shape}")
        return data


def standardize_macro(raw: pd.DataFrame, indicator: str) -> pd.DataFrame:
    out = raw.rename(columns={"日期": "date", "今值": "value"}).copy()
    out = out[["date", "value"]].copy()
    out["date"] = pd.to_datetime(out["date"])
    out["value"] = pd.to_numeric(out["value"], errors="coerce")
    out = out[out["date"] >= START_DATE].dropna(subset=["value"])
    out["indicator"] = indicator
    out["source"] = "akshare"
    return out[["date", "indicator", "value", "source"]]


def fetch_macro(indicator: str, func_name: str) -> pd.DataFrame:
    try:
        raw = getattr(ak, func_name)()
        data = standardize_macro(raw, indicator)
        if data.empty:
            raise ValueError("No data returned")
        log_event("SUCCESS", f"macro_{indicator}", f"shape={data.shape}")
        return data
    except Exception as exc:
        dates = pd.date_range(START_DATE, END_DATE, freq="MS")
        rng = np.random.default_rng(abs(hash(indicator)) % (2**32 - 1))
        base = 1.5 if indicator == "cpi" else 8.5
        data = pd.DataFrame({"date": dates, "indicator": indicator, "value": base + np.cumsum(rng.normal(0, 0.08, len(dates))), "source": "simulated_fallback"})
        log_event("FAILED", f"macro_{indicator}", f"{type(exc).__name__}: {exc}; fallback shape={data.shape}")
        return data


def simulate_finance(row: dict) -> pd.DataFrame:
    years = list(range(max(2020, END_DATE.year - 5), END_DATE.year))
    rng = np.random.default_rng(int(row["code"]) % (2**32 - 1))
    industry_roe = {"银行": 10, "白酒": 22, "汽车": 8, "能源": 9, "通讯": 11}
    records = []
    for year in years[-5:]:
        records.extend(
            [
                {"code": row["code"], "name": row["name"], "industry": row["industry"], "year": year, "indicator": "roe", "value": industry_roe.get(row["industry"], 10) + rng.normal(0, 2), "source": "simulated_fallback"},
                {"code": row["code"], "name": row["name"], "industry": row["industry"], "year": year, "indicator": "debt_to_asset", "value": 50 + rng.normal(0, 10), "source": "simulated_fallback"},
            ]
        )
    return pd.DataFrame(records)


def fetch_finance(row: dict) -> pd.DataFrame:
    try:
        raw = ak.stock_financial_analysis_indicator(symbol=row["code"], start_year="2020")
        raw["date"] = pd.to_datetime(raw["日期"])
        annual = raw[raw["date"].dt.month == 12].copy()
        if annual.empty:
            annual = raw.sort_values("date").groupby(raw["date"].dt.year).tail(1).copy()
        annual["year"] = annual["date"].dt.year
        annual = annual.sort_values("year").tail(5)
        records = []
        for _, item in annual.iterrows():
            for indicator, candidates in {"roe": ["净资产收益率(%)", "加权净资产收益率(%)"], "debt_to_asset": ["资产负债率(%)"]}.items():
                col = next((candidate for candidate in candidates if candidate in annual.columns), None)
                if col is None:
                    continue
                value = pd.to_numeric(item[col], errors="coerce")
                if pd.notna(value):
                    records.append({"code": row["code"], "name": row["name"], "industry": row["industry"], "year": int(item["year"]), "indicator": indicator, "value": float(value), "source": "akshare"})
        data = pd.DataFrame(records)
        if data.empty:
            raise ValueError("No usable finance metrics")
        log_event("SUCCESS", f"finance_{row['code']}", f"shape={data.shape}")
        return data
    except Exception as exc:
        data = simulate_finance(row)
        log_event("FAILED", f"finance_{row['code']}", f"{type(exc).__name__}: {exc}; fallback shape={data.shape}")
        return data


def main() -> None:
    for directory in ["data/stock", "data/index", "data/macro", "data/finance", "data/clean", "data/combined", "output"]:
        os.makedirs(ROOT / directory, exist_ok=True)
    LOG_PATH.write_text("", encoding="utf-8")
    pd.DataFrame(STOCKS).to_csv(ROOT / "data/stock_list.csv", index=False, encoding="utf-8-sig")

    for row in STOCKS:
        fetch_stock(row).to_csv(ROOT / f"data/stock/stock_{row['code']}.csv", index=False, encoding="utf-8-sig")
        time.sleep(0.2)
    for item in INDEXES:
        fetch_index(item).to_csv(ROOT / f"data/index/index_{item['code']}.csv", index=False, encoding="utf-8-sig")
        time.sleep(0.2)
    for indicator, func_name in [("cpi", "macro_china_cpi_yearly"), ("m2", "macro_china_m2_yearly")]:
        fetch_macro(indicator, func_name).to_csv(ROOT / f"data/macro/macro_{indicator}.csv", index=False, encoding="utf-8-sig")
        time.sleep(0.2)
    finance = pd.concat([fetch_finance(row) for row in STOCKS], ignore_index=True)
    finance.to_csv(ROOT / "data/finance/finance_ratios.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()
