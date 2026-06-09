import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from state import AgentState
from config import (GMAIL_ADDRESS, GMAIL_APP_PASSWORD, EMAIL_RECIPIENT,
                    WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_RECIPIENT_NUMBER)


def _send_email(subject: str, body: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = EMAIL_RECIPIENT
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            s.sendmail(GMAIL_ADDRESS, EMAIL_RECIPIENT, msg.as_string())
        print(f"[notifier] Email sent to {EMAIL_RECIPIENT}")
        return True
    except Exception as e:
        print(f"[notifier] Email failed: {e}")
        return False


def _send_whatsapp(message: str) -> bool:
    if not all([WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_RECIPIENT_NUMBER]):
        print("[notifier] WhatsApp config missing — skipping")
        return False
    try:
        body = message[:4000] + "\n...[see email for full report]" if len(message) > 4000 else message
        resp = requests.post(
            f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages",
            headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"},
            json={"messaging_product": "whatsapp", "to": WHATSAPP_RECIPIENT_NUMBER,
                  "type": "text", "text": {"body": body}},
            timeout=15,
        )
        success = resp.status_code == 200
        print(f"[notifier] WhatsApp {'sent' if success else 'failed: ' + resp.text}")
        return success
    except Exception as e:
        print(f"[notifier] WhatsApp error: {e}")
        return False


def notify(state: AgentState) -> AgentState:
    report = state["report_text"]
    run_time = state["run_time"]
    top5_count = len(state["top5"])
    errors = list(state.get("errors", []))
    subject = f"[{run_time.upper()}] Hybrid Investable Picks — {top5_count} found"
    if not _send_email(subject, report):
        errors.append("notifier: email failed")
    if not _send_whatsapp(report):
        errors.append("notifier: whatsapp failed")
    return {**state, "errors": errors}
