import time
import os
from agent.groq_client import groq_chat
from concurrent.futures import ThreadPoolExecutor, as_completed
from agent.state import PromptCIState

def run_prompt(system_prompt: str, user_input: str) -> str:
    return groq_chat(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        max_tokens=256
    )


def run_pair(args):
    tc, old_prompt, new_prompt = args
    return {
        "input": tc["input"],
        "type": tc["type"],
        "tests_for": tc["tests_for"],
        "old_output": run_prompt(old_prompt, tc["input"]),
        "new_output": run_prompt(new_prompt, tc["input"])
    }


def regression_runner(state: PromptCIState) -> dict:
    start = time.time()

    old_prompt = state.get("old_prompt", "")
    new_prompt = state.get("new_prompt", "")
    test_cases = state.get("test_cases", [])

    args = [(tc, old_prompt, new_prompt) for tc in test_cases]

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(run_pair, arg) for arg in args]
        output_pairs = [f.result() for f in as_completed(futures)]

    latency = int((time.time() - start) * 1000)

    return {
        "output_pairs": output_pairs,
        "node_trace": [{"node": "regression_runner", "latency_ms": latency}]
    }