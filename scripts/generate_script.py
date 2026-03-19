"""
Step 1: Generate video script using FREE Google Gemini API
Get your free API key at: https://aistudio.google.com/app/apikey
"""

import os
import json
import urllib.request
import urllib.error
import logging

log = logging.getLogger(__name__)

# ─── CONFIG ──────────────────────────────────────────────────────
# Paste your free Gemini API key here (from https://aistudio.google.com)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyACKA2vkXXuGxjvRxxMHHo9m9k2OFSeaiE")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash-lite:generateContent?key=" + GEMINI_API_KEY
)

PROMPT_TEMPLATE = """You are a YouTube content creator. Create a complete video package for the topic: "{topic}"

Return ONLY a valid JSON object with these exact keys:
{{
  "title": "Catchy YouTube title (max 60 chars)",
  "script": "Full video narration script (150-200 words, engaging, clear, no timestamps)",
  "description": "YouTube video description (2-3 sentences + relevant hashtags)",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "hook": "First sentence to grab attention",
  "sections": ["Section 1 title", "Section 2 title", "Section 3 title"]
}}

Rules:
- Script must flow naturally when spoken aloud
- Start with the hook to grab attention immediately
- End with a call to action (like and subscribe)
- Tags should be relevant single words or short phrases
- Return ONLY the JSON, no markdown, no extra text
"""

def generate_script(topic: str) -> dict | None:
    """Generate video script using Gemini API (free tier)."""
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        log.error("Please set your GEMINI_API_KEY in scripts/generate_script.py or as environment variable")
        return None

    prompt = PROMPT_TEMPLATE.format(topic=topic)
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        GEMINI_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()

            # Remove markdown code fences if present
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]

            result = json.loads(text.strip())
            log.info(f"Script generated: {result.get('title', 'No title')}")
            return result

    except urllib.error.HTTPError as e:
        log.error(f"Gemini API HTTP error {e.code}: {e.read().decode()}")
        return None
    except json.JSONDecodeError as e:
        log.error(f"Failed to parse Gemini response as JSON: {e}")
        return None
    except Exception as e:
        log.error(f"Unexpected error in generate_script: {e}")
        return None


# ─── OFFLINE TEST (no API key needed) ────────────────────────────
def generate_script_offline(topic: str) -> dict:
    """Returns dummy data so you can test without an API key."""
    return {
        "title": f"Amazing Facts: {topic}",
        "script": (
            f"Did you know that {topic} is one of the most fascinating subjects? "
            "In today's video, we're going to explore some incredible facts that "
            "will blow your mind. Scientists have spent years researching this topic "
            "and have discovered some truly amazing things. "
            "From surprising origins to unexpected connections, "
            "there is so much to learn. "
            "Stay with us as we dive deep into the world of knowledge and discovery. "
            "By the end of this video, you will see the world in a completely new way. "
            "If you enjoy learning fascinating facts like these, "
            "please like this video and subscribe to our channel "
            "so you never miss an episode!"
        ),
        "description": (
            f"Discover amazing facts about {topic} in this educational video. "
            "We cover everything you need to know in a simple and engaging way. "
            "#facts #educational #knowledge #learning #interesting"
        ),
        "tags": ["facts", "educational", "knowledge", "interesting", topic.lower()],
        "hook": f"Did you know that {topic} is one of the most fascinating subjects?",
        "sections": ["Introduction", "Key Facts", "Conclusion"]
    }


if __name__ == "__main__":
    # Quick test
    result = generate_script_offline("Space Exploration")
    print(json.dumps(result, indent=2))
