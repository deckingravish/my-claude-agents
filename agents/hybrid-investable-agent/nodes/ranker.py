from state import AgentState, AnalyzedSecurity
from config import TOP_N_RESULTS


def _score(s: AnalyzedSecurity) -> float:
    drop_score = min(s["drop_pct"] / 50.0, 1.0)
    confidence_score = s["confidence"]
    pe = s.get("pe_ratio")
    pe_score = max(0.0, 1.0 - (pe / 30.0)) if pe and isinstance(pe, (int, float)) and pe > 0 else 0.5
    # Small bonus for pre_filter macro picks (fast + cheap) — they tend to be reliable
    source_bonus = 0.05 if s.get("decision_source") == "pre_filter_macro" else 0.0
    return round(drop_score * 0.4 + confidence_score * 0.4 + pe_score * 0.2 + source_bonus, 4)


def rank(state: AgentState) -> AgentState:
    investable = [a for a in state["analyzed"] if a["investable"] and not a["disqualifiers"]]
    for item in investable:
        item["score"] = _score(item)
    investable.sort(key=lambda x: x["score"], reverse=True)
    top5 = investable[:TOP_N_RESULTS]
    print(f"[ranker] {len(top5)} picks from {len(investable)} investable candidates")
    return {**state, "top5": top5}
