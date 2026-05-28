import time
import json
import os
from agent.groq_client import groq_chat
from agent.state import PromptCIState


SYSTEM_PROMPT = """You are an expert prompt engineer analyzing changes between two versions of an LLM system prompt.

Your job is to understand the INTENT and IMPACT of the change, not just the text diff.

Return ONLY a valid JSON object with this exact structure:
{
    "intent": "one sentence describing what the engineer was trying to achieve",
    "changed_behavior": "what the LLM will now do differently",
    "affected_query_types": ["list", "of", "query", "types", "affected"],
    "risk_level": "low|medium|high",
    "risk_reason": "why this risk level"
}"""

def diff_analyst(state: PromptCIState) -> dict:
    start = time.time()

    old_prompt = state["old_prompt"]
    new_prompt = state["new_prompt"]
    prompt_file_path = state["prompt_file_path"]

    raw = groq_chat(
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"""Analyze this prompt change...

File: {prompt_file_path}

OLD PROMPT:
{old_prompt}

NEW PROMPT:
{new_prompt}

Return the JSON analysis."""}
    ]
)
    
    try:
        clean = raw
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        diff_analysis = json.loads(clean.strip())
    except json.JSONDecodeError:
        diff_analysis = {
            "intent": raw,
            "changed_behavior": "unknown",
            "affected_query_types": [],
            "risk_level": "medium",
            "risk_reason": "could not parse analysis"
        }

    latency = int((time.time() - start) * 1000)

    return {
        "diff_analysis": diff_analysis,
        "node_trace": [{"node": "diff_analyst", "latency_ms": latency}]
    }