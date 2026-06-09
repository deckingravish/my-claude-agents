import schedule
import time
from main import run_agent
from config import PRE_MARKET_TIME, POST_MARKET_TIME

print(f"[scheduler] Agent scheduled at {PRE_MARKET_TIME} and {POST_MARKET_TIME} daily")
print("[scheduler] Press Ctrl+C to stop\n")

schedule.every().day.at(PRE_MARKET_TIME).do(run_agent)
schedule.every().day.at(POST_MARKET_TIME).do(run_agent)

while True:
    schedule.run_pending()
    time.sleep(30)
