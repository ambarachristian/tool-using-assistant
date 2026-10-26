"""Milestone 1: send one message to Claude and print the reply."""
import anthropic
from dotenv import load_dotenv

# Copy the values from .env into the environment.
# override=True: the .env key wins over the one set in Windows.
load_dotenv(override=True)

# The client finds ANTHROPIC_API_KEY in the environment by itself.
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"

SYSTEM_PROMPT = (
    "You are a patient tutor for someone new to AI agents. "
    "Answer in plain language, in at most three short sentences, "
    "and end with a one-line everyday analogy."
)


response = client.messages.create(
    model=MODEL,
    max_tokens=16000,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": "What is an AI agent?"},
    ],
)


# The reply is a list of content blocks. Print only the text ones.
for block in response.content:
    if block.type == "text":
        print(block.text)

# Look inside the response.
usage = response.usage
cost = usage.input_tokens * 2 / 1_000_000 + usage.output_tokens * 10 / 1_000_000

print("\n--- response details ---")
print("stop_reason: ", response.stop_reason)
print("block types: ", [block.type for block in response.content])
print("input tokens: ", usage.input_tokens)
print("output tokens:", usage.output_tokens)
print(f"cost:          ${cost:.5f}")
