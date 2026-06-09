# Curated universe of large/mid-cap stocks in safe sectors
# US tickers = plain symbols, UK tickers = suffix .L, ETFs noted separately

UNIVERSE = {
    "consumer_staples": {
        "US": ["PG", "KO", "PEP", "WMT", "COST", "CL", "MKC", "SJM", "HRL"],
        "UK": ["ULVR.L", "TSCO.L", "SBRY.L", "MKS.L", "DGE.L", "ABF.L"],
    },
    "healthcare": {
        "US": ["JNJ", "ABT", "MDT", "TMO", "DHR", "BSX", "BDX", "ZTS", "EW"],
        "UK": ["AZN.L", "GSK.L", "HIK.L", "SMT.L"],
    },
    "utilities": {
        "US": ["NEE", "DUK", "SO", "AEP", "XEL", "ES", "WEC", "CMS", "LNT"],
        "UK": ["NG.L", "SSE.L", "UU.L", "SVT.L", "PNN.L"],
    },
    "industrials": {
        "US": ["HON", "MMM", "ITW", "EMR", "ROK", "ETN", "PH", "GWW", "FAST"],
        "UK": ["RR.L", "BA.L", "IMI.L", "WEIR.L"],
    },
    "technology_bluechip": {
        "US": ["MSFT", "AAPL", "IBM", "CSCO", "ACN", "INTU", "ADP", "PAYX"],
        "UK": ["SAGE.L", "AUTO.L"],
    },
    "financial_bluechip": {
        "US": ["BRK-B", "JPM", "BAC", "WFC", "USB", "TFC", "PNC", "MTB"],
        "UK": ["HSBA.L", "LLOY.L", "BARC.L", "NWG.L", "STAN.L", "LGEN.L"],
    },
    # Blue-chip majors only — avoid small/speculative energy
    "energy_bluechip": {
        "US": ["XOM", "CVX", "COP", "PSX", "EOG", "SLB", "KMI", "OKE"],
        "UK": ["BP.L", "SHEL.L", "TLW.L", "ENQ.L"],
    },
}

# Safe broad-market ETFs (trade like stocks, free data via yfinance)
ETFS = [
    "XLP",    # SPDR Consumer Staples
    "XLV",    # SPDR Healthcare
    "XLU",    # SPDR Utilities
    "XLI",    # SPDR Industrials
    "XLK",    # SPDR Technology (large-cap only)
    "XLF",    # SPDR Financials (blue-chip)
    "XLE",    # SPDR Energy (blue-chip majors)
    "ISF.L",  # iShares FTSE 100
    "VMID.L", # Vanguard FTSE 250
    "VWRL.L", # Vanguard FTSE All-World
    "IWDA.L", # iShares MSCI World
    "CSPX.L", # iShares S&P 500 (London listed)
    "IUKD.L", # iShares UK Dividend
    "INRG.L", # iShares Global Clean Energy (UK-listed)
]

# Benchmark indices used to compare stock drop vs market drop
BENCHMARKS = {
    "US": "^GSPC",   # S&P 500
    "UK": "^FTSE",   # FTSE 100
    "ETF": "^GSPC",  # default to S&P 500
}


def get_all_tickers() -> list[str]:
    tickers = []
    for sector_data in UNIVERSE.values():
        for market_tickers in sector_data.values():
            tickers.extend(market_tickers)
    tickers.extend(ETFS)
    return list(set(tickers))


def get_benchmark(ticker: str) -> str:
    if ticker.endswith(".L"):
        return BENCHMARKS["UK"]
    if ticker in ETFS:
        return BENCHMARKS["ETF"]
    return BENCHMARKS["US"]
