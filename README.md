# PromptCI

CI for LLM prompts. PromptCI watches pull requests that change your `prompts/*.txt` files, runs the old and new prompt through a battery of generated test cases, checks the outputs for safety and consistency regressions, scores the change, and posts a review comment straight on the PR — the same feedback loop you already get from a linter or a test suite, but for prompt engineering.

## Why

Prompt changes are code changes, but they usually ship without any of the safety net: no diff review for behavior, no regression tests, no automated approve/block signal. A one-line tweak to a system prompt can silently make a support bot refuse things it used to answer, or answer things it used to refuse. PromptCI closes that gap by treating a prompt edit like any other change that needs to pass CI before merge.

## How it works

PromptCI is a [LangGraph](https://github.com/langchain-ai/langgraph) pipeline exposed over a FastAPI service. A GitHub webhook (or a manual `/run` call) triggers this graph:

```
fetch_context → diff_analyst → test_generator ─┬─→ regression_runner ─┐
                                                └─→ safety_checker ────┴─→ judge → report_writer
```

| Node | What it does |
|---|---|
| `fetch_context` | Pulls PR metadata and diff via MCP tools, finds the changed file under `prompts/`, and fetches the file's contents at both the base and head commit. |
| `diff_analyst` | Asks an LLM to explain the *intent* and *impact* of the prompt change (not just the text diff) and assigns a risk level. |
| `test_generator` | Generates 15 test inputs: 8 that directly probe the changed behavior, 7 regression inputs that should be unaffected. |
| `regression_runner` | Runs every test input against both the old and new prompt in parallel and collects output pairs. |
| `safety_checker` | Compares each output pair for over-refusal, under-refusal, inconsistency, hallucination, or information leakage. |
| `judge` | Scores the change on quality, consistency, safety, and task completion, then recommends **APPROVE**, **REVIEW**, or **BLOCK**. |
| `report_writer` | Writes a markdown report and posts it as a comment on the pull request via MCP. |

`regression_runner` and `safety_checker` fan out from `test_generator` and run concurrently before feeding into `judge`.

GitHub access (fetching diffs/files, posting comments) goes through a small [MCP](https://modelcontextprotocol.io/) server (`mcp_server/github_tools.py`) rather than calling the GitHub API directly from the graph nodes, so the tool surface is reusable outside the LangGraph pipeline. Every run — scores, recommendation, node timings, and the final report — is persisted to SQLite so you can track a prompt file's history over time.

## Project layout

```
agent/
  graph.py            # builds and compiles the LangGraph pipeline
  state.py            # shared PromptCIState TypedDict passed between nodes
  groq_client.py       # LLM chat wrapper (Groq, with retry/backoff)
  mcp_client.py        # spawns and talks to the MCP server over stdio
  nodes/
    fetch_context.py
    diff_analyst.py
    test_generator.py
    regression_runner.py
    safety_checker.py
    judge.py
    report_writer.py
    error_handler.py
api/
  main.py             # FastAPI app: webhook, SSE run endpoint, history endpoints
mcp_server/
  github_tools.py      # MCP tools: get_pr_diff, get_file_at_commit, post_pr_comment, get_pr_metadata, list_prompt_files
db/
  storage.py           # SQLite persistence for run history
eval/
  scenarios.py         # 20 hand-written prompt-change scenarios with expected outcomes
  run_evals.py         # runs the pipeline against every scenario and scores accuracy
render.yaml            # Render.com deployment config
```

## Setup

**Requirements:** Python 3.11+, a [Groq API key](https://console.groq.com/), and a GitHub personal access token with `repo` scope (to read PR diffs/files and post comments).

```bash
git clone https://github.com/asheesh07/PromptCI.git
cd PromptCI
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```bash
GROQ_API_KEY=your_groq_api_key
GITHUB_TOKEN=your_github_pat
GITHUB_WEBHOOK_SECRET=your_webhook_secret   # optional, verifies incoming webhook signatures
```

Run the API locally:

```bash
uvicorn api.main:app --reload
```

## Usage

**Set up a webhook** on any repo you want covered: Settings → Webhooks → add `https://<your-deployment>/webhook`, content type `application/json`, events: Pull requests. PromptCI only kicks off analysis when a PR touches a `.txt` file under `prompts/`.

**Or trigger a run manually** and stream progress over Server-Sent Events:

```bash
curl "http://localhost:8000/run?repo=owner/repo&pr_number=42"
```

**Check run history** for a specific prompt file, or all runs for a repo:

```bash
curl "http://localhost:8000/history?repo=owner/repo&prompt_file=prompts/support.txt"
curl "http://localhost:8000/runs?repo=owner/repo"
```

A completed run posts a comment on the PR with an overall score, a breakdown across quality/consistency/safety/task-completion, any flagged edge cases, and an APPROVE/REVIEW/BLOCK recommendation.

## Evaluation

`eval/scenarios.py` has 20 hand-labeled prompt changes (10 that should be approved, 10 that should be flagged) covering things like removed safety disclaimers, contradictory instructions, and scope creep. Run the pipeline against all of them:

```bash
python3 eval/run_evals.py
```

Progress is checkpointed to `eval/results.json`, so an interrupted run resumes from where it left off. The script reports binary flag accuracy (APPROVE vs. flagged), strict 3-class accuracy, true positive rate (bad changes caught), and false positive rate (good changes wrongly flagged).

## Deployment

`render.yaml` deploys the FastAPI app on [Render](https://render.com) with `GITHUB_TOKEN`, `GROQ_API_KEY`, and `GITHUB_WEBHOOK_SECRET` as secret env vars — set those in the Render dashboard rather than committing them.

## Tech stack

FastAPI · LangGraph · Groq (Llama 3.3 70B) · MCP · SQLite · Server-Sent Events
