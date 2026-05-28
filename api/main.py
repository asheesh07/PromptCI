import os
import json
import hmac
import hashlib
import asyncio
import threading
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

load_dotenv()

from agent.graph import promptci_graph
from db.storage import init_db, save_run, get_history, get_all_runs

init_db()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")


def verify_signature(payload: bytes, signature: str) -> bool:
    if not WEBHOOK_SECRET:
        return True
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def run_pipeline_sync(repo: str, pr_number: int, pr_url: str):
    import traceback
    import sys
    print(f"Python: {sys.executable}")
    print(f"CWD: {os.getcwd()}")
    print(f"Files: {os.listdir('.')}")
    
    # test MCP client
    try:
        from agent.mcp_client import mcp
        print("MCP client imported OK")
        result = mcp.call_tool("get_pr_metadata", {
            "repo": repo,
            "pr_number": pr_number
        })
        print(f"MCP test result: {result[:100]}")
    except Exception as e:
        print(f"MCP client error: {e}")
        print(traceback.format_exc())
        return


@app.get("/")
async def root():
    return {"status": "PromptCI running"}


@app.post("/webhook")
async def webhook(request: Request):
    payload_bytes = await request.body()

    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(payload_bytes, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    event = request.headers.get("X-GitHub-Event", "")
    if event != "pull_request":
        return {"status": "ignored", "event": event}

    payload = json.loads(payload_bytes)
    action = payload.get("action", "")

    if action not in ["opened", "synchronize"]:
        return {"status": "ignored", "action": action}

    pr = payload["pull_request"]
    repo = payload["repository"]["full_name"]
    pr_number = pr["number"]
    pr_url = pr["html_url"]

    changed_files = []
    try:
        import httpx
        token = os.environ.get("GITHUB_TOKEN")
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        r = httpx.get(
            f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files",
            headers=headers
        )
        changed_files = [f["filename"] for f in r.json()]
    except Exception as e:
        print(f"Error fetching files: {e}")

    prompt_changed = any(
        f.startswith("prompts/") and f.endswith(".txt")
        for f in changed_files
    )

    if not prompt_changed:
        return {"status": "ignored", "reason": "no prompt files changed"}

    thread = threading.Thread(
        target=run_pipeline_sync,
        args=(repo, pr_number, pr_url),
        daemon=True
    )
    thread.start()

    return {"status": "accepted", "pr": pr_number}


@app.get("/run")
async def run_sse(repo: str, pr_number: int):
    pr_url = f"https://github.com/{repo}/pull/{pr_number}"

    async def event_stream():
        yield {
            "event": "start",
            "data": json.dumps({"message": "Pipeline started"})
        }

        initial_state = {
            "pr_url": pr_url,
            "repo": repo,
            "pr_number": pr_number,
            "node_trace": [],
            "error": None
        }

        try:
            final_state = await asyncio.to_thread(
                promptci_graph.invoke, initial_state
            )
            save_run(final_state)

            for trace in final_state.get("node_trace", []):
                yield {
                    "event": "node_complete",
                    "data": json.dumps(trace)
                }

            yield {
                "event": "complete",
                "data": json.dumps({
                    "recommendation": final_state.get("recommendation"),
                    "scores": final_state.get("scores"),
                    "final_report": final_state.get("final_report"),
                    "node_trace": final_state.get("node_trace")
                })
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)})
            }

    return EventSourceResponse(event_stream())


@app.get("/history")
async def history(repo: str, prompt_file: str):
    return get_history(repo, prompt_file)


@app.get("/runs")
async def all_runs(repo: str):
    return get_all_runs(repo)

