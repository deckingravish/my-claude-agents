import json
import anthropic
from state import AgentState, SecurityData, AnalyzedSecurity
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a conservative investment analyst helping a small individual investor.
Your job is to assess whether a stock or ETF that has dropped in price is still worth investing in long-term.

Rules:
- IMMEDIATELY disqualify if news mentions: fraud, accounting scandal, regulatory ban, criminal investigation, CEO arrested, product recall causing permanent damage, or loss of core business license.
- Flag as NOT investable if the drop reflects permanent structural damage to the business.
- Flag as INVESTABLE if the drop is caused by: market-wide selloff, sector rotation, temporary macro fear, one-time earnings miss (not a trend), short-term geopolitical noise, or sentiment overreaction.
- Be conservative — when in doubt, mark as NOT investable.
- Keep explanations simple and clear for a non-expert investor."""

ANALYSIS_SCHEMA = {
    "investable": "boolean — true if safe to buy the dip",
    "event_description": "1-2 sentences: what caused the price drop",
    "investment_reason": "1-2 sentences: why it is (or isn't) a good buy at this price",
    "disqualifiers": "list of strings — fraud/ban/scandal flags found, empty list if none",
    "confidence": "float 0.0-1.0 — how confident you are in this assessment",
    "risk_level": "LOW or MEDIUM only — never HIGH (those are already filtered out)",
}


def _build_prompt(security: SecurityData) -> str:
    headlines = "\n".join(f"  - {h}" for h in security["news"]) or "  No recent news found."
    return f"""
Security: {security['name']} ({security['ticker']})
Sector: {security['sector']} | Market: {security['market']}
Current Price: {security['current_price']} | 52-Week High: {security['week52_high']}
Drop from 52-week high: {security['drop_pct']}%
Index drop over same period: {security['index_drop_pct']}%
P/E Ratio: {security.get('pe_ratio', 'N/A')}
Debt/Equity: {security.get('debt_to_equity', 'N/A')}
Revenue Growth: {security.get('revenue_growth', 'N/A')}

Recent News Headlines:
{headlines}

Respond ONLY with a JSON object matching this schema:
{json.dumps(ANALYSIS_SCHEMA, indent=2)}
"""


def analyze(state: AgentState) -> AgentState:
    candidates = state["candidates"]
    errors = list(state.get("errors", []))
    analyzed: list[AnalyzedSecurity] = []

    print(f"[ai_analyzer] Analyzing {len(candidates)} candidates with Claude...")

    for security in candidates:
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=512,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": _build_prompt(security)}],
            )

            raw = response.content[0].text.strip()
            # Strip markdown code fences if Claude adds them
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            result = json.loads(raw)

            analyzed.append(AnalyzedSecurity(
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
                investable=result.get("investable", False),
                event_description=result.get("event_description", ""),
                investment_reason=result.get("investment_reason", ""),
                disqualifiers=result.get("disqualifiers", []),
                confidence=float(result.get("confidence", 0.5)),
                risk_level=result.get("risk_level", "MEDIUM"),
                score=0.0,  # set by ranker
            ))

        except Exception as e:
            errors.append(f"ai_analyzer:{security['ticker']}: {str(e)}")

    investable_count = sum(1 for a in analyzed if a["investable"])
    print(f"[ai_analyzer] {investable_count}/{len(analyzed)} flagged as investable")

    return {**state, "analyzed": analyzed, "errors": errors}
