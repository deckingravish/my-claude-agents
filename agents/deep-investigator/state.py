from typing import TypedDict, Optional


class ResearchStep(TypedDict):
    tool: str          # which tool was called
    query: str         # what was queried
    result: str        # what came back (truncated to 800 chars)
    reasoning: str     # why the LLM chose this tool


class AgentState(TypedDict):
    ticker: str
    company_name: str
    drop_pct: float
    current_price: float
    week52_high: float
    sector: str
    market: str
    research_steps: list[ResearchStep]   # grows with each tool call
    iteration_count: int
    max_iterations: int                  # safety cap
    next_action: str                     # "call_tool" | "synthesize"
    next_tool: Optional[str]
    next_query: Optional[str]
    next_reasoning: Optional[str]
    final_thesis: str
    investable_verdict: bool
    confidence: float
    errors: list[str]
