# Newsletter Automation Workflow

## Objective
Given a topic, research it, write the content, generate an infographic, format it as HTML, and send via Gmail — fully automated.

## Required Inputs
- **Topic**: A string describing the newsletter subject (e.g. "The rise of AI agents in enterprise software")
- **Recipient** (optional): Override email address. Falls back to `NEWSLETTER_RECIPIENT` in `.env`.

## Required Environment Variables (`.env`)
```
ANTHROPIC_API_KEY=       # Claude API — content writing
PERPLEXITY_API_KEY=      # Perplexity sonar-pro — research
KEY_AI_API_KEY=          # Key.ai — Nano Banana infographic generation
KEY_AI_BASE_URL=         # Key.ai API base URL (default: https://api.key.ai/v1)
GMAIL_ADDRESS=           # Sending Gmail address
GMAIL_APP_PASSWORD=      # Gmail app password (not your login password)
NEWSLETTER_RECIPIENT=    # Default recipient email
BRAND_COLOR=             # Optional hex color for header (default: #1a1a2e)
ACCENT_COLOR=            # Optional hex color for accents (default: #e94560)
```

## Pipeline Steps

### Step 1 — Research (`tools/research_topic.py`)
Calls Perplexity `sonar-pro` with the topic. Returns key facts, recent developments, statistics, and expert perspectives. Output: `.tmp/research.json`.

### Step 2 — Write Content (`tools/write_content.py`)
Sends research to Claude (`claude-sonnet-4-6`) with a cached system prompt. Claude returns structured JSON: subject line, preview text, headline, intro, 3–4 sections, key takeaways, infographic prompt, and CTA text. Uses prompt caching on the system prompt to reduce cost on repeated runs. Output: `.tmp/content.json`.

### Step 3 — Generate Infographic (`tools/generate_infographic.py`)
Calls Nano Banana via Key.ai using the `infographic_prompt` from Step 2. Saves the image to `.tmp/infographic.png`. This step is non-blocking — if it fails, the pipeline continues without an image.

### Step 4 — Format HTML (`tools/format_newsletter.py`)
Combines content and infographic into a responsive HTML email. The infographic is base64-embedded (no external hosting needed). Supports brand color customization via `.env`. Output: `.tmp/newsletter.html`.

### Step 5 — Send (`tools/send_gmail.py`)
Sends via Gmail SMTP (port 465, SSL). Includes a plain-text fallback. Output: delivered email.

## Running the Pipeline

**Full pipeline (recommended):**
```bash
cd /path/to/Newsletter-Demo
python tools/run_newsletter.py "Your topic here"
# With a custom recipient:
python tools/run_newsletter.py "Your topic here" recipient@example.com
```

**Individual steps (for debugging):**
```bash
python tools/research_topic.py "Your topic here"
python tools/write_content.py
python tools/generate_infographic.py
python tools/format_newsletter.py
python tools/send_gmail.py
```

## Gmail App Password Setup
1. Go to myaccount.google.com → Security → 2-Step Verification → App passwords
2. Create a new app password (name it "Newsletter")
3. Copy the 16-character password into `.env` as `GMAIL_APP_PASSWORD`

## Key.ai / Nano Banana Setup
1. Sign up at key.ai and get your API key
2. Confirm the base URL for Nano Banana image generation (default assumed: `https://api.key.ai/v1`)
3. Verify the model name is `nano-banana` in their docs; update `tools/generate_infographic.py` if different

## Edge Cases & Known Constraints
- **Perplexity rate limits**: `sonar-pro` has per-minute limits. If you hit them, add a retry with backoff in `research_topic.py`.
- **Infographic failure**: The pipeline continues without an image if Key.ai fails. The HTML email degrades gracefully.
- **Large infographics**: Base64 embedding increases email size. If deliverability is a concern, upload the image to a CDN and use a URL instead.
- **Gmail send limits**: Free Gmail accounts are limited to 500 emails/day. Use Google Workspace for volume.

## Outputs
- `.tmp/research.json` — Raw Perplexity research
- `.tmp/content.json` — Structured newsletter content
- `.tmp/infographic.png` — Generated infographic image
- `.tmp/newsletter.html` — Final HTML email (preview in browser to verify before sending)
