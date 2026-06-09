import yfinance as yf
from data.universe import get_benchmark, ETFS
from state import AgentState, SecurityData
from config import DROP_THRESHOLD_PCT


def _pct_drop(current: float, high: float) -> float:
    return round((high - current) / high * 100, 2) if high > 0 else 0.0


def _get_index_drop(benchmark_ticker: str) -> float:
    try:
        hist = yf.Ticker(benchmark_ticker).history(period="3mo")
        if hist.empty:
            return 0.0
        return _pct_drop(hist["Close"].iloc[-1], hist["Close"].max())
    except Exception:
        return 0.0


def screen_prices(state: AgentState) -> AgentState:
    tickers = state["universe"]
    candidates: list[SecurityData] = []
    errors = list(state.get("errors", []))

    print(f"[price_screener] Screening {len(tickers)} tickers...")
    yf.download(tickers, period="1y", progress=False, threads=True)

    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            current = info.get("currentPrice") or info.get("regularMarketPrice")
            high = info.get("fiftyTwoWeekHigh")
            if not current or not high:
                continue
            drop = _pct_drop(current, high)
            if drop < DROP_THRESHOLD_PCT:
                continue
            market = "UK" if ticker.endswith(".L") else "ETF" if ticker in ETFS else "US"
            candidates.append(SecurityData(
                ticker=ticker,
                name=info.get("longName") or info.get("shortName") or ticker,
                sector=info.get("sector") or info.get("category") or "ETF",
                market=market,
                current_price=round(current, 2),
                week52_high=round(high, 2),
                drop_pct=drop,
                index_drop_pct=_get_index_drop(get_benchmark(ticker)),
                pe_ratio=info.get("trailingPE"),
                debt_to_equity=info.get("debtToEquity"),
                revenue_growth=info.get("revenueGrowth"),
                market_cap=info.get("marketCap"),
                news=[],
            ))
        except Exception as e:
            errors.append(f"price_screener:{ticker}: {str(e)}")

    candidates.sort(key=lambda x: x["drop_pct"], reverse=True)
    print(f"[price_screener] {len(candidates)} candidates passed >{DROP_THRESHOLD_PCT}% filter")
    return {**state, "candidates": candidates, "errors": errors}
