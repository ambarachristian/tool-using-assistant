"""Milestone 2: give Claude a tool and look at how it asks to use it."""
import anthropic
from dotenv import load_dotenv

from tools import TOOLS, run_tool

load_dotenv(override=True)
client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=16000,
    tools=TOOLS,
    messages=[
        {"role": "user", "content": "Compare the weather in Tokyo and Paris right now."},
    ],
)

print("stop_reason: ", response.stop_reason)
print("input tokens:", response.usage.input_tokens)
for block in response.content:
    print("\n--- block:", block.type)
    if block.type == "text":
        print(block.text)
    elif block.type == "tool_use":
        print("id:   ", block.id)
        print("name: ", block.name)
        print("input:", block.input)
        result = run_tool(block.name, block.input)
        print("result:", result)

