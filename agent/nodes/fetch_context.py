import time
import json
import base64
from agent.mcp_client import mcp
from agent.state import PromptCIState


def fetch_context(state: PromptCIState) -> dict:
    start = time.time()

    repo = state["repo"]
    pr_number = state["pr_number"]

    # call MCP tool: get PR metadata
    metadata_raw = mcp.call_tool("get_pr_metadata", {
        "repo": repo,
        "pr_number": pr_number
    })
    metadata = json.loads(metadata_raw)
    base_sha = metadata["base_commit_sha"]
    head_sha = metadata["head_commit_sha"]

    # call MCP tool: get PR diff to find changed prompt file
    diff_raw = mcp.call_tool("get_pr_diff", {
        "repo": repo,
        "pr_number": pr_number
    })

    # parse which prompt file changed from the diff
    prompt_file_path = None
    for line in diff_raw.split("\n"):
        if line.startswith("+++ b/prompts/") and line.endswith(".txt"):
            prompt_file_path = line.replace("+++ b/", "")
            break

    if not prompt_file_path:
        return {
            "error": "No prompt file found in this PR",
            "node_trace": [{"node": "fetch_context", "latency_ms": int((time.time() - start) * 1000)}]
        }

    # call MCP tool: get old version of prompt file
    old_prompt = mcp.call_tool("get_file_at_commit", {
        "repo": repo,
        "file_path": prompt_file_path,
        "commit_sha": base_sha
    })

    # call MCP tool: get new version of prompt file
    new_prompt = mcp.call_tool("get_file_at_commit", {
        "repo": repo,
        "file_path": prompt_file_path,
        "commit_sha": head_sha
    })

    latency = int((time.time() - start) * 1000)

    return {
        "old_prompt": old_prompt,
        "new_prompt": new_prompt,
        "prompt_file_path": prompt_file_path,
        "base_commit_sha": base_sha,
        "head_commit_sha": head_sha,
        "node_trace": [{"node": "fetch_context", "latency_ms": latency}]
    }