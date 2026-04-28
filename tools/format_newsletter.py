#!/usr/bin/env python3
"""Format newsletter content + infographic into an HTML email. Saves to .tmp/newsletter.html."""

import base64
import json
import os
from datetime import date
from dotenv import load_dotenv

load_dotenv()

BRAND_COLOR = os.getenv("BRAND_COLOR", "#1a1a2e")
ACCENT_COLOR = os.getenv("ACCENT_COLOR", "#e94560")


def build_sections_html(sections: list) -> str:
    parts = []
    for section in sections:
        parts.append(f"""
        <div style="margin-bottom:32px;">
          <h2 style="color:{BRAND_COLOR};font-size:20px;font-weight:700;margin:0 0 12px;">
            {section['heading']}
          </h2>
          <p style="color:#444;font-size:16px;line-height:1.7;margin:0;">
            {section['body'].replace(chr(10), '<br>')}
          </p>
        </div>""")
    return "\n".join(parts)


def build_takeaways_html(takeaways: list) -> str:
    items = "".join(
        f'<li style="margin-bottom:10px;color:#444;font-size:15px;">{t}</li>'
        for t in takeaways
    )
    return f"<ul style='padding-left:20px;margin:0;'>{items}</ul>"


def build_citations_html(citations: list) -> str:
    if not citations:
        return ""
    items = "".join(
        f'<li style="margin-bottom:4px;"><a href="{c}" style="color:{ACCENT_COLOR};font-size:13px;">{c}</a></li>'
        for c in citations[:5]
    )
    return f"""
    <div style="margin-top:32px;padding-top:20px;border-top:1px solid #eee;">
      <p style="color:#999;font-size:13px;margin:0 0 8px;font-weight:600;">SOURCES</p>
      <ul style="padding-left:16px;margin:0;">{items}</ul>
    </div>"""


def format_newsletter() -> str:
    with open(".tmp/content.json") as f:
        content = json.load(f)

    # Embed infographic as base64 if it exists
    infographic_html = ""
    if os.path.exists(".tmp/infographic.png"):
        with open(".tmp/infographic.png", "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        infographic_html = f"""
        <div style="margin:32px 0;text-align:center;">
          <img src="data:image/png;base64,{b64}"
               alt="Newsletter infographic"
               style="max-width:100%;height:auto;border-radius:8px;" />
        </div>"""

    today = date.today().strftime("%B %d, %Y")
    sections_html = build_sections_html(content["sections"])
    takeaways_html = build_takeaways_html(content["key_takeaways"])
    citations_html = build_citations_html(content.get("citations", []))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{content['subject']}</title>
</head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">

  <!-- Preheader (hidden preview text) -->
  <span style="display:none;max-height:0;overflow:hidden;">{content['preview_text']}</span>

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:{BRAND_COLOR};padding:32px 40px;border-radius:8px 8px 0 0;text-align:center;">
              <p style="color:rgba(255,255,255,0.6);font-size:12px;letter-spacing:2px;text-transform:uppercase;margin:0 0 8px;">NEWSLETTER &bull; {today}</p>
              <h1 style="color:#fff;font-size:28px;font-weight:800;margin:0;line-height:1.3;">{content['headline']}</h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#fff;padding:40px;">

              <!-- Intro -->
              <p style="color:#333;font-size:17px;line-height:1.7;margin:0 0 32px;font-weight:500;">{content['intro']}</p>

              {infographic_html}

              {sections_html}

              <!-- Key Takeaways -->
              <div style="background:#f9f9f9;border-left:4px solid {ACCENT_COLOR};padding:24px;border-radius:0 8px 8px 0;margin-bottom:32px;">
                <p style="color:{BRAND_COLOR};font-size:13px;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin:0 0 16px;">KEY TAKEAWAYS</p>
                {takeaways_html}
              </div>

              <!-- CTA -->
              <div style="text-align:center;margin-top:8px;">
                <a href="#" style="display:inline-block;background:{ACCENT_COLOR};color:#fff;text-decoration:none;padding:14px 32px;border-radius:6px;font-size:16px;font-weight:700;">{content['cta_text']}</a>
              </div>

              {citations_html}

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f5f5f5;padding:24px 40px;text-align:center;border-radius:0 0 8px 8px;">
              <p style="color:#aaa;font-size:12px;margin:0;">You're receiving this because you subscribed. <a href="#" style="color:#aaa;">Unsubscribe</a></p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>

</body>
</html>"""

    with open(".tmp/newsletter.html", "w") as f:
        f.write(html)

    print(f"Newsletter HTML saved to .tmp/newsletter.html")
    return ".tmp/newsletter.html"


if __name__ == "__main__":
    format_newsletter()
