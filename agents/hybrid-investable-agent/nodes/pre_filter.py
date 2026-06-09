from state import AgentState, SecurityData, AnalyzedSecurity

# These keywords in news → instant disqualify, no LLM needed
DISQUALIFY_KEYWORDS = [
    "fraud", "fraudulent", "accounting scandal", "sec investigation",
    "criminal charges", "arrested", "bankrupt", "bankruptcy",
    "regulatory ban", "license revoked", "delisted", "ponzi",
    "class action lawsuit", "restatement", "going concern",
    "product recall", "fatal", "bribery",
]

# These keywords → clearly macro/temporary, mark investable without LLM
MACRO_KEYWORDS = [
    "broad market selloff", "market-wide", "interest rate decision",
    "fed rate", "tariff announcement", "trade war", "inflation data",
    "jobs report", "sector rotation", "profit taking", "index rebalance",
    "geopolitical tension", "oil price", "bond yield",
]


def _headlines_contain(headlines: list[str], keywords: list[str]) -> list[str]:
    combined = " ".join(headlines).lower()
    return [kw for kw in keywords if kw in combined]


def _is_market_move(security: SecurityData) -> bool:
    # Stock dropped less than 1.5x what the index dropped → market-wide move
    idx = security["index_drop_pct"]
    return idx > 2.0 and security["drop_pct"] < idx * 1.5


def _make_result(security: SecurityData, investable: bool,
                 event: str, reason: str,
                 disqualifiers: list[str], source: str) -> AnalyzedSecurity:
    return AnalyzedSecurity(
        ticker=security["ticker"],
        name=security["name"],
        sector=security["sector"],
        market=security["market"],
        current_price=security["current_price"],
        week52_high=security["week52_high"],
        drop_pct=security["drop_pct"],
        pe_ratio=security.get("pe_ratio"),
        debt_to_equity=security.get("debt_to_equity"),
        revenue_growth=security.get("revenue_growth"),
        investable=investable,
        event_description=event,
        investment_reason=reason,
        disqualifiers=disqualifiers,
        confidence=0.90 if disqualifiers else 0.70,
        risk_level="MEDIUM",
        score=0.0,
        decision_source=source,
    )


def pre_filter(state: AgentState) -> AgentState:
    """
    Skill node — no LLM. Routes candidates into 3 buckets:
      1. Disqualified  → added to analyzed as investable=False
      2. Macro/obvious → added to analyzed as investable=True
      3. Ambiguous     → kept in candidates for LLM to judge
    """
    candidates = state["candidates"]
    existing_analyzed = list(state.get("analyzed", []))
    errors = list(state.get("errors", []))

    pre_decided: list[AnalyzedSecurity] = []
    to_llm: list[SecurityData] = []

    for s in candidates:
        headlines = s.get("news", [])
        bad_flags = _headlines_contain(headlines, DISQUALIFY_KEYWORDS)

        if bad_flags:
            pre_decided.append(_make_result(
                s, investable=False,
                event=f"Disqualifying signal in news: {', '.join(bad_flags[:2])}.",
                reason="Automatically rejected — rule-based disqualifier triggered.",
                disqualifiers=bad_flags,
                source="pre_filter_disqualify",
            ))
        elif _is_market_move(s) or _headlines_contain(headlines, MACRO_KEYWORDS):
            pre_decided.append(_make_result(
                s, investable=True,
                event="Broad market or macro-driven selloff detected.",
                reason="Drop is in line with market movement — no stock-specific issue found by rules.",
                disqualifiers=[],
                source="pre_filter_macro",
            ))
        else:
            to_llm.append(s)

    disqualified = sum(1 for p in pre_decided if not p["investable"])
    macro_passed = sum(1 for p in pre_decided if p["investable"])

    print(f"[pre_filter] {disqualified} disqualified | "
          f"{macro_passed} passed (macro rule) | "
          f"{len(to_llm)} → Claude for judgment")

    return {
        **state,
        "candidates": to_llm,
        "analyzed": existing_analyzed + pre_decided,
        "errors": errors,
    }


def route_after_pre_filter(state: AgentState) -> str:
    """
    Conditional edge function.
    If there are still ambiguous candidates → go to LLM analyzer.
    If pre_filter handled everything → go straight to ranker.
    """
    if state["candidates"]:
        return "analyze"
    return "rank"
