import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
NEWS_API_KEY      = os.getenv("NEWS_API_KEY")

GMAIL_ADDRESS      = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_RECIPIENT    = os.getenv("EMAIL_RECIPIENT", "deckingravish@gmail.com")

WHATSAPP_TOKEN            = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID  = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_RECIPIENT_NUMBER = os.getenv("WHATSAPP_RECIPIENT_NUMBER")

DROP_THRESHOLD_PCT = 5.0
TOP_N_RESULTS      = 5
PRE_MARKET_TIME    = "07:00"
POST_MARKET_TIME   = "18:00"
