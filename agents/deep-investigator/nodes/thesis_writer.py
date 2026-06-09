import json
import anthropic
import os
from dotenv import load_dotenv
from state import AgentState

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a senior investment analyst writing a final investment thesis
for a small individual investor. Be clear, honest, and conservative.
If evidence is mixed, say so. Never overstate confidence."""


def thesis_writer(state: AgentState) -> AgentState:
    """
    LLM node — called once at the end.
    Synthesizes all research steps into a final investment thesis.
    """
    steps = state.get("research_steps", [])
    research_text = "\n\n".join(
        f"[{s['tool']}] Query: {s['query']}\nFindings: {s['result']}"
        for s in steps
    ) or "No research was conducted."

    prompt = f"""
Stock: {state['company_name']} ({state['ticker']})
Drop: {state['drop_pct']}% from 52-week high | Current: {state['current_price']}
Sector: {state['sector']} | Market: {state['market']}

RESEARCH CONDUCTED:
{research_text}

Write a complete investment thesis. Respond ONLY with JSON:
{{
  "investable": true or false,
  "confidence": 0.0-1.0,
  "verdict_summary": "One sentence buy/avoid verdict",
  "what_happened": "2-3 sentences explaining the drop clearly",
  "bull_case": "2-3 sentences — why it could recover",
  "bear_case": "2-3 sentences — what could go wrong",
  "key_risks": ["list", "of", "specific", "risks"],
  "recommendation": "Specific action: e.g. 'Consider buying in tranches below $X', or 'Avoid until Q3 earnings clarify...'",
  "time_horizon": "Short (< 1yr) / Medium (1-3yr) / Long (3yr+)"
}}"""

    errors = list(state.get("errors", []))

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        thesis = json.loads(raw)

        # Format into readable report
        risks = "\n".join(f"    • {r}" for r in thesis.get("key_risks", []))
        formatted = f"""
{'═'*60}
  DEEP INVESTIGATION THESIS: {state['company_name']} ({state['ticker']})
{'═'*60}

  VERDICT: {'✅ INVESTABLE' if thesis['investable'] else '❌ AVOID'}
  Confidence: {int(thesis['confidence']*100)}%
  Time Horizon: {thesis.get('time_horizon','N/A')}

  Summary:
    {thesis.get('verdict_summary','')}

  What Happened:
    {thesis.get('what_happened','')}

  Bull Case (why it recovers):
    {thesis.get('bull_case','')}

  Bear Case (what could go wrong):
    {thesis.get('bear_case','')}

  Key Risks:
{risks}

  Recommendation:
    {thesis.get('recommendation','')}

  Research depth: {len(steps)} tool calls | Drop: {state['drop_pct']}%
{'─'*60}
⚠  AI-generated thesis — not financial advice.
"""
        print(f"[thesis_writer] Thesis complete — "
              f"{'INVESTABLE' if thesis['investable'] else 'AVOID'} "
              f"({int(thesis['confidence']*100)}% confidence)")

        return {
            **state,
            "final_thesis":      formatted,
            "investable_verdict": thesis.get("investable", False),
            "confidence":         float(thesis.get("confidence", 0.5)),
            "errors":             errors,
        }

    except Exception as e:
        errors.append(f"thesis_writer: {str(e)}")
        return {**state, "final_thesis": "Thesis generation failed.",
                "investable_verdict": False, "confidence": 0.0, "errors": errors}
