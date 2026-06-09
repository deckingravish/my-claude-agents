def search_web(query: str, max_results: int = 5) -> str:
    """Free web search via DuckDuckGo — no API key needed."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        if not results:
            return "No results found."
        lines = [f"- {r['title']}: {r['body'][:200]}" for r in results]
        return "\n".join(lines)
    except Exception as e:
        return f"Web search failed: {str(e)}"
