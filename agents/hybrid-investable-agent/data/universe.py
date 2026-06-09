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
    "energy_bluechip": {
        "US": ["XOM", "CVX", "COP", "PSX", "EOG", "SLB", "KMI", "OKE"],
        "UK": ["BP.L", "SHEL.L", "TLW.L", "ENQ.L"],
    },
}

ETFS = [
    "XLP", "XLV", "XLU", "XLI", "XLK", "XLF", "XLE",
    "ISF.L", "VMID.L", "VWRL.L", "IWDA.L", "CSPX.L", "IUKD.L", "INRG.L",
]

BENCHMARKS = {
    "US": "^GSPC",
    "UK": "^FTSE",
    "ETF": "^GSPC",
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
