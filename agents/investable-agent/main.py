from langgraph.graph import StateGraph, END
from state import AgentState
from nodes.universe_loader import load_universe
from nodes.price_screener import screen_prices
from nodes.news_fetcher import fetch_news
from nodes.ai_analyzer import analyze
from nodes.ranker import rank
from nodes.report_generator import generate_report
from nodes.notifier import notify


def build_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("load_universe", load_universe)
    workflow.add_node("screen_prices", screen_prices)
    workflow.add_node("fetch_news", fetch_news)
    workflow.add_node("analyze", analyze)
    workflow.add_node("rank", rank)
    workflow.add_node("generate_report", generate_report)
    workflow.add_node("notify", notify)

    workflow.set_entry_point("load_universe")
    workflow.add_edge("load_universe", "screen_prices")
    workflow.add_edge("screen_prices", "fetch_news")
    workflow.add_edge("fetch_news", "analyze")
    workflow.add_edge("analyze", "rank")
    workflow.add_edge("rank", "generate_report")
    workflow.add_edge("generate_report", "notify")
    workflow.add_edge("notify", END)

    return workflow.compile()


def run_agent():
    print("\n" + "="*55)
    print("  INVESTABLE SCREENER AGENT STARTING")
    print("="*55)
    graph = build_graph()
    final_state = graph.invoke({})
    errors = final_state.get("errors", [])
    if errors:
        print(f"\n[main] {len(errors)} non-fatal errors:")
        for e in errors:
            print(f"  - {e}")
    print("\n[main] Agent run complete.")


if __name__ == "__main__":
    run_agent()
