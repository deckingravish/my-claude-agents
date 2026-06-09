import requests
import yfinance as yf
from state import AgentState, SecurityData
from config import NEWS_API_KEY


def _yf_news(ticker: str) -> list[str]:
    try:
        news = yf.Ticker(ticker).news or []
        headlines = []
        for item in news[:5]:
            title = (item.get("content") or {}).get("title") or item.get("title", "")
            if title:
                headlines.append(title)
        return headlines
    except Exception:
        return []


def _newsapi(query: str) -> list[str]:
    if not NEWS_API_KEY:
        return []
    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={"q": query, "sortBy": "publishedAt", "pageSize": 5,
                    "language": "en", "apiKey": NEWS_API_KEY},
            timeout=10,
        )
        return [f"{a['title']} — {a['source']['name']}"
                for a in resp.json().get("articles", [])]
    except Exception:
        return []


def fetch_news(state: AgentState) -> AgentState:
    candidates = state["candidates"]
    errors = list(state.get("errors", []))
    updated: list[SecurityData] = []

    print(f"[news_fetcher] Fetching news for {len(candidates)} candidates...")
    for s in candidates:
        try:
            headlines = list(dict.fromkeys(_yf_news(s["ticker"]) + _newsapi(s["name"])))
            updated.append({**s, "news": headlines[:8]})
        except Exception as e:
            errors.append(f"news_fetcher:{s['ticker']}: {str(e)}")
            updated.append(s)

    return {**state, "candidates": updated, "errors": errors}
