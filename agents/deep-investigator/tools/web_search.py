import requests
from urllib.parse import quote
from xml.etree import ElementTree as ET


def search_web(query: str, max_results: int = 5) -> str:
    """Free news search via Google News RSS — no API key needed."""
    try:
        url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")[:max_results]
        if not items:
            return "No results found."
        lines = []
        for item in items:
            title = item.findtext("title", "")
            desc  = (item.findtext("description", "") or "")[:200]
            lines.append(f"- {title}: {desc}")
        return "\n".join(lines)
    except Exception as e:
        return f"Web search failed: {str(e)}"
