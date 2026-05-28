import os
from dotenv import load_dotenv
import json
load_dotenv()

from agent.nodes.fetch_context import fetch_context

# first open a real PR on demo-ai-app
# change one line in prompts/customer_support.txt and open a PR
# paste the PR number below

state = {
    "pr_url": "https://github.com/asheesh07/demo-ai-app/pull/1",
    "repo": "asheesh07/demo-ai-app",
    "pr_number": 1,
    "node_trace": []
}

result = fetch_context(state)
print("prompt file:", result.get("prompt_file_path"))
print("old prompt:", result.get("old_prompt", "")[:100])
print("new prompt:", result.get("new_prompt", "")[:100])
print("latency:", result.get("node_trace"))
print("error:", result.get("error"))

from agent.nodes.diff_analyst import diff_analyst

result2 = diff_analyst({**state, **result})
print("\n--- diff analysis ---")
print(json.dumps(result2["diff_analysis"], indent=2))
print("latency:", result2["node_trace"][-1])

from agent.nodes.test_generator import test_generator

result3 = test_generator({**state, **result, **result2})
print("\n--- test cases ---")
for i, tc in enumerate(result3["test_cases"]):
    print(f"{i+1}. [{tc['type']}] {tc['input']}")
print("latency:", result3["node_trace"][-1])

from agent.nodes.regression_runner import regression_runner

result4 = regression_runner({**state, **result, **result2, **result3})
print("\n--- output pairs (first 2) ---")
for pair in result4["output_pairs"][:2]:
    print(f"\nINPUT: {pair['input']}")
    print(f"OLD: {pair['old_output'][:120]}")
    print(f"NEW: {pair['new_output'][:120]}")
print("latency:", result4["node_trace"][-1])

from agent.nodes.safety_checker import safety_checker

result5 = safety_checker({**state, **result, **result2, **result3, **result4})
print("\n--- safety findings ---")
print("risk score:", result5["safety_findings"].get("risk_score"))
print("summary:", result5["safety_findings"].get("summary"))
for issue in result5["safety_findings"].get("issues", []):
    print(f"  [{issue['severity']}] {issue['issue_type']}: {issue['description'][:100]}")
print("latency:", result5["node_trace"][-1])


from agent.nodes.judge import judge

result6 = judge({**state, **result, **result2, **result3, **result4, **result5})
print("\n--- scores ---")
scores = result6["scores"]
print(f"quality:         {scores.get('quality')}/100  {scores.get('quality_note','')}")
print(f"consistency:     {scores.get('consistency')}/100  {scores.get('consistency_note','')}")
print(f"safety:          {scores.get('safety')}/100  {scores.get('safety_note','')}")
print(f"task_completion: {scores.get('task_completion')}/100  {scores.get('task_completion_note','')}")
print(f"overall:         {scores.get('overall')}/100")
print(f"recommendation:  {scores.get('recommendation')}")
print(f"reason:          {scores.get('recommendation_reason')}")
print("latency:", result6["node_trace"][-1])


from agent.nodes.report_writer import report_writer

result7 = report_writer({**state, **result, **result2, **result3, **result4, **result5, **result6})
print("\n--- final report ---")
print(result7["final_report"])
print("\nlatency:", result7["node_trace"][-1])

import httpx

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

url = "https://api.github.com/repos/asheesh07/demo-ai-app/issues/1/comments"
r = httpx.post(url, headers=HEADERS, json={"body": result7["final_report"]})
print("\n--- posted to github ---")
print("status:", r.status_code)
print("comment url:", r.json().get("html_url"))