from typing import TypedDict, Optional


class SecurityData(TypedDict):
    ticker: str
    name: str
    sector: str
    market: str          # "US" | "UK" | "ETF"
    current_price: float
    week52_high: float
    drop_pct: float      # % drop from 52-week high
    index_drop_pct: float  # benchmark index drop over same period
    pe_ratio: Optional[float]
    debt_to_equity: Optional[float]
    revenue_growth: Optional[float]
    market_cap: Optional[float]
    news: list[str]      # recent headline strings


class AnalyzedSecurity(TypedDict):
    ticker: str
    name: str
    sector: str
    market: str
    current_price: float
    week52_high: float
    drop_pct: float
    pe_ratio: Optional[float]
    debt_to_equity: Optional[float]
    revenue_growth: Optional[float]
    investable: bool
    event_description: str    # what caused the drop
    investment_reason: str    # why it's still a good buy
    disqualifiers: list[str]  # fraud/ban/scandal if any
    confidence: float         # 0.0 - 1.0
    risk_level: str           # "LOW" | "MEDIUM"
    score: float              # final ranking score


class AgentState(TypedDict):
    universe: list[str]               # all tickers to screen
    candidates: list[SecurityData]    # passed price filter
    analyzed: list[AnalyzedSecurity]  # after AI judgment
    top5: list[AnalyzedSecurity]      # final top 5
    report_text: str                  # formatted report
    run_time: str                     # "pre-market" | "post-market"
    errors: list[str]                 # non-fatal errors to log
