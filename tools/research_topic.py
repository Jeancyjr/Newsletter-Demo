#!/usr/bin/env python3
"""Research a topic using Perplexity API and save results to .tmp/research.json."""

import sys
import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
API_URL = "https://api.perplexity.ai/chat/completions"


def research_topic(topic: str) -> dict:
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a research assistant. Given a topic, provide comprehensive, "
                    "factual research suitable for a professional newsletter. Include: "
                    "key facts, recent developments, statistics, expert perspectives, "
                    "and actionable insights. Be thorough and cite sources where possible."
                ),
            },
            {
                "role": "user",
                "content": f"Research this newsletter topic thoroughly: {topic}",
            },
        ],
        "max_tokens": 4000,
        "return_citations": True,
        "return_related_questions": False,
    }

    response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()

    research_text = data["choices"][0]["message"]["content"]
    citations = data.get("citations", [])

    result = {
        "topic": topic,
        "research": research_text,
        "citations": citations,
    }

    os.makedirs(".tmp", exist_ok=True)
    with open(".tmp/research.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Research saved to .tmp/research.json ({len(research_text)} chars)")
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/research_topic.py '<topic>'")
        sys.exit(1)
    topic = " ".join(sys.argv[1:])
    research_topic(topic)
