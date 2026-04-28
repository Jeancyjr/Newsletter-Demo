#!/usr/bin/env python3
"""Orchestrator: runs the full newsletter pipeline for a given topic."""

import sys
from research_topic import research_topic
from write_content import write_content
from generate_infographic import generate_infographic
from format_newsletter import format_newsletter
from send_gmail import send_newsletter


def run(topic: str, recipient: str = None) -> None:
    print(f"\n=== Newsletter Pipeline: {topic} ===\n")

    print("[1/5] Researching topic with Perplexity...")
    research_topic(topic)

    print("\n[2/5] Writing content with Claude...")
    write_content()

    print("\n[3/5] Generating infographic with Nano Banana...")
    try:
        generate_infographic()
    except Exception as e:
        print(f"  Warning: infographic generation failed ({e}). Continuing without image.")

    print("\n[4/5] Formatting HTML newsletter...")
    format_newsletter()

    print("\n[5/5] Sending via Gmail...")
    send_newsletter(recipient)

    print("\n=== Done ===")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/run_newsletter.py '<topic>' [recipient@email.com]")
        sys.exit(1)
    topic = sys.argv[1]
    recipient = sys.argv[2] if len(sys.argv) > 2 else None
    run(topic, recipient)
