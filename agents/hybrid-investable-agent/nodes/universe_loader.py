from data.universe import get_all_tickers
from state import AgentState
from datetime import datetime


def load_universe(state: AgentState) -> AgentState:
    tickers = get_all_tickers()
    run_time = "pre-market" if datetime.now().hour < 12 else "post-market"
    print(f"[universe_loader] {len(tickers)} tickers | run: {run_time}")
    return {
        **state,
        "universe": tickers,
        "candidates": [],
        "analyzed": [],
        "top5": [],
        "report_text": "",
        "run_time": run_time,
        "errors": [],
    }
