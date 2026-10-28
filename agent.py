"""Milestone 3: an agent loop written by hand."""
import sys

import anthropic
from dotenv import load_dotenv

from tools import TOOLS, run_tool

load_dotenv(override=True)
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"
MAX_ITERATIONS = 10
SYSTEM_PROMPT = (
    "You are a helpful assistant with three tools: a calculator, a current-weather "
    "lookup and a reader for the user's notes folder. Use a tool whenever it gives "
    "a more accurate answer than your own knowledge. Never guess a number you can "
    "compute or look up. In your final answer, briefly say which tools you used "
    "and why."
)


def handle_tool_calls(response) -> list[dict]:
    """Run every tool Claude asked for. Return one tool_result block per request."""
    results = []
    for block in response.content:
        if block.type == "tool_use":
            print(f"  [tool] {block.name}({block.input})")
            output = run_tool(block.name, block.input)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output,
            })
    return results

def run_agent(messages: list) -> str:
    """Loop until Claude gives a final answer or we reach MAX_ITERATIONS.
    Appends every turn to `messages`, so the caller keeps the full history."""

    for turn in range(1, MAX_ITERATIONS + 1):

        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        print(f"[turn {turn}] stop_reason: {response.stop_reason}")

        # Keep Claude's whole reply, tool_use blocks included, in the history.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            # Claude wants no more tools: this is the final answer.
            return "".join(b.text for b in response.content if b.type == "text")

        # Run the tools and send ALL results back in ONE user message.
        messages.append({"role": "user", "content": handle_tool_calls(response)})

    return f"Stopped: no final answer after {MAX_ITERATIONS} turns."


def describe(block) -> str:
    """One short line for a content block (an SDK object or a plain dict)."""
    b = block if isinstance(block, dict) else block.to_dict()
    if b["type"] == "text":
        return f"text: {b['text'][:60]!r}"
    if b["type"] == "tool_use":
        return f"tool_use    ..{b['id'][-6:]}: {b['name']}({b['input']})"
    if b["type"] == "tool_result":
        return f"tool_result ..{b['tool_use_id'][-6:]}: {str(b['content'])[:50]!r}"
    return b["type"]


def print_transcript(messages: list) -> None:
    """Show the conversation the way the API sees it: one line per block."""
    print("\n=== transcript ===")
    for i, message in enumerate(messages):
        content = message["content"]
        blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
        for block in blocks:
            print(f"{i:>2} {message['role']:<9} {describe(block)}")


if __name__ == "__main__":
    # Use the words after "python agent.py" as the question, or a default one.
    question = " ".join(sys.argv[1:]) or "What is the total of my shopping list in shopping.md?"
    messages = [{"role": "user", "content": question}]
    print(run_agent(messages))
    print_transcript(messages)

