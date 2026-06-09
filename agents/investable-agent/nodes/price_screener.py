import yfinance as yf
from data.universe import get_benchmark
from state import AgentState, SecurityData
from config import DROP_THRESHOLD_PCT


def _pct_drop(current: float, high: float) -> float:
    if high <= 0:
        return 0.0
    return round((high - current) / high * 100, 2)


def _get_index_drop(benchmark_ticker: str) -> float:
    try:
        idx = yf.Ticker(benchmark_ticker)
        hist = idx.history(period="3mo")
        if hist.empty or len(hist) < 2:
            return 0.0
        peak = hist["Close"].max()
        latest = hist["Close"].iloc[-1]
        return _pct_drop(latest, peak)
    except Exception:
        return 0.0


def screen_prices(state: AgentState) -> AgentState:
    tickers = state["universe"]
    candidates: list[SecurityData] = []
    errors = list(state.get("errors", []))

    print(f"[price_screener] Screening {len(tickers)} tickers...")

    # Batch download is faster than individual calls
    data = yf.download(tickers, period="1y", progress=False, threads=True)

    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info

            current_price = info.get("currentPrice") or info.get("regularMarketPrice")
            week52_high = info.get("fiftyTwoWeekHigh")

            if not current_price or not week52_high:
                continue

            drop_pct = _pct_drop(current_price, week52_high)

            if drop_pct < DROP_THRESHOLD_PCT:
                continue

            benchmark = get_benchmark(ticker)
            index_drop = _get_index_drop(benchmark)

            market = "UK" if ticker.endswith(".L") else "ETF" if ticker in ["XLP", "XLV", "XLU", "XLI", "XLK", "XLF", "XLE"] else "US"

            candidates.append(SecurityData(
                ticker=ticker,
                name=info.get("longName") or info.get("shortName") or ticker,
                sector=info.get("sector") or info.get("category") or "ETF",
                market=market,
                current_price=round(current_price, 2),
                week52_high=round(week52_high, 2),
                drop_pct=drop_pct,
                index_drop_pct=index_drop,
                pe_ratio=info.get("trailingPE"),
                debt_to_equity=info.get("debtToEquity"),
                revenue_growth=info.get("revenueGrowth"),
                market_cap=info.get("marketCap"),
                news=[],
            ))

        except Exception as e:
            errors.append(f"price_screener:{ticker}: {str(e)}")

    # Sort by largest drop first so news/AI nodes process most interesting first
    candidates.sort(key=lambda x: x["drop_pct"], reverse=True)

    print(f"[price_screener] {len(candidates)} candidates passed >{DROP_THRESHOLD_PCT}% drop filter")

    return {**state, "candidates": candidates, "errors": errors}
