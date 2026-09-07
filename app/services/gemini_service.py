import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"


def generate_social_content(topic: str) -> dict:

    prompt = f"""
You are an expert social media content strategist,
creative director, and AI image prompt engineer.

User topic:
"{topic}"

Create content for Instagram and Facebook.

Return ONLY valid JSON in exactly this format:

{{
    "image_prompt": "Detailed image generation prompt",
    "caption": "Engaging social media caption",
    "hashtags": [
        "#hashtag1",
        "#hashtag2",
        "#hashtag3"
    ]
}}

IMAGE PROMPT requirements:
- Main subject
- Environment
- Visual elements
- Composition
- Lighting
- Mood
- Camera perspective
- Professional visual style
- Color direction
- Realistic details
- No unnecessary text inside image

CAPTION requirements:
- Natural and professional
- Engaging
- Easy to understand
- Suitable for Instagram and Facebook
- Include a relevant call-to-action when appropriate
- Do not make unsupported factual claims

HASHTAGS requirements:
- Generate 8-12 relevant hashtags
- Mix broad and niche hashtags
- Return hashtags as a JSON array

Do not add markdown.
Do not add explanations.
Return only valid JSON.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    result = response.text.strip()

    # Remove accidental markdown code fences
    if result.startswith("```"):
        result = result.replace("```json", "")
        result = result.replace("```", "")
        result = result.strip()

    try:
        content = json.loads(result)

    except json.JSONDecodeError:
        raise ValueError(
            "Gemini returned invalid JSON. Please try again."
        )

    return content
