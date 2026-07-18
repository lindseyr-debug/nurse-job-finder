"""Send a text-message alert (via email-to-SMS gateway) when new jobs are found.

Credentials are read from a local .env file that is never committed to git
(see .gitignore) and is never shared with anyone else -- create your own
by copying .env.example to .env and filling in your own values.
"""

import os
import smtplib
from email.mime.text import MIMEText

from dotenv import load_dotenv

import config

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send_new_job_alert(new_jobs):
    """Send a short text listing the top new matches. Silently no-ops if unconfigured."""
    if not new_jobs:
        return

    gmail_address = os.environ.get("GMAIL_ADDRESS")
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
    phone_gateway = os.environ.get("PHONE_GATEWAY")

    if not all([gmail_address, gmail_app_password, phone_gateway]):
        print("  [notifier] Skipping text alert -- .env not configured. See .env.example.")
        return

    # Keep this short -- Verizon's email-to-SMS gateway silently truncates
    # long messages instead of splitting them, so the link must come first
    # and the whole thing must comfortably fit in one text.
    body = f"{len(new_jobs)} new Chicago RN job(s): {config.DASHBOARD_URL}"

    message = MIMEText(body)
    message["From"] = gmail_address
    message["To"] = phone_gateway
    message["Subject"] = ""  # carrier gateways usually ignore/strip the subject

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(gmail_address, gmail_app_password)
            server.sendmail(gmail_address, [phone_gateway], message.as_string())
        print("  [notifier] Text alert sent.")
    except smtplib.SMTPException as exc:
        print(f"  [notifier] Failed to send text alert: {exc}")
