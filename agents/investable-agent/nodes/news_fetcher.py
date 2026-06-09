import requests
import yfinance as yf
from state import AgentState, SecurityData
from config import NEWS_API_KEY


def _fetch_newsapi(query: str) -> list[str]:
    if not NEWS_API_KEY:
        return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "pageSize": 5,
            "language": "en",
            "apiKey": NEWS_API_KEY,
        }
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            return []
        articles = resp.json().get("articles", [])
        return [f"{a['title']} — {a['source']['name']}" for a in articles]
    except Exception:
        return []


def _fetch_yfinance_news(ticker: str) -> list[str]:
    try:
        t = yf.Ticker(ticker)
        news = t.news or []
        headlines = []
        for item in news[:5]:
            # yfinance 0.2.x+ nests title under content.title; older versions use top-level title
            title = (item.get("content") or {}).get("title") or item.get("title", "")
            if title:
                headlines.append(title)
        return headlines
    except Exception:
        return []


def fetch_news(state: AgentState) -> AgentState:
    candidates = state["candidates"]
    errors = list(state.get("errors", []))
    updated: list[SecurityData] = []

    print(f"[news_fetcher] Fetching news for {len(candidates)} candidates...")

    for security in candidates:
        try:
            yf_headlines = _fetch_yfinance_news(security["ticker"])
            # Use company name for NewsAPI to get broader coverage
            api_headlines = _fetch_newsapi(security["name"])
            all_headlines = list(dict.fromkeys(yf_headlines + api_headlines))  # dedupe
            updated.append({**security, "news": all_headlines[:8]})
        except Exception as e:
            errors.append(f"news_fetcher:{security['ticker']}: {str(e)}")
            updated.append(security)

    print(f"[news_fetcher] News fetched for all candidates")
    return {**state, "candidates": updated, "errors": errors}
