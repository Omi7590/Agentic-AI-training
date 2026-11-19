# RTI Mitra - run_eval.py
# Evaluates two RAG configs on the 15-question eval set.
# Config A: top_k=3
# Config B: top_k=5
# Scoring:
#   - Answerable questions: pass if answer does NOT contain "I don't know"
#   - Unanswerable questions (Q6): pass if answer DOES contain "I don't know"
# Prints a results table and writes the winner to eval/eval_results.md

import json
import os

EVAL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_set.json")
RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_results.md")


def score_answer(answer: str, answerable: bool) -> bool:
    """Return True if the answer is correct for its type."""
    has_dont_know = "i don't know" in answer.lower() or "i do not know" in answer.lower()
    if answerable:
        return not has_dont_know
    else:
        return has_dont_know


def run_eval():
    with open(EVAL_PATH, encoding="utf-8") as f:
        eval_set = json.load(f)

    configs = ["config_a", "config_b"]
    scores = {"config_a": 0, "config_b": 0}
    rows = []

    for item in eval_set:
        row = {
            "id": item["id"],
            "question": item["question"][:60],
            "answerable": item["answerable"],
        }
        for cfg in configs:
            answer = item[cfg]["answer"]
            passed = score_answer(answer, item["answerable"])
            scores[cfg] += 1 if passed else 0
            row[cfg] = "✅" if passed else "❌"
        rows.append(row)

    total = len(eval_set)

    # Print table to terminal
    print(f"\n{'ID':<4} {'Answerable':<11} {'Config A':<10} {'Config B':<10} Question")
    print("-" * 80)
    for r in rows:
        print(f"{r['id']:<4} {'Yes' if r['answerable'] else 'No':<11} {r['config_a']:<10} {r['config_b']:<10} {r['question']}")

    print(f"\nConfig A score: {scores['config_a']}/{total}")
    print(f"Config B score: {scores['config_b']}/{total}")
    winner = "Config A (top_k=3)" if scores["config_a"] >= scores["config_b"] else "Config B (top_k=5)"
    print(f"Winner: {winner}")

    # Write eval_results.md
    lines = []
    lines.append("# RAG Evaluation Results — RTI Mitra\n\n")
    lines.append("## Configs compared\n\n")
    lines.append("| Config | top_k | Description |\n")
    lines.append("|--------|-------|-------------|\n")
    lines.append("| Config A | 3 | Retrieve top 3 chunks per question |\n")
    lines.append("| Config B | 5 | Retrieve top 5 chunks per question |\n\n")
    lines.append("## Scoring\n\n")
    lines.append("- Answerable question: PASS if answer does not contain 'I don't know'\n")
    lines.append("- Unanswerable question (Q6): PASS if answer contains 'I don't know'\n\n")
    lines.append("## Results table\n\n")
    lines.append("| ID | Question | Answerable | Config A | Config B |\n")
    lines.append("|----|----------|-----------|---------|----------|\n")
    for r in rows:
        lines.append(f"| {r['id']} | {r['question']} | {'Yes' if r['answerable'] else 'No'} | {r['config_a']} | {r['config_b']} |\n")
    lines.append("\n## Scores\n\n")
    lines.append("| Config | Score |\n|--------|-------|\n")
    lines.append(f"| Config A (top_k=3) | {scores['config_a']}/{total} |\n")
    lines.append(f"| Config B (top_k=5) | {scores['config_b']}/{total} |\n\n")
    lines.append(f"## Winner: {winner}\n\n")
    if winner == "Config A (top_k=3)":
        lines.append("Top-3 retrieval is sufficient for RTI Mitra — the rules are short and specific, so fetching 3 chunks avoids noise from loosely related records.\n")
    else:
        lines.append("Top-5 retrieval scores higher — more context helps the LLM pick the right rule, especially for multi-part questions.\n")

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\nSaved results to {RESULTS_PATH}")
    return scores, winner


if __name__ == "__main__":
    run_eval()
