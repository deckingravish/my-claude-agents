import sys
import yfinance as yf
from langgraph.graph import StateGraph, END
from state import AgentState
from nodes.researcher import researcher
from nodes.tool_executor import tool_executor
from nodes.thesis_writer import thesis_writer


def route_researcher(state: AgentState) -> str:
    """
    Conditional edge — reads the LLM's decision and routes accordingly.
    'call_tool' → tool_executor → back to researcher (the loop)
    'synthesize' → thesis_writer → END
    """
    return state.get("next_action", "synthesize")


def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("researcher",    researcher)
    workflow.add_node("tool_executor", tool_executor)
    workflow.add_node("thesis_writer", thesis_writer)

    workflow.set_entry_point("researcher")

    # ── THE REACT LOOP ────────────────────────────────────────────────────
    # researcher decides → route to tool or synthesis
    workflow.add_conditional_edges(
        "researcher",
        route_researcher,
        {
            "call_tool":  "tool_executor",   # LLM wants more data → run tool
            "synthesize": "thesis_writer",   # LLM has enough → write thesis
        }
    )
    # After tool executes → always go back to researcher for next decision
    workflow.add_edge("tool_executor", "researcher")
    # ─────────────────────────────────────────────────────────────────────

    workflow.add_edge("thesis_writer", END)

    return workflow.compile()


def run_investigation(ticker: str, drop_pct: float = None):
    print(f"\n{'='*60}")
    print(f"  DEEP INVESTIGATION AGENT — {ticker.upper()}")
    print(f"{'='*60}\n")

    # Fetch basic info to seed the state
    try:
        info = yf.Ticker(ticker).info
        company_name = info.get("longName") or info.get("shortName") or ticker
        current      = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        high         = info.get("fiftyTwoWeekHigh", 0)
        sector       = info.get("sector") or "Unknown"
        market       = "UK" if ticker.endswith(".L") else "US"
        calculated_drop = round((high - current) / high * 100, 1) if high else 0
        actual_drop = drop_pct if drop_pct is not None else calculated_drop
    except Exception as e:
        print(f"Could not fetch data for {ticker}: {e}")
        return

    initial_state: AgentState = {
        "ticker":          ticker.upper(),
        "company_name":    company_name,
        "drop_pct":        actual_drop,
        "current_price":   current,
        "week52_high":     high,
        "sector":          sector,
        "market":          market,
        "research_steps":  [],
        "iteration_count": 0,
        "max_iterations":  8,      # max 8 tool calls before forcing synthesis
        "next_action":     "call_tool",
        "next_tool":       None,
        "next_query":      None,
        "next_reasoning":  None,
        "final_thesis":    "",
        "investable_verdict": False,
        "confidence":      0.0,
        "errors":          [],
    }

    print(f"Company:  {company_name}")
    print(f"Drop:     {actual_drop}% from 52wk high of {high}")
    print(f"Price:    {current} | Sector: {sector}\n")
    print("Starting ReAct research loop...\n")

    graph = build_graph()
    final_state = graph.invoke(initial_state)

    print("\n" + final_state["final_thesis"])

    if final_state.get("errors"):
        print(f"\n[{len(final_state['errors'])} non-fatal errors]")
        for e in final_state["errors"]:
            print(f"  - {e}")

    # Save thesis to file
    filename = f"thesis_{ticker.upper()}_{__import__('datetime').date.today()}.txt"
    with open(filename, "w") as f:
        f.write(final_state["final_thesis"])
    print(f"\n[Saved] {filename}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <TICKER> [drop_pct]")
        print("Example: python main.py MSFT 27.4")
        sys.exit(1)

    ticker   = sys.argv[1]
    drop_pct = float(sys.argv[2]) if len(sys.argv) > 2 else None
    run_investigation(ticker, drop_pct)
