"""Milestone 5: run 10 test questions, log which tools the agent chose, and score them.

Run:  python evaluate.py              # ask all 10 questions (about 30 API calls)
      python evaluate.py --rescore    # re-grade the saved answers, no API calls
Writes eval_log.json (every tool call, input and answer) and eval_results.md (the table).
"""
import json
import sys
from datetime import datetime, timezone

import anthropic

from agent import MODEL, run_agent

# (question, the set of tools a good agent should use). An empty set means: no tools.
TESTS = [
    ("What is 1234.5 multiplied by 678.9?", {"calculator"}),
    ("What is (12.5 + 7.25) times 3?", {"calculator"}),
    ("Is it raining in Tokyo right now?", {"get_weather"}),
    ("What's the temperature in New York right now, in Fahrenheit?", {"get_weather"}),
    ("Is it warmer in Lisbon or Oslo right now, and by how many degrees?",
     {"get_weather", "calculator"}),
    ("What's on my grocery list? It's somewhere in my notes.", {"read_file"}),
    ("What is the total of my shopping list in shopping.md?", {"read_file", "calculator"}),
    ("Read my note trip.md and tell me whether I need an umbrella at my destination today.",
     {"read_file", "get_weather"}),
    ("Who wrote Romeo and Juliet?", set()),
    ("What's the weather in Xyzzyville?", {"get_weather"}),
]

# A word the answer must contain to count as naming each tool it used.
TOOL_WORDS = {"calculator": "calculator", "get_weather": "weather", "read_file": "file"}


def tool_calls(messages: list) -> list[dict]:
    """Every tool call in the history, in order, with its input."""
    calls = []
    for message in messages:
        if message["role"] == "assistant" and not isinstance(message["content"], str):
            for block in message["content"]:
                if block.type == "tool_use":
                    calls.append({"tool": block.name, "input": block.input})
    return calls


def explains(answer: str, used: set) -> bool:
    """Heuristic: the answer says what it used ("used" or "tool") and names each tool.
    (A first version demanded the word "tool" and wrongly failed answers like
    "I used read_file to open trip.md and get_weather to check Lisbon".)"""
    text = answer.lower()
    return ("used" in text or "tool" in text) and all(TOOL_WORDS[name] in text for name in used)


def run_test(number: int, question: str, expected: set) -> dict:
    print(f"\n===== Test {number}: {question}")
    messages = [{"role": "user", "content": question}]
    try:
        answer = run_agent(messages)
    except anthropic.APIError as error:
        answer = f"[API error: {error}]"
    calls = tool_calls(messages)
    used = {call["tool"] for call in calls}
    return {
        "number": number,
        "question": question,
        "expected_tools": sorted(expected),
        "tool_calls": calls,
        "right_tools": used == expected,
        "explained": explains(answer, used),
        "turns": sum(1 for m in messages if m["role"] == "assistant"),
        "answer": answer,
    }


def results_table(results: list[dict]) -> str:
    """A Markdown table for the README."""
    lines = [
        "| # | Question | Expected tools | Tools called, in order | Right tools | Explained | Turns |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        expected = ", ".join(r["expected_tools"]) or "none"
        called = " → ".join(c["tool"] for c in r["tool_calls"]) or "none"
        lines.append(
            f"| {r['number']} | {r['question']} | {expected} | {called} | "
            f"{'yes' if r['right_tools'] else 'NO'} | {'yes' if r['explained'] else 'NO'} | {r['turns']} |"
        )
    right = sum(r["right_tools"] for r in results)
    explained = sum(r["explained"] for r in results)
    lines.append("")
    lines.append(f"Right tools: {right}/{len(results)} · Explained: {explained}/{len(results)}")
    return "\n".join(lines)


def rescore() -> tuple[list[dict], str]:
    """Re-grade the answers saved in eval_log.json with the current checks."""
    with open("eval_log.json", encoding="utf-8") as f:
        log = json.load(f)
    for r in log["results"]:
        used = {call["tool"] for call in r["tool_calls"]}
        r["right_tools"] = used == set(r["expected_tools"])
        r["explained"] = explains(r["answer"], used)
    return log["results"], log["run_at"]


def main() -> None:
    if "--rescore" in sys.argv:
        results, run_at = rescore()
    else:
        results = [run_test(n, q, expected) for n, (q, expected) in enumerate(TESTS, start=1)]
        run_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with open("eval_log.json", "w", encoding="utf-8") as f:
        json.dump({"model": MODEL, "run_at": run_at, "results": results}, f, indent=2, ensure_ascii=False)

    table = results_table(results)
    with open("eval_results.md", "w", encoding="utf-8") as f:
        f.write(f"# Evaluation results\n\nModel: {MODEL} · Run at: {run_at} (UTC)\n\n{table}\n")

    print("\n" + table)


if __name__ == "__main__":
    main()
