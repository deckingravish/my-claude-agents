from datetime import datetime
from state import AgentState, AnalyzedSecurity

SOURCE_LABEL = {
    "pre_filter_disqualify": "Rule (auto-reject)",
    "pre_filter_macro":      "Rule (macro pattern)",
    "llm":                   "Claude AI",
}


def _format_security(rank: int, s: AnalyzedSecurity) -> str:
    currency = "£" if s["market"] == "UK" else "$"
    rev = s.get("revenue_growth")
    rev_str = f"{rev*100:.1f}%" if rev else "N/A"
    source = SOURCE_LABEL.get(s.get("decision_source", "llm"), "Claude AI")
    return f"""
{'='*55}
#{rank}  {s['name']} ({s['ticker']})
    Sector: {s['sector']}  |  Market: {s['market']}  |  Risk: {s['risk_level']}
    Decision by: {source}
{'='*55}
  Price:         {currency}{s['current_price']}
  52-Week High:  {currency}{s['week52_high']}
  Drop from High: {s['drop_pct']}%  (index: {s.get('index_drop_pct',0):.1f}%)

  What happened:
    {s['event_description']}

  Why still investable:
    {s['investment_reason']}

  P/E: {s.get('pe_ratio') or 'N/A'}  |  Debt/Equity: {s.get('debt_to_equity') or 'N/A'}  |  Rev Growth: {rev_str}
  AI Confidence: {int(s['confidence']*100)}%  |  Score: {s['score']}
"""


def generate_report(state: AgentState) -> AgentState:
    top5 = state["top5"]
    now = datetime.now().strftime("%A, %d %b %Y — %H:%M")
    run_time = state["run_time"]

    # Summary of how decisions were made
    analyzed = state.get("analyzed", [])
    llm_count   = sum(1 for a in analyzed if a.get("decision_source") == "llm")
    rule_count  = sum(1 for a in analyzed if "pre_filter" in a.get("decision_source", ""))

    body = "\n".join(_format_security(i+1, s) for i, s in enumerate(top5)) if top5 else \
           "\nNo investable opportunities found today.\n"

    report = f"""
╔══════════════════════════════════════════════════════╗
║     HYBRID INVESTABLE OPPORTUNITIES REPORT          ║
║  {now:<50}║
║  Session: {run_time:<43}║
╚══════════════════════════════════════════════════════╝
Decision breakdown: {rule_count} by rules (free) | {llm_count} by Claude AI
{body}
Criteria: >5% drop from 52-week high | Large & Mid-cap
Markets: US + UK + Global ETFs | 7 safe sectors
──────────────────────────────────────────────────────
⚠  AI-generated analysis — not financial advice.
"""
    print(f"[report_generator] Report ready | {len(top5)} picks | "
          f"{rule_count} rule-based | {llm_count} LLM-based")
    return {**state, "report_text": report}
