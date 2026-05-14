import json
import platform
import sys
from dataclasses import dataclass
from typing import Optional, List, Dict

from anthropic import Anthropic

from .runner import FailureReport
from .config import get_api_key

@dataclass
class Analysis:
    root_cause: str
    location: str
    explanation: str
    fix: str
    also_found: List[str]
    confidence: int
    fix_diff: Optional[str] = None

def get_env_info() -> str:
    """Gather basic system info for context."""
    return f"""
    OS: {platform.system()} {platform.release()}
    Python Version: {sys.version}
    """

def analyze_failure(report: FailureReport, context: Dict[str, str]) -> Analysis:
    """Uses Anthropic API to analyze the failure."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY env var or use `rootcause config <key>`")

    client = Anthropic(api_key=api_key)

    prompt = f"""
You are an expert debugging assistant performing root cause analysis.

A developer's test is failing. Analyze the failure and identify the EXACT root cause.

## Failing Test Output
{report.traceback or report.stdout + report.stderr}

## Source Code Context
{context.get('source_context', 'No local source context found.')}

## Recent Git Changes (last 5 commits touching these files)
{context.get('git_context', 'No recent git changes found.')}

## Environment
{get_env_info()}

Respond with ONLY valid JSON in this exact format:
{{
  "root_cause": "One sentence describing the exact root cause",
  "location": "filename.py:line_number",
  "explanation": "2-4 sentences explaining WHY this causes the failure",
  "fix": "Exact code change needed — show before and after",
  "also_found": ["list of other potential issues spotted, or empty array"],
  "confidence": 87,
  "fix_diff": "unified diff format if applicable, or null"
}}

Rules:
- Only reference files and line numbers that appear in the context above
- Be specific — generic answers like 'check your configuration' are not acceptable
- confidence should reflect how certain you are (not how hard the fix is)
- If you cannot determine root cause, set confidence below 40 and explain why
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="You are an expert debugging assistant. Always respond in valid JSON only.",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = response.content[0].text.strip()

    # Simple extraction just in case the model wraps in markdown json blocks
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    try:
        data = json.loads(response_text)
        return Analysis(
            root_cause=data.get("root_cause", "Unknown"),
            location=data.get("location", "Unknown"),
            explanation=data.get("explanation", "No explanation provided."),
            fix=data.get("fix", "No fix provided."),
            also_found=data.get("also_found", []),
            confidence=data.get("confidence", 0),
            fix_diff=data.get("fix_diff")
        )
    except json.JSONDecodeError:
        raise ValueError(f"Failed to parse AI response as JSON: {response_text}")
