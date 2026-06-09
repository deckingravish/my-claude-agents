import yfinance as yf


def get_financials(ticker: str) -> str:
    """Returns key financial metrics and recent income/balance sheet data."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        lines = []

        metrics = {
            "Market Cap":       info.get("marketCap"),
            "P/E Ratio":        info.get("trailingPE"),
            "Forward P/E":      info.get("forwardPE"),
            "P/S Ratio":        info.get("priceToSalesTrailing12Months"),
            "P/B Ratio":        info.get("priceToBook"),
            "Debt/Equity":      info.get("debtToEquity"),
            "Current Ratio":    info.get("currentRatio"),
            "ROE":              info.get("returnOnEquity"),
            "ROA":              info.get("returnOnAssets"),
            "Revenue Growth":   info.get("revenueGrowth"),
            "Earnings Growth":  info.get("earningsGrowth"),
            "Profit Margin":    info.get("profitMargins"),
            "Free Cash Flow":   info.get("freeCashflow"),
            "Dividend Yield":   info.get("dividendYield"),
        }

        lines.append("Key Financial Metrics:")
        for name, val in metrics.items():
            if val is not None:
                if name in ("Market Cap", "Free Cash Flow") and isinstance(val, (int, float)):
                    val = f"${val/1e9:.1f}B" if abs(val) >= 1e9 else f"${val/1e6:.0f}M"
                elif name in ("Revenue Growth", "Earnings Growth", "Profit Margin",
                              "ROE", "ROA", "Dividend Yield") and isinstance(val, float):
                    val = f"{val*100:.1f}%"
                lines.append(f"  {name}: {val}")

        # Last 2 years revenue from income statement
        try:
            income = t.income_stmt
            if income is not None and not income.empty and "Total Revenue" in income.index:
                rev_row = income.loc["Total Revenue"].head(2)
                lines.append("\nAnnual Revenue (recent 2 years):")
                for col, val in rev_row.items():
                    lines.append(f"  {col.year}: ${val/1e9:.2f}B")
        except Exception:
            pass

        return "\n".join(lines) if lines else "No financial data available."

    except Exception as e:
        return f"Financials error: {str(e)}"
