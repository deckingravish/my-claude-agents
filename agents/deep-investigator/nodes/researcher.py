import json
import anthropic
import os
from dotenv import load_dotenv
from state import AgentState

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a thorough investment researcher investigating a stock that has dropped >20%.
Your goal: determine WHY it dropped and WHETHER it is still investable long-term.

You have 5 tools available:
- search_web        : Search news and web for recent events about the stock
- get_sec_filings   : Check SEC filings (8-K material events, 10-Q earnings)
- get_analyst_reports: See what professional analysts think + price targets
- get_financials    : Check balance sheet, revenue growth, debt, cash flow
- get_sector_peers  : Compare drop vs sector peers (stock-specific or market-wide?)

Research strategy:
1. Start with search_web to understand the recent event
2. Use get_sec_filings to check for regulatory/legal filings
3. Use get_sector_peers to judge if peers also dropped (macro) or only this stock
4. Use get_analyst_reports for professional consensus
5. Use get_financials if you need to assess fundamental strength
6. Once you have enough evidence → respond with action: "synthesize"

IMPORTANT:
- You have a maximum number of steps — don't waste them on low-value queries
- If you find clear fraud/ban/criminal evidence → synthesize immediately (NOT investable)
- If you find it's clearly macro → synthesize (probably investable)
- Never repeat the same tool + query twice"""

TOOL_SCHEMA = """
Respond ONLY with JSON (no markdown, no explanation outside JSON):
{
  "reasoning": "Why I am choosing this action based on what I know so far",
  "action": "call_tool" or "synthesize",
  "tool": "search_web | get_sec_filings | get_analyst_reports | get_financials | get_sector_peers",
  "query": "the specific query or ticker to pass to the tool"
}

If action is "synthesize", omit "tool" and "query".
"""


def researcher(state: AgentState) -> AgentState:
    """
    LLM node — the 'brain' of Agent 2.
    Reads all research so far, decides what to investigate next,
    OR decides it has enough to write the thesis.
    """
    iteration = state.get("iteration_count", 0)
    max_iter = state.get("max_iterations", 8)

    # Force synthesis if we hit the iteration cap
    if iteration >= max_iter:
        print(f"[researcher] Max iterations ({max_iter}) reached → forcing synthesis")
        return {**state, "next_action": "synthesize", "iteration_count": iteration}

    # Build context from all research steps so far
    steps = state.get("research_steps", [])
    research_summary = ""
    if steps:
        research_summary = "\n\nResearch conducted so far:\n"
        for i, step in enumerate(steps, 1):
            research_summary += (
                f"\nStep {i} — Tool: {step['tool']} | Query: {step['query']}\n"
                f"Reasoning: {step['reasoning']}\n"
                f"Result: {step['result'][:600]}...\n"
            )
    else:
        research_summary = "\n\nNo research conducted yet — this is your first action."

    prompt = f"""
Stock under investigation: {state['company_name']} ({state['ticker']})
Drop: {state['drop_pct']}% from 52-week high of {state['week52_high']}
Current Price: {state['current_price']} | Sector: {state['sector']} | Market: {state['market']}
Iterations used: {iteration}/{max_iter}
{research_summary}

{TOOL_SCHEMA}
"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        decision = json.loads(raw)

        action = decision.get("action", "synthesize")
        print(f"[researcher] Step {iteration+1}: {action.upper()} "
              f"{'→ ' + decision.get('tool','') if action == 'call_tool' else ''} "
              f"| Reasoning: {decision.get('reasoning','')[:80]}...")

        return {
            **state,
            "next_action":    action,
            "next_tool":      decision.get("tool"),
            "next_query":     decision.get("query"),
            "next_reasoning": decision.get("reasoning", ""),
            "iteration_count": iteration + 1,
        }

    except Exception as e:
        errors = list(state.get("errors", []))
        errors.append(f"researcher step {iteration}: {str(e)}")
        return {**state, "next_action": "synthesize",
                "iteration_count": iteration + 1, "errors": errors}
