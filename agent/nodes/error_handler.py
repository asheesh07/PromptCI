import time
from agent.state import PromptCIState
from agent.mcp_client import mcp


def error_handler(state: PromptCIState) -> dict:
    start = time.time()
    error = state.get("error", "Unknown error")
    repo = state.get("repo")
    pr_number = state.get("pr_number")

    print(f"Error handler triggered: {error}")

    report = f"""## 🤖 PromptCI — Analysis Failed

**Error:** {error}

The PromptCI pipeline encountered an error while analyzing this prompt change.
Please check the pipeline logs or retry by pushing a new commit.

---
*[PromptCI](https://github.com/asheesh07/promptci)*"""

    try:
        if repo and pr_number:
            mcp.call_tool("post_pr_comment", {
                "repo": repo,
                "pr_number": pr_number,
                "body": report
            })
    except Exception as e:
        print(f"Failed to post error comment: {e}")

    latency = int((time.time() - start) * 1000)

    return {
        "final_report": report,
        "node_trace": [{"node": "error_handler", "latency_ms": latency}]
    }