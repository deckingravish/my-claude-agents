from state import AgentState, ResearchStep
from tools.web_search import search_web
from tools.sec_filings import get_sec_filings
from tools.analyst_reports import get_analyst_reports
from tools.financials import get_financials
from tools.sector_peers import get_sector_peers

TOOL_REGISTRY = {
    "search_web":           search_web,
    "get_sec_filings":      get_sec_filings,
    "get_analyst_reports":  get_analyst_reports,
    "get_financials":       get_financials,
    "get_sector_peers":     get_sector_peers,
}


def tool_executor(state: AgentState) -> AgentState:
    """
    Skill node — no LLM.
    Receives the tool + query chosen by the researcher node,
    executes it, appends the result to research_steps, returns updated state.
    """
    tool_name = state.get("next_tool")
    query     = state.get("next_query") or state["ticker"]
    reasoning = state.get("next_reasoning", "")

    if tool_name not in TOOL_REGISTRY:
        errors = list(state.get("errors", []))
        errors.append(f"tool_executor: unknown tool '{tool_name}'")
        return {**state, "errors": errors}

    print(f"[tool_executor] Running {tool_name}('{query}')...")
    try:
        result = TOOL_REGISTRY[tool_name](query)
    except Exception as e:
        result = f"Tool failed: {str(e)}"

    step = ResearchStep(
        tool=tool_name,
        query=query,
        result=result[:800],    # cap at 800 chars to keep state manageable
        reasoning=reasoning,
    )

    updated_steps = list(state.get("research_steps", [])) + [step]
    print(f"[tool_executor] Got {len(result)} chars — research steps: {len(updated_steps)}")

    return {**state, "research_steps": updated_steps}
