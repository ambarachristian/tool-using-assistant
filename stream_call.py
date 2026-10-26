"""Milestone 1: stream Claude's reply to the terminal as it is written."""
import anthropic
from dotenv import load_dotenv

load_dotenv(override=True)
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"
SYSTEM_PROMPT = (
    "You are a patient tutor for someone new to AI agents. "
    "Answer in plain language, in about two short paragraphs."
)

with client.messages.stream(
    model=MODEL,
    max_tokens=16000,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": "How does an AI agent decide which tool to use?"},
    ],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    # When the stream ends, the SDK has assembled the full message for you.
    final = stream.get_final_message()

print("\n\n--- response details ---")
print("stop_reason:  ", final.stop_reason)
print("output tokens:", final.usage.output_tokens)
