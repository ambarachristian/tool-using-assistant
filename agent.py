"""A tool-using assistant: a hand-written agent loop around the Claude API.

Usage:
    python agent.py                      # chat mode: ask follow-up questions, 'quit' to leave
    python agent.py "your question"      # one question, then exit
    python agent.py --transcript "..."   # one question, then print the message history
"""
import sys

import anthropic
from dotenv import load_dotenv

from tools import TOOLS, run_tool

# Print any character Claude writes (°, →, accents), even when output goes to a file.
sys.stdout.reconfigure(encoding="utf-8")

load_dotenv(override=True)
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"
MAX_ITERATIONS = 10
# If Claude declines a request in certain safety categories, the API can retry it
# on another model inside the same call. Beta feature, Claude API only.
FALLBACK_BETA = "server-side-fallback-2026-07-01"
SYSTEM_PROMPT = (
    "You are a helpful assistant with three tools: a calculator, a current-weather "
    "lookup and a reader for the user's notes folder. Use a tool whenever it gives "
    "a more accurate answer than your own knowledge. Never guess a number you can "
    "compute or look up. If a tool returns an error, read it, then retry with "
    "corrected input or explain the problem. In your final answer, briefly say "
    "which tools you used and why, or say that you needed none. "
    "Your answer is shown in a plain terminal: write plain text, with no Markdown "
    "(no **, no # headings, no tables)."
)


def handle_tool_calls(response) -> list[dict]:
    """Run every tool Claude asked for. Return one tool_result block per request.
    A failing tool becomes an error result for Claude instead of a crash."""
    results = []
    for block in response.content:
        if block.type == "tool_use":
            print(f"  [tool] {block.name}({block.input})")
            try:
                output = run_tool(block.name, block.input)
                is_error = False
            except Exception as error:
                output = f"{type(error).__name__}: {error}"
                is_error = True
                print(f"  [tool error] {output}")
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": output,
                "is_error": is_error,
            })
    return results


def ask_claude(messages: list):
    """One streamed call to Claude. Prints text as it arrives; returns the full message."""
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
        betas=[FALLBACK_BETA],
        fallbacks="default",
    ) as stream:
        printed = False
        for text in stream.text_stream:
            print(text, end="", flush=True)
            printed = True
        if printed:
            print()
        return stream.get_final_message()


def run_agent(messages: list) -> str:
    """Loop until Claude gives a final answer or we reach MAX_ITERATIONS.
    Appends every turn to `messages`, so the caller keeps the full history."""
    for turn in range(1, MAX_ITERATIONS + 1):
        print(f"[turn {turn}]")
        response = ask_claude(messages)

        # Keep Claude's whole reply, tool_use blocks included, in the history.
        # (A refusal can come back empty, and the API rejects empty messages.)
        if response.content:
            messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            # Run the tools and send ALL results back in ONE user message.
            messages.append({"role": "user", "content": handle_tool_calls(response)})
            continue

        answer = "".join(b.text for b in response.content if b.type == "text")
        if response.stop_reason == "max_tokens":
            # Never run tools from a cut-off reply: their input may be incomplete.
            note = "[The answer was cut off: it reached the max_tokens limit.]"
            print(note)
            return f"{answer}\n{note}"
        if response.stop_reason == "refusal":
            category = getattr(response.stop_details, "category", None) or "unspecified"
            note = f"[Claude declined this request (safety category: {category}).]"
            print(note)
            return note
        return answer  # end_turn: the normal final answer

    note = f"[Stopped: no final answer after {MAX_ITERATIONS} turns.]"
    print(note)
    return note


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


def ask_safely(messages: list) -> bool:
    """Run the agent and turn API failures into short messages.
    Returns False when continuing makes no sense (bad API key)."""
    try:
        run_agent(messages)
    except anthropic.AuthenticationError:
        print("[error] The API key was rejected. Check ANTHROPIC_API_KEY in .env.")
        return False
    except anthropic.RateLimitError:
        print("[error] Rate limited by the API. Wait a moment, then ask again.")
    except anthropic.APIConnectionError:
        print("[error] Could not reach the API. Check your internet connection.")
    except anthropic.APIStatusError as error:
        print(f"[error] The API returned {error.status_code}: {error.message}")
    return True


def chat() -> None:
    """Interactive chat. One messages list for the whole session = the agent's memory."""
    print("Tool-using assistant. Ask a question, or type 'quit' to leave.")
    messages = []
    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"quit", "exit"}:
            break
        if not question:
            continue
        messages.append({"role": "user", "content": question})
        if not ask_safely(messages):
            break


if __name__ == "__main__":
    args = sys.argv[1:]
    show_transcript = "--transcript" in args
    question = " ".join(a for a in args if a != "--transcript")
    if question:
        messages = [{"role": "user", "content": question}]
        ask_safely(messages)
        if show_transcript:
            print_transcript(messages)
    else:
        chat()
