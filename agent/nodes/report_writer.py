import time
import os
from agent.groq_client import groq_chat
from agent.state import PromptCIState
from agent.mcp_client import mcp


SYSTEM_PROMPT = """You are writing an automated code review comment for a GitHub pull request.

The comment is about a prompt file change analyzed by an AI pipeline.

Write a clean, structured markdown comment. Use this exact format:

## 🤖 PromptCI — Analysis Complete

**Overall score: {overall}/100** {emoji} {recommendation}

**What changed:** {intent}

---

### Scores

| Dimension | Score | Note |
|---|---|---|
| Quality | {quality}/100 | {quality_note} |
| Consistency | {consistency}/100 | {consistency_note} |
| Safety | {safety}/100 | {safety_note} |
| Task completion | {task_completion}/100 | {task_completion_note} |

---

### Edge cases flagged
{list any issues from safety findings, or "None detected"}

---

### Recommendation
**{recommendation}** — {recommendation_reason}

---
*Analyzed by [PromptCI](https://github.com/asheesh07/promptci) · {num_test_cases} test cases · {total_latency}s total*

Use ✅ for APPROVE, ⚠️ for REVIEW, ❌ for BLOCK."""


def report_writer(state: PromptCIState) -> dict:
    start = time.time()

    scores = state["scores"]
    diff_analysis = state["diff_analysis"]
    safety_findings = state["safety_findings"]
    test_cases = state["test_cases"]
    node_trace = state.get("node_trace", [])

    total_latency = round(sum(n["latency_ms"] for n in node_trace) / 1000, 1)
    num_test_cases = len(test_cases)

    issues_text = ""
    if safety_findings.get("issues"):
        for issue in safety_findings["issues"]:
            issues_text += f"- [{issue['severity'].upper()}] {issue['issue_type']}: {issue['description']}\n"
    else:
        issues_text = "None detected"

    final_report = groq_chat(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""Write the GitHub PR comment for this prompt change analysis.

SCORES:
- overall: {scores.get('overall')}/100
- quality: {scores.get('quality')}/100 — {scores.get('quality_note')}
- consistency: {scores.get('consistency')}/100 — {scores.get('consistency_note')}
- safety: {scores.get('safety')}/100 — {scores.get('safety_note')}
- task_completion: {scores.get('task_completion')}/100 — {scores.get('task_completion_note')}

RECOMMENDATION: {scores.get('recommendation')}
REASON: {scores.get('recommendation_reason')}

INTENT: {diff_analysis['intent']}
ISSUES: {issues_text}
TEST CASES RUN: {num_test_cases}
TOTAL LATENCY: {total_latency}s

Write the markdown comment now."""}
        ],
        max_tokens=1024
    )

    
    latency = int((time.time() - start) * 1000)

    try:
        mcp.call_tool("post_pr_comment", {
        "repo": state.get("repo"),
        "pr_number": state.get("pr_number"),
        "body": final_report
        })
    except Exception as e:
        print(f"Failed to post PR comment: {e}")
    
    return {
        "final_report": final_report,
        "node_trace": [{"node": "report_writer", "latency_ms": latency}]
    }