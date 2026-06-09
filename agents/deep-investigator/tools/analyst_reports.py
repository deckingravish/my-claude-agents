import yfinance as yf


def get_analyst_reports(ticker: str) -> str:
    """Returns analyst ratings and recent upgrades/downgrades via yfinance."""
    try:
        t = yf.Ticker(ticker)
        lines = []

        info = t.info
        target_high = info.get("targetHighPrice")
        target_low = info.get("targetLowPrice")
        target_mean = info.get("targetMeanPrice")
        recommendation = info.get("recommendationKey", "N/A")
        num_analysts = info.get("numberOfAnalystOpinions", "N/A")
        current = info.get("currentPrice") or info.get("regularMarketPrice", 0)

        lines.append(f"Analyst Consensus: {recommendation.upper()} ({num_analysts} analysts)")
        if target_mean and current:
            upside = round((target_mean - current) / current * 100, 1)
            lines.append(f"Price Targets: Low ${target_low} | Mean ${target_mean} | High ${target_high}")
            lines.append(f"Implied upside from current price: {upside}%")

        # Recent upgrades/downgrades
        try:
            updown = t.upgrades_downgrades
            if updown is not None and not updown.empty:
                recent = updown.head(5)
                lines.append("\nRecent Upgrades/Downgrades:")
                for idx, row in recent.iterrows():
                    lines.append(f"  [{idx.date()}] {row.get('Firm','?')}: "
                                 f"{row.get('FromGrade','?')} → {row.get('ToGrade','?')} "
                                 f"({row.get('Action','?')})")
        except Exception:
            pass

        return "\n".join(lines) if lines else "No analyst data available."

    except Exception as e:
        return f"Analyst reports error: {str(e)}"
