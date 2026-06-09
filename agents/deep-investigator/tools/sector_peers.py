import yfinance as yf

# Curated peer groups by sector for quick comparison
PEER_MAP = {
    "Technology":         ["MSFT", "AAPL", "GOOGL", "IBM", "ACN"],
    "Healthcare":         ["JNJ", "ABT", "MDT", "TMO", "ZTS"],
    "Consumer Staples":   ["PG", "KO", "PEP", "UL", "WMT"],
    "Utilities":          ["NEE", "DUK", "SO", "AEP", "NG.L"],
    "Industrials":        ["HON", "MMM", "ITW", "EMR", "GE"],
    "Financial Services": ["JPM", "BAC", "WFC", "BRK-B", "HSBA.L"],
    "Energy":             ["XOM", "CVX", "BP.L", "SHEL.L", "COP"],
}


def get_sector_peers(ticker: str) -> str:
    """Compares the stock's drop with its sector peers to see if it's stock-specific."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        sector = info.get("sector", "")
        peers = PEER_MAP.get(sector, [])

        if not peers:
            return f"No peer group defined for sector: {sector}"

        # Remove the ticker itself from peers
        peers = [p for p in peers if p.upper() != ticker.upper()][:4]

        lines = [f"Sector: {sector}", f"Comparing {ticker} vs peers: {', '.join(peers)}", ""]

        for peer in peers:
            try:
                p_info = yf.Ticker(peer).info
                p_current = p_info.get("currentPrice") or p_info.get("regularMarketPrice", 0)
                p_high = p_info.get("fiftyTwoWeekHigh", 0)
                if p_current and p_high:
                    p_drop = round((p_high - p_current) / p_high * 100, 1)
                    lines.append(f"  {peer}: {p_drop}% below 52wk high (now: {p_current})")
            except Exception:
                lines.append(f"  {peer}: data unavailable")

        # The key insight: if peers are also down similarly → sector-wide, not stock-specific
        lines.append(
            f"\nInsight: If {ticker}'s drop ({info.get('fiftyTwoWeekHigh',0)}) "
            "is much larger than peers → stock-specific issue. "
            "If similar → sector-wide or macro."
        )

        return "\n".join(lines)

    except Exception as e:
        return f"Sector peers error: {str(e)}"
