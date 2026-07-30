import os
import json
from google import genai
from google.genai import types
from typing import Dict, Any

REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "line": {"type": "integer"},
                    "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                    "category": {"type": "string", "enum": ["bug", "style", "correctness", "security"]},
                    "description": {"type": "string"},
                    "suggested_fix": {"type": "string"},
                },
                "required": ["line", "severity", "category", "description"],
            },
        },
        "overall_quality": {"type": "string", "enum": ["pass", "fail"]},
    },
    "required": ["issues", "overall_quality"],
}

PROMPT_TEMPLATE = """You are a senior code reviewer. Review this diff for bugs,
security issues, and style problems. Diff:

{diff_text}
"""

def review_diff(diff_text: str) -> Dict[str, Any]:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-2.0-flash",  # <--- THIS IS THE CORRECT MODEL FROM YOUR LIST
        contents=PROMPT_TEMPLATE.format(diff_text=diff_text),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=REVIEW_SCHEMA,
        ),
    )
    return json.loads(response.text)
