import requests


def get_sec_filings(ticker: str) -> str:
    """
    Fetches recent 8-K and 10-Q filings from SEC EDGAR.
    Free — no API key needed.
    """
    try:
        # Step 1: Get company CIK from ticker
        resp = requests.get(
            "https://www.sec.gov/files/company_tickers.json",
            headers={"User-Agent": "InvestableAgent research@example.com"},
            timeout=10,
        )
        if resp.status_code != 200:
            return "SEC EDGAR lookup failed."

        companies = resp.json()
        cik = None
        for entry in companies.values():
            if entry.get("ticker", "").upper() == ticker.upper():
                cik = str(entry["cik_str"]).zfill(10)
                break

        if not cik:
            return f"Could not find SEC CIK for ticker {ticker}."

        # Step 2: Fetch recent filings
        filings_resp = requests.get(
            f"https://data.sec.gov/submissions/CIK{cik}.json",
            headers={"User-Agent": "InvestableAgent research@example.com"},
            timeout=10,
        )
        if filings_resp.status_code != 200:
            return "Could not fetch SEC filings."

        data = filings_resp.json()
        recent = data.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        descriptions = recent.get("primaryDocument", [])

        results = []
        for form, date, desc in zip(forms, dates, descriptions):
            if form in ("8-K", "10-Q", "10-K") and len(results) < 6:
                results.append(f"[{date}] {form}: {desc}")

        return "\n".join(results) if results else "No recent 8-K/10-Q/10-K filings found."

    except Exception as e:
        return f"SEC filings error: {str(e)}"
