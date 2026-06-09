from typing import TypedDict, Optional


class SecurityData(TypedDict):
    ticker: str
    name: str
    sector: str
    market: str
    current_price: float
    week52_high: float
    drop_pct: float
    index_drop_pct: float
    pe_ratio: Optional[float]
    debt_to_equity: Optional[float]
    revenue_growth: Optional[float]
    market_cap: Optional[float]
    news: list[str]


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
    event_description: str
    investment_reason: str
    disqualifiers: list[str]
    confidence: float
    risk_level: str
    score: float
    # NEW — tracks how the decision was made
    decision_source: str   # "pre_filter_disqualify" | "pre_filter_macro" | "llm"


class AgentState(TypedDict):
    universe: list[str]
    candidates: list[SecurityData]      # shrinks as pre_filter routes stocks away
    analyzed: list[AnalyzedSecurity]    # grows from both pre_filter and llm
    top5: list[AnalyzedSecurity]
    report_text: str
    run_time: str
    errors: list[str]
