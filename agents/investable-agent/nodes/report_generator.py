from datetime import datetime
from state import AgentState, AnalyzedSecurity


def _format_metric(value, suffix="", prefix="") -> str:
    if value is None:
        return "N/A"
    return f"{prefix}{value}{suffix}"


def _format_market_cap(cap) -> str:
    if not cap:
        return "N/A"
    if cap >= 1_000_000_000_000:
        return f"${cap/1_000_000_000_000:.1f}T"
    if cap >= 1_000_000_000:
        return f"${cap/1_000_000_000:.1f}B"
    return f"${cap/1_000_000:.0f}M"


def _format_security(rank: int, s: AnalyzedSecurity) -> str:
    currency = "£" if s["market"] == "UK" else "$"
    rev_growth = s.get("revenue_growth")
    rev_str = f"{rev_growth*100:.1f}%" if rev_growth else "N/A"

    return f"""
{'='*55}
#{rank}  {s['name']} ({s['ticker']})
    Sector: {s['sector']}  |  Market: {s['market']}  |  Risk: {s['risk_level']}
{'='*55}
  Price:         {currency}{s['current_price']}
  52-Week High:  {currency}{s['week52_high']}
  Drop from High: {s['drop_pct']}%  (index moved: {s.get('index_drop_pct', 0):.1f}%)

  What happened:
    {s['event_description']}

  Why still investable:
    {s['investment_reason']}

  Key Metrics:
    P/E Ratio:       {_format_metric(s.get('pe_ratio'), 'x')}
    Debt/Equity:     {_format_metric(s.get('debt_to_equity'))}
    Revenue Growth:  {rev_str}

  AI Confidence: {int(s['confidence']*100)}%  |  Score: {s['score']}
"""


def generate_report(state: AgentState) -> AgentState:
    top5 = state["top5"]
    run_time = state["run_time"]
    now = datetime.now().strftime("%A, %d %b %Y — %H:%M")

    if not top5:
        body = "\nNo investable opportunities found today matching your criteria.\nCheck back at the next run.\n"
    else:
        body = "\n".join(_format_security(i + 1, s) for i, s in enumerate(top5))

    errors = state.get("errors", [])
    error_section = ""
    if errors:
        error_section = f"\n\n[{len(errors)} non-fatal errors during run — check logs]\n"

    report = f"""
╔══════════════════════════════════════════════════════╗
║       DAILY INVESTABLE OPPORTUNITIES REPORT         ║
║  {now:<50}║
║  Session: {run_time:<43}║
╚══════════════════════════════════════════════════════╝
{body}{error_section}
Criteria: >5% drop from 52-week high | Large & Mid-cap
Sectors:  Consumer Staples, Healthcare, Utilities,
          Industrials, Technology (blue-chip),
          Financial (blue-chip), Energy (blue-chip)
Markets:  US + UK + Global ETFs
──────────────────────────────────────────────────────
⚠  This is AI-generated analysis, not financial advice.
   Always do your own research before investing.
"""

    print(f"[report_generator] Report generated with {len(top5)} picks")
    return {**state, "report_text": report}
