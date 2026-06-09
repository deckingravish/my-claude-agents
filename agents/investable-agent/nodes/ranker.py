from state import AgentState, AnalyzedSecurity
from config import TOP_N_RESULTS


def _compute_score(s: AnalyzedSecurity) -> float:
    # drop magnitude: deeper dip = more upside (weight 40%)
    drop_score = min(s["drop_pct"] / 50.0, 1.0)  # cap at 50% drop = 1.0

    # AI confidence (weight 40%)
    confidence_score = s["confidence"]

    # Fundamentals: low P/E relative to market avg (~20) is better (weight 20%)
    pe = s.get("pe_ratio")
    if pe and isinstance(pe, (int, float)) and pe > 0:
        pe_score = max(0.0, 1.0 - (pe / 30.0))  # P/E of 0 → 1.0, P/E of 30+ → 0.0
    else:
        pe_score = 0.5  # neutral if no data

    return round(drop_score * 0.4 + confidence_score * 0.4 + pe_score * 0.2, 4)


def rank(state: AgentState) -> AgentState:
    analyzed = state["analyzed"]

    # Only rank investable ones with no disqualifiers
    investable = [
        a for a in analyzed
        if a["investable"] and not a["disqualifiers"]
    ]

    # Assign scores
    for item in investable:
        item["score"] = _compute_score(item)

    # Sort by score descending, take top N
    investable.sort(key=lambda x: x["score"], reverse=True)
    top5 = investable[:TOP_N_RESULTS]

    print(f"[ranker] Top {len(top5)} picks selected from {len(investable)} investable candidates")

    return {**state, "top5": top5}
