#!/usr/bin/env python3
"""Use Claude to write newsletter content from research. Saves to .tmp/content.json."""

import json
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are an expert newsletter writer. Given research on a topic, you write
engaging, professional newsletter content. Your writing is clear, insightful, and valuable
to the reader. You avoid jargon, use active voice, and always include actionable takeaways.

You must respond with ONLY valid JSON matching this exact structure:
{
  "subject": "Email subject line (compelling, under 60 chars)",
  "preview_text": "Email preview text (under 100 chars)",
  "headline": "Main newsletter headline",
  "intro": "Opening paragraph (2-3 sentences, hooks the reader)",
  "sections": [
    {"heading": "Section heading", "body": "Section content (2-4 paragraphs)"}
  ],
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
  "infographic_prompt": "A detailed prompt for generating an infographic image that visualizes the key data or concept from this newsletter",
  "cta_text": "Call-to-action button text (5-8 words)"
}

Include 3-4 sections. Make the infographic_prompt specific and visual."""


def write_content() -> dict:
    with open(".tmp/research.json") as f:
        research = json.load(f)

    user_message = (
        f"Topic: {research['topic']}\n\n"
        f"Research:\n{research['research']}\n\n"
        f"Write a compelling newsletter based on this research."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    content = json.loads(raw)
    content["topic"] = research["topic"]
    content["citations"] = research.get("citations", [])

    with open(".tmp/content.json", "w") as f:
        json.dump(content, f, indent=2)

    usage = response.usage
    print(
        f"Content written. Tokens: {usage.input_tokens} in / {usage.output_tokens} out "
        f"(cache read: {getattr(usage, 'cache_read_input_tokens', 0)})"
    )
    print(f"Subject: {content['subject']}")
    return content


if __name__ == "__main__":
    write_content()
