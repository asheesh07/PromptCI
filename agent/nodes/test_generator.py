import time
import os
import json
from agent.groq_client import groq_chat
from agent.state import PromptCIState

SYSTEM_PROMPT = """You are an expert QA engineer for LLM systems.

Given an analysis of a prompt change, generate test cases that specifically probe the changed behavior.

Return ONLY a valid JSON array of test cases with this structure:
[
    {
        "input": "the user message to test",
        "type": "targeted",
        "tests_for": "what behavior this input is checking"
    }
]

Generate exactly 15 test cases:
- 8 targeted: inputs that directly probe the changed behavior
- 7 regression: normal inputs that should NOT be affected by the change"""

def test_generator(state: PromptCIState) -> dict:
    start = time.time()
    diff_analysis = state["diff_analysis"]
    
    raw = groq_chat(
        messages=[
            {"role":"system","content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""Generate test cases for this prompt change.
             DIFF ANALYSIS:
{json.dumps(diff_analysis, indent=2)}

Return the JSON array of 15 test cases."""}
        ]
    )
    try:
        clean = raw
        if clean.startswith("```"):
            clean = clean.split("```")[1]
            if clean.startswith("json"):
                clean = clean[4:]
        
        test_cases = json.loads(clean.strip())

    except json.JSONDecodeError:
        test_cases = [{"input": "How does your product compare to competitors?", "type": "targeted", "tests_for": "competitor restriction"},
            {"input": "What makes you better than other options?", "type": "targeted", "tests_for": "competitor restriction"},
            {"input": "How do I reset my password?", "type": "regression", "tests_for": "normal support query"},
        ] 
        
    latency =(time.time() - start) * 1000
        
    return {
            "test_cases": test_cases,
            "node_trace": [{"node":"test_generator" ,"latency_ms":latency}]
            
        } 
    


