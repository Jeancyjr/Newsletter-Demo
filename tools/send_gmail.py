#!/usr/bin/env python3
"""Send the newsletter HTML via Gmail SMTP using an app password."""

import json
import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
NEWSLETTER_RECIPIENT = os.getenv("NEWSLETTER_RECIPIENT")


def send_newsletter(recipient: str = None) -> None:
    to_address = recipient or NEWSLETTER_RECIPIENT
    if not to_address:
        raise ValueError("No recipient — set NEWSLETTER_RECIPIENT in .env or pass as argument")

    with open(".tmp/content.json") as f:
        content = json.load(f)

    with open(".tmp/newsletter.html") as f:
        html_body = f.read()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = content["subject"]
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_address

    # Plain-text fallback
    plain_text = (
        f"{content['headline']}\n\n"
        f"{content['intro']}\n\n"
        + "\n\n".join(
            f"{s['heading']}\n{s['body']}" for s in content["sections"]
        )
        + "\n\nKey Takeaways:\n"
        + "\n".join(f"- {t}" for t in content["key_takeaways"])
    )
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        smtp.sendmail(GMAIL_ADDRESS, to_address, msg.as_string())

    print(f"Newsletter sent to {to_address} — Subject: {content['subject']}")


if __name__ == "__main__":
    recipient = sys.argv[1] if len(sys.argv) > 1 else None
    send_newsletter(recipient)
