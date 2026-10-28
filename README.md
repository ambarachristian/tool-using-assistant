# Tool-using assistant

A command-line assistant that calls the Claude API directly and uses three tools: a calculator, a current-weather lookup and a notes-file reader. The agent loop is written by hand in plain Python, with no agent framework.

Project 2 of an AI-agents learning roadmap (Level 1, Foundations).

## What it does

- Picks the right tool for a question, or none when it doesn't need one.
- Chains tools: read a note, then look up the weather for the city in it.
- Asks for several tools at once when they don't depend on each other (Tokyo *and* Paris).
- Recovers from tool errors, like an unknown city or a wrong file name, instead of crashing.
- Streams its answer to the terminal and explains which tools it used and why.
- Remembers the conversation in chat mode, so follow-ups like "And in Fahrenheit?" work.

## Setup

Python 3.13 (tested). On Windows PowerShell:

```powershell
git clone https://github.com/ambarachristian/tool-using-assistant.git
cd tool-using-assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env    # then put your Anthropic API key in .env
```

The weather tool uses [Open-Meteo](https://open-meteo.com/), which needs no API key.

## Usage

```powershell
python agent.py                                   # chat mode, type 'quit' to leave
python agent.py "Is it raining in Tokyo right now?"
python agent.py --transcript "What is the total of my shopping list in shopping.md?"
python evaluate.py                                # run the 10 test questions
```

`--transcript` prints the full message history after the answer, one line per block, so you can see each `tool_use` matched to its `tool_result`.

## How it works

```
messages = [user question]
repeat (at most MAX_ITERATIONS = 10 times):
    send messages + tool definitions to Claude (streamed)
    append Claude's reply to messages
    if stop_reason == "tool_use":
        run every requested tool
        append ONE user message with all tool_result blocks (matched by tool_use_id)
    else:
        that's the final answer: stop
```

| File | Role |
|---|---|
| `agent.py` | The agent loop, streaming, stop-reason handling, chat mode, API error handling |
| `tools.py` | Tool definitions (JSON schemas Claude sees) and tool functions (what the code runs), plus the `run_tool` dispatcher |
| `evaluate.py` | Runs the 10 test questions and logs the tools chosen to `eval_log.json` and `eval_results.md` |
| `notes/` | The only folder `read_file` can read |
| `first_call.py`, `stream_call.py`, `see_tool_call.py` | Learning scripts from milestones 1–2: a first call, streaming, and looking at a raw `tool_use` block |

### Tools

| Tool | Input | Notes |
|---|---|---|
| `calculator` | `operation` (add, subtract, multiply, divide, power), `a`, `b` | Uses `Decimal`, so results are exact (0.1 + 0.2 = 0.3). No `eval()`: only five known operations can run. |
| `get_weather` | `city`, optional `unit` (celsius, fahrenheit) | Two Open-Meteo requests: city → coordinates → current weather. Returns only the fields Claude needs, with units. |
| `read_file` | `path` | Confined to `notes/`: the resolved path must stay inside the folder, so `../.env` is refused. A missing file's error lists the files that exist. |

### Robustness

- **Tool errors are sent back to Claude, not raised.** A failing tool returns a `tool_result` with `is_error: true` and a clear message ("No place found named 'Xyzzyville'", "Cannot divide by zero"). Claude then retries or explains.
- **Input validation on two levels.** `strict: true` schemas make the API guarantee each input's shape (types, enums, required fields). The functions still check meaning: empty city, division by zero, a path outside `notes/`.
- **Every stop reason is handled.** `tool_use` continues the loop, `end_turn` is the answer, `max_tokens` is reported as cut off (and its tools are never run), and `refusal` is reported. Server-side refusal fallback (`fallbacks: "default"`, beta) is enabled.
- **API failures are caught by type** (bad key, rate limit, network, other status), so chat mode survives them.
- **Network calls have timeouts** (10 s), and file reads are capped at 20,000 characters with an explicit truncation note.

## Evaluation

`python evaluate.py` asks 10 questions, each with a fresh history. It records every tool call and its input in `eval_log.json`, then checks two things:
- **Right tools**: the set of tools called equals the expected set.
- **Explained**: the answer says what it used and names each tool. This is a keyword check, and all 10 answers were also read by hand.

Model: `claude-sonnet-5-5` · Run: 2026-10-28 · 26 API calls in total.

| # | Question | Expected tools | Tools called, in order | Right tools | Explained | Turns |
|---|---|---|---|---|---|---|
| 1 | What is 1234.5 multiplied by 678.9? | calculator | calculator | yes | yes | 2 |
| 2 | What is (12.5 + 7.25) times 3? | calculator | calculator → calculator | yes | yes | 3 |
| 3 | Is it raining in Tokyo right now? | get_weather | get_weather | yes | yes | 2 |
| 4 | What's the temperature in New York right now, in Fahrenheit? | get_weather | get_weather | yes | yes | 2 |
| 5 | Is it warmer in Lisbon or Oslo right now, and by how many degrees? | calculator, get_weather | get_weather → get_weather → calculator | yes | yes | 3 |
| 6 | What's on my grocery list? It's somewhere in my notes. | read_file | read_file → read_file | yes | yes | 3 |
| 7 | What is the total of my shopping list in shopping.md? | calculator, read_file | read_file → calculator → calculator → calculator | yes | yes | 5 |
| 8 | Read my note trip.md and tell me whether I need an umbrella at my destination today. | get_weather, read_file | read_file → get_weather | yes | yes | 3 |
| 9 | Who wrote Romeo and Juliet? | none | none | yes | yes | 1 |
| 10 | What's the weather in Xyzzyville? | get_weather | get_weather | yes | yes | 2 |

**Right tools: 10/10 · Explained: 10/10**

### Findings

- **Parallel, then chained (test 5).** Both weather lookups came in the same turn, then the two temperatures became the calculator's inputs in the next turn.
- **Recovery from a wrong guess (test 6).** Claude guessed `grocery.md`. The error listed `shopping.md, trip.md`, and Claude opened the right file without help.
- **Graceful failure (test 10).** The unknown city produced a clear error result, and Claude asked for a correct spelling instead of making up weather.
- **Honest limits (test 8).** Claude pointed out that the tool gives current conditions, not a forecast.
- **One small slip (test 5).** Claude worked out a second difference ("feels like", 7.3 °C) in its head, despite the "never guess a number" rule. The number was right, and Claude said it hadn't used the calculator for it.
- **Tool design drives cost (test 7).** The calculator takes two numbers, so adding four prices took three calls and five turns, and every turn re-sends the whole history. A `sum` operation that takes a list would cut that to about three turns.
- **Check the checker.** The first version of the "explained" check demanded the literal word "tool" and scored 7/10. Reading the three failures showed good explanations ("I used read_file to open trip.md and get_weather to check Lisbon"). The check was fixed, and the saved answers were re-graded with `python evaluate.py --rescore`, with no new API calls.

Caveats: this is a small test set run once, and the weather answers depend on live data.

## Key ideas

1. **Claude never runs tools.** It returns a `tool_use` block (name, input, id). Your code runs the function and sends back a `tool_result` with the same id.
2. **The API has no memory.** The `messages` list *is* the memory, and it's re-sent on every call, Claude's own `tool_use` blocks included.
3. **The agent loop is ordinary code.** Call, check `stop_reason`, run tools, append, repeat, with a cap on the number of turns.
4. **Tool descriptions are prompts.** They decide *when* Claude picks a tool. Say what the tool is for, when to use it, and what it can't do.
5. **Model output is untrusted input.** Enforce limits in code (`resolve()` + `is_relative_to()`, a fixed list of operations), not in the prompt.
6. **Errors are data.** Return them to the model with a clear message, and the agent recovers instead of crashing.
