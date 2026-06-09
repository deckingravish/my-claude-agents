from langgraph.graph import StateGraph, END
from state import AgentState
from nodes.universe_loader import load_universe
from nodes.price_screener import screen_prices
from nodes.news_fetcher import fetch_news
from nodes.pre_filter import pre_filter, route_after_pre_filter
from nodes.ai_analyzer import analyze
from nodes.ranker import rank
from nodes.report_generator import generate_report
from nodes.notifier import notify


def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("load_universe",    load_universe)
    workflow.add_node("screen_prices",    screen_prices)
    workflow.add_node("fetch_news",       fetch_news)
    workflow.add_node("pre_filter",       pre_filter)
    workflow.add_node("analyze",          analyze)
    workflow.add_node("rank",             rank)
    workflow.add_node("generate_report",  generate_report)
    workflow.add_node("notify",           notify)

    workflow.set_entry_point("load_universe")
    workflow.add_edge("load_universe",   "screen_prices")
    workflow.add_edge("screen_prices",   "fetch_news")
    workflow.add_edge("fetch_news",      "pre_filter")

    # ── THE HYBRID CONDITIONAL EDGE ──────────────────────────────────────
    # pre_filter decides: ambiguous candidates exist → LLM, else → ranker
    workflow.add_conditional_edges(
        "pre_filter",
        route_after_pre_filter,
        {
            "analyze": "analyze",   # LLM path — only for ambiguous stocks
            "rank":    "rank",      # skip LLM entirely if rules handled everything
        }
    )
    # ─────────────────────────────────────────────────────────────────────

    workflow.add_edge("analyze",         "rank")
    workflow.add_edge("rank",            "generate_report")
    workflow.add_edge("generate_report", "notify")
    workflow.add_edge("notify",          END)

    return workflow.compile()


def run_agent():
    print("\n" + "="*55)
    print("  HYBRID INVESTABLE SCREENER — STARTING")
    print("="*55)
    graph = build_graph()
    final_state = graph.invoke({})
    if final_state.get("errors"):
        print(f"\n[{len(final_state['errors'])} non-fatal errors]")
        for e in final_state["errors"]:
            print(f"  - {e}")
    print("\n[main] Done.")


if __name__ == "__main__":
    run_agent()
