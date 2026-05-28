from typing import TypedDict, Optional, Annotated
import operator

class PromptCIState(TypedDict, total=False):
    # inputs
    pr_url: str
    repo: str
    pr_number: int

    # fetched by fetch_context
    old_prompt: str
    new_prompt: str
    prompt_file_path: str
    base_commit_sha: str
    head_commit_sha: str

    # written by each node
    diff_analysis: dict
    test_cases: list
    output_pairs: list
    safety_findings: dict
    scores: dict
    final_report: str
    recommendation: str

    # node_trace accumulates across all nodes using operator.add
    node_trace: Annotated[list, operator.add]

    error: Optional[str]