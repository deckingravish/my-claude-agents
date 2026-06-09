"""
Full pipeline test with real Claude Haiku analysis.
Node 7 (Notifier) is skipped — report is printed to terminal only.

Run: python test_dry_run.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Only set defaults for notification keys — Anthropic key must come from .env
os.environ.setdefault("NEWS_API_KEY", "")
os.environ.setdefault("GMAIL_ADDRESS", "test@gmail.com")
os.environ.setdefault("GMAIL_APP_PASSWORD", "test")
os.environ.setdefault("WHATSAPP_TOKEN", "test")
os.environ.setdefault("WHATSAPP_PHONE_NUMBER_ID", "test")
os.environ.setdefault("WHATSAPP_RECIPIENT_NUMBER", "+447000000000")

from state import AgentState
from nodes.universe_loader import load_universe
from nodes.price_screener import screen_prices
from nodes.news_fetcher import fetch_news
from nodes.ai_analyzer import analyze
from nodes.ranker import rank
from nodes.report_generator import generate_report


def run_test():
    print("\n" + "="*55)
    print("  FULL TEST — Real Claude Haiku | No notifications")
    print("="*55 + "\n")

    state: AgentState = {}

    print("--- Node 1: Universe Loader ---")
    state = load_universe(state)
    print(f"  Tickers loaded: {len(state['universe'])}\n")

    print("--- Node 2: Price Screener (real yfinance data) ---")
    state = screen_prices(state)
    print(f"  Candidates found: {len(state['candidates'])}")
    for c in state["candidates"]:
        print(f"    {c['ticker']}: {c['drop_pct']}% below 52wk high")
    print()

    if not state["candidates"]:
        print("  No candidates passed the >5% filter today.\n")

    print("--- Node 3: News Fetcher ---")
    state = fetch_news(state)
    for c in state["candidates"]:
        print(f"  {c['ticker']}: {len(c['news'])} headlines")
    print()

    print(f"--- Node 4: AI Analyzer (Claude Haiku — {len(state['candidates'])} calls) ---")
    print("  This may take 1-3 minutes...")
    state = analyze(state)
    investable = [a for a in state["analyzed"] if a["investable"]]
    print(f"  {len(investable)}/{len(state['analyzed'])} flagged investable\n")

    print("--- Node 5: Ranker ---")
    state = rank(state)
    print(f"  Top picks: {[s['ticker'] for s in state['top5']]}\n")

    print("--- Node 6: Report Generator ---")
    state = generate_report(state)
    print("\n" + state["report_text"])

    print("--- Node 7: Notifier (SKIPPED — add Gmail/WhatsApp keys to go live) ---\n")

    print("="*55)
    print("  TEST COMPLETE")
    if state.get("errors"):
        print(f"  Non-fatal errors: {len(state['errors'])}")
        for e in state["errors"]:
            print(f"    - {e}")
    print("="*55)


if __name__ == "__main__":
    run_test()
