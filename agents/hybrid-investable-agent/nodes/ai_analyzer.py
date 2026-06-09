import json
import anthropic
from state import AgentState, SecurityData, AnalyzedSecurity
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a conservative investment analyst for a small individual investor.
Assess whether a stock drop is a buying opportunity or a warning sign.

DISQUALIFY immediately if news mentions: fraud, regulatory ban, criminal investigation,
CEO arrested, product recall causing permanent damage, or loss of core business license.

Mark INVESTABLE if drop is caused by: temporary macro fear, one-time earnings miss,
short-term sentiment, sector rotation, or geopolitical noise that doesn't harm fundamentals.

Be conservative — when in doubt, mark NOT investable. Keep explanations simple."""


def _build_prompt(s: SecurityData) -> str:
    headlines = "\n".join(f"  - {h}" for h in s["news"]) or "  No recent news."
    return f"""
Security: {s['name']} ({s['ticker']}) | Sector: {s['sector']} | Market: {s['market']}
Price: {s['current_price']} | 52-Week High: {s['week52_high']} | Drop: {s['drop_pct']}%
Index drop same period: {s['index_drop_pct']}%
P/E: {s.get('pe_ratio','N/A')} | Debt/Equity: {s.get('debt_to_equity','N/A')} | Revenue Growth: {s.get('revenue_growth','N/A')}

Recent Headlines:
{headlines}

Respond ONLY with JSON:
{{
  "investable": true/false,
  "event_description": "1-2 sentences on what caused the drop",
  "investment_reason": "1-2 sentences on why investable or not",
  "disqualifiers": ["list any fraud/ban/scandal signals, empty if none"],
  "confidence": 0.0-1.0,
  "risk_level": "LOW or MEDIUM"
}}"""


def analyze(state: AgentState) -> AgentState:
    candidates = state["candidates"]   # only ambiguous ones reach here
    existing = list(state.get("analyzed", []))
    errors = list(state.get("errors", []))
    llm_results: list[AnalyzedSecurity] = []

    print(f"[ai_analyzer] Claude judging {len(candidates)} ambiguous candidates...")

    for s in candidates:
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=512,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": _build_prompt(s)}],
            )
            raw = response.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            result = json.loads(raw)

            llm_results.append(AnalyzedSecurity(
                ticker=s["ticker"], name=s["name"], sector=s["sector"],
                market=s["market"], current_price=s["current_price"],
                week52_high=s["week52_high"], drop_pct=s["drop_pct"],
                pe_ratio=s.get("pe_ratio"), debt_to_equity=s.get("debt_to_equity"),
                revenue_growth=s.get("revenue_growth"),
                investable=result.get("investable", False),
                event_description=result.get("event_description", ""),
                investment_reason=result.get("investment_reason", ""),
                disqualifiers=result.get("disqualifiers", []),
                confidence=float(result.get("confidence", 0.5)),
                risk_level=result.get("risk_level", "MEDIUM"),
                score=0.0,
                decision_source="llm",
            ))
        except Exception as e:
            errors.append(f"ai_analyzer:{s['ticker']}: {str(e)}")

    all_analyzed = existing + llm_results
    investable = sum(1 for a in all_analyzed if a["investable"])
    print(f"[ai_analyzer] Total analyzed: {len(all_analyzed)} | "
          f"Investable: {investable} | LLM calls made: {len(llm_results)}")

    return {**state, "analyzed": all_analyzed, "candidates": [], "errors": errors}
