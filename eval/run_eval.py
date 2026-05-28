import os
import sys
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from agent.nodes.diff_analyst import diff_analyst
from agent.nodes.test_generator import test_generator
from agent.nodes.regression_runner import regression_runner
from agent.nodes.safety_checker import safety_checker
from agent.nodes.judge import judge
from eval.scenarios import SCENARIOS


def run_scenario(scenario: dict) -> dict:
    print(f"\nRunning {scenario['id']}: {scenario['description']}")

    state = {
        "pr_url": "eval",
        "repo": "eval",
        "pr_number": 0,
        "old_prompt": scenario["old_prompt"],
        "new_prompt": scenario["new_prompt"],
        "prompt_file_path": "prompts/eval.txt",
        "base_commit_sha": "",
        "head_commit_sha": "",
        "node_trace": [],
        "error": None
    }

    try:
        state = {**state, **diff_analyst(state)}
        time.sleep(1)
        state = {**state, **test_generator(state)}
        time.sleep(1)
        state = {**state, **regression_runner(state)}
        time.sleep(1)
        state = {**state, **safety_checker(state)}
        time.sleep(1)
        state = {**state, **judge(state)}

        recommendation = state["scores"].get("recommendation")
        overall = state["scores"].get("overall")

        correct = recommendation == scenario["expected"] or (
            scenario["expected"] == "BLOCK" and recommendation in ["BLOCK", "REVIEW"]
        )

        print(f"  Expected: {scenario['expected']} | Got: {recommendation} | Score: {overall} | {'✓' if correct else '✗'}")

        return {
            "id": scenario["id"],
            "description": scenario["description"],
            "expected": scenario["expected"],
            "got": recommendation,
            "overall_score": overall,
            "correct": correct
        }

    except Exception as e:
        print(f"  ERROR: {e}")
        return {
            "id": scenario["id"],
            "description": scenario["description"],
            "expected": scenario["expected"],
            "got": "ERROR",
            "overall_score": 0,
            "correct": False
        }


def main():
    results = []

    for scenario in SCENARIOS:
        result = run_scenario(scenario)
        results.append(result)
        time.sleep(3)

    correct = sum(1 for r in results if r["correct"])
    total = len(results)
    good_scenarios = [r for r in results if r["expected"] == "APPROVE"]
    bad_scenarios = [r for r in results if r["expected"] in ["REVIEW", "BLOCK"]]

    tp = sum(1 for r in bad_scenarios if r["correct"])
    fp = sum(1 for r in good_scenarios if not r["correct"])

    print("\n" + "="*50)
    print("EVAL RESULTS")
    print("="*50)
    print(f"Overall accuracy:    {correct}/{total} = {round(correct/total*100)}%")
    print(f"True positive rate:  {tp}/{len(bad_scenarios)} = {round(tp/len(bad_scenarios)*100)}%")
    print(f"False positive rate: {fp}/{len(good_scenarios)} = {round(fp/len(good_scenarios)*100)}%")
    print("="*50)

    with open("eval/results.json", "w") as f:
        json.dump({
            "accuracy": round(correct/total*100),
            "true_positive_rate": round(tp/len(bad_scenarios)*100),
            "false_positive_rate": round(fp/len(good_scenarios)*100),
            "results": results
        }, f, indent=2)

    print("\nResults saved to eval/results.json")


if __name__ == "__main__":
    main()