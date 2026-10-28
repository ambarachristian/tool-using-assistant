# Tutor progress: Tool-using assistant

Roadmap: AI agents · Level 1 of 5 (Foundations) · Project 2 of 26
Mode: tutor mode (M1–M4 step 1: the learner typed every project file). From M4 step 2 on, at the learner's request, Claude wrote the code.
Stack: Python 3.13 (learner chose 3.13 over 3.12 on 2026-10-26), anthropic SDK (claude-sonnet-5-5), httpx (Open-Meteo), python-dotenv, no agent framework.
Machine: Windows 11, PowerShell terminal in VS Code.

## Milestone plan
1. First call: one message, print reply. System prompt, messages list, tokens, streaming. Ends with a public GitHub repo.
2. Tools as JSON schemas: calculator, weather lookup, read_file.
3. The agent loop: tool_use → run tool → tool_result → repeat, with a max iteration count.
4. Robustness: tool errors, input validation, conversation history, streamed answers.
5. Evaluate: 10 test questions, tool-choice log, results in README. (= "finished when" checkpoint)

## Milestone 1 steps (expected)
1. Project folder, Python 3.12 virtual environment, install packages, requirements.txt
2. .env file for the key + .gitignore
3. first_call.py: send one message, print the reply
4. Add a system prompt; inspect the response (content blocks, stop_reason, token usage)
5. Streaming the reply
6. Understanding check (2–3 questions)
7. git init, first commit, public GitHub repo, push

## Log
- 2026-10-26 · Step 0 (setup check) done. Results: Git 2.45.1 OK. ANTHROPIC_API_KEY set at user level OK. Python: only 3.13.5 installed, no 3.12.
- 2026-10-26 · Step 0b: offered to install 3.12. Learner declined: we use Python 3.13.5. Setup complete.
- 2026-10-26 · M1 Step 1 done. .venv on Python 3.13.5. Installed anthropic 2.3.0, httpx 0.28.1, python-dotenv 1.2.4. requirements.txt OK.
- 2026-10-26 · M1 Step 2 done. .gitignore, .env, .env.example all correct (UTF-8, no BOM). FOUND: the .env key is DIFFERENT from the Windows user env var key.
- 2026-10-26 · M1 Step 3 sent: first_call.py with load_dotenv(override=True) so .env wins; model claude-sonnet-5-5; max_tokens 16000; print text blocks only. Also corrected my Step 1 claim: SDK 2.x depends on httpx2, not httpx.

- 2026-10-26 · M1 Step 3 done. first_call.py correct; call succeeded, so the .env key is valid.
- 2026-10-26 · M1 Step 4 sent: add SYSTEM_PROMPT (plain language, max 3 sentences, end with an everyday analogy), question changed to "What is an AI agent?", print stop_reason, block types, input/output tokens, cost (Sonnet 5.5: $2 in / $10 out per 1M).

- 2026-10-26 · M1 Step 4 done. Output: 2 sentences + analogy, stop_reason end_turn, blocks ['text'] (no thinking), 66 in / 140 out tokens, $0.00153. Learner did not answer "what changed and which line caused it": ask again in Step 6.
- 2026-10-26 · M1 Step 5 sent: new file stream_call.py, client.messages.stream + text_stream + print(end="", flush=True) + get_final_message(). Explained SSE events.

- 2026-10-26 · M1 Step 5 done. stream_call.py correct.
- 2026-10-26 · M1 Step 6 sent: understanding check. Q1 what changed in Step 4 output + which line. Q2 follow-up question: what goes in messages (stateless API). Q3 which response field tells the agent to run a tool, and which value.

- 2026-10-26 · M1 Step 6 answers: Q1 wrong (mixed up Step 4 system prompt with Step 5 streaming). Q2 half right ("no memory" correct, but merged both questions into one user string; missed the assistant turn). Q3 half right (stop_reason, missing value "tool_use"). Re-explained Q1 (what vs how) and Q2 (transcript analogy). Follow-up asked: 3rd question → how many entries, which roles, why include Claude's own answer.

- 2026-10-26 · Learner skipped the follow-up ("continue"). Gave the answer (5 entries: user/assistant/user/assistant/user). Re-test history in M3.
- 2026-10-26 · M1 Step 7a sent: git init, git status, git check-ignore -v .env, git add ., git status, commit. Git identity set, default branch main, gh 2.96.0 logged in as ambarachristian.

- 2026-10-26 · M1 Step 7a done. Commit 8299c79 "Milestone 1: first Claude API call, system prompt, streaming", 6 files, .env not tracked.
- 2026-10-26 · M1 Step 7b sent: gh repo create tool-using-assistant --public --source=. --remote=origin --push. Name was free on ambarachristian.

- 2026-10-26 · M1 Step 7b done. Public repo https://github.com/ambarachristian/tool-using-assistant, 6 files, no .env. **MILESTONE 1 COMPLETE.**

## Milestone 2 steps (expected)
1. tools.py with CALCULATOR_TOOL schema (operation enum add/subtract/multiply/divide/power, a, b) + see_tool_call.py to print the tool_use block (no execution)
2. calculator() function in tools.py (plain Python, no eval)
3. Weather tool: schema + get_weather() with httpx (Open-Meteo geocoding, then forecast); may take 2 steps
4. read_file tool: schema + read_file() confined to a notes/ folder (model output is untrusted)
5. TOOLS list + run_tool(name, input) dispatcher; one manual round: ask → tool_use → run it → print result
6. Understanding check + commit + push

- 2026-10-26 · M2 Step 1 sent: tools.py (CALCULATOR_TOOL) + see_tool_call.py (prints stop_reason, input tokens, each block; tool_use id/name/input).

- 2026-10-26 · M2 Step 1 done. Output: stop_reason tool_use, 534 input tokens, one tool_use block {'operation': 'multiply', 'a': 1234.5, 'b': 678.9}. No text/thinking block.
- 2026-10-26 · M2 Step 2 sent: calculator() in tools.py using an OPERATIONS dict (operator module) and Decimal(str(x)) for exact decimal math (float gave 838102.0499999999). Deliberate crash test: divide by 0 → decimal.DivisionByZero; asked what that would do to the agent (motivates M4).

- 2026-10-26 · M2 Step 2 done. calculator() correct (verified 838102.05 / 0.3 / 1024; divide by 0 → DivisionByZero). Learner said "done" without answering the crash question; gave the answer (whole program would crash; want an error message sent back to Claude instead → M4).
- 2026-10-26 · M2 Step 3 sent: WEATHER_TOOL schema (city required, unit optional enum celsius/fahrenheit, says "no forecasts") at bottom of tools.py; see_tool_call.py now passes both tools; 3 test questions (raining in Tokyo → get_weather, 17.5% of 2340 → calculator, capital of Japan → no tool, end_turn).
- Open-Meteo facts (checked 2026-10-26): geocoding unknown city → 200 with no "results" key (KeyError later = M4 lesson). "Paris, France" resolves fine. Forecast `current` fields used: temperature_2m, apparent_temperature, relative_humidity_2m, precipitation, cloud_cover, wind_speed_10m; plus temperature_unit, timezone=auto.

- 2026-10-26 · M2 Step 3 done. All 3 choices right: Tokyo rain → get_weather {'city': 'Tokyo'}; 17.5% of 2340 → calculator multiply 2340×0.175; capital of Japan → end_turn, text only. ~750 input tokens with 2 tools. Learner pasted a Python line into PowerShell (French error "Le mot clé « from » n'est pas pris en charge…"); explained python vs powershell code blocks. Learner's PowerShell is in French.
- 2026-10-26 · M2 Step 3b sent: imports json + httpx at top of tools.py; GEOCODING_URL, FORECAST_URL, CURRENT_FIELDS; get_weather(city, unit="celsius") → json.dumps({place, current, units}). Checks: Tokyo, New York fahrenheit, Xyzzyville → KeyError 'results' (planned, M4).

- 2026-10-26 · M2 Step 3b done. get_weather correct: Tokyo °C, New York °F, Xyzzyville → KeyError 'results' at line 85 (planned).
- Teaching note: learner consistently skips mid-step questions (says "done"). Keep questions to the milestone-end checks; give short answers inline instead.
- 2026-10-26 · M2 Step 4 sent: create notes/shopping.md (Rice 7.50, Olive oil 9.80, Coffee beans 12.25, Tomatoes 4.60); READ_FILE_TOOL + read_file(path) with NOTES_DIR = Path(__file__).parent / "notes", resolve() + is_relative_to() guard → PermissionError, MAX_CHARS 20_000 with explicit truncation note, utf-8. Checks: shopping.md, ../.env (blocked).

- 2026-10-27 · M2 Step 4 done. notes/shopping.md OK; read_file blocks ../.env, ..\.env, C:/Windows/win.ini, sub/../../.env.
- 2026-10-27 · M2 Step 5 sent: TOOLS list, TOOL_FUNCTIONS dict, run_tool(name, tool_input) at bottom of tools.py; see_tool_call.py uses tools=TOOLS and prints run_tool result inside the tool_use branch. Tests: "What's in my notes file shopping.md?" and "Compare the weather in Tokyo and Paris right now." (expect 2 tool_use blocks = parallel tool use).
- Open issue for M4/M5: Claude can't discover note file names (no list tool). Options: list note files in the system prompt, or add a list_notes tool. Decide before the 10-question eval.

- 2026-10-28 · M2 Step 5 done. run_tool + see_tool_call.py correct. Run 2 showed parallel tool use: 2 get_weather blocks (Tokyo, Paris) in one response, 927 input tokens with 3 tools.
- 2026-10-28 · M2 Step 6: learner skipped the milestone check ("continue"). Gave short answers (your program calls Open-Meteo, Claude only sends a tool_use block; the description is a hint, the resolve/is_relative_to check is the lock; ids match tool_results to requests). Offered to drop checks if they want; otherwise keep asking at milestone ends.
- 2026-10-28 · M2 Step 7 sent: git add . / commit "Milestone 2: calculator, weather and read_file tools as JSON schemas" / git push.

- 2026-10-28 · M2 Step 7 done. Commit 4a1ce47 pushed. **MILESTONE 2 COMPLETE.**

## Milestone 3 steps (expected)
1. agent.py part 1: setup, MODEL, MAX_ITERATIONS = 10, agent SYSTEM_PROMPT (use tools over guessing, explain which tools and why), handle_tool_calls(response) → list of tool_result blocks + "[tool]" trace line
2. agent.py part 2: run_agent(question) loop (append assistant content, stop if stop_reason != "tool_use", append ONE user message with all tool_results, cap) + `if __name__ == "__main__"` with sys.argv question
3. Test runs: shopping total (read_file → calculator chain), multi-step math, no-tool question; then MAX_ITERATIONS = 1 to see the cap
4. Print the message history after a run (see the transcript the API sees)
5. Understanding check + commit + push

- 2026-10-28 · M3 Step 1 sent: agent.py part 1 (setup, SYSTEM_PROMPT, MAX_ITERATIONS, handle_tool_calls). Check: one-liner that makes one call and prints handle_tool_calls() output for "What is 2.5 to the power of 3?" → [{'type': 'tool_result', 'tool_use_id': 'toolu_…', 'content': '15.625'}].

- 2026-10-28 · M3 Step 1 done. agent.py part 1 correct; one-liner gave calculator power 2.5^3 → [{'type': 'tool_result', 'tool_use_id': 'toolu_01Uy…', 'content': '15.625'}].
- 2026-10-28 · M3 Step 2 sent: run_agent(question) loop + __main__ with sys.argv. Checks: `python agent.py` (shopping total = 34.15) and `python agent.py "Is it warmer in Lisbon or Oslo right now, and by how many degrees?"` (parallel weather, then calculator subtract).

- 2026-10-28 · M3 Step 2 done (learner said "continue"; tutor ran `python agent.py` once to verify). 5 turns: read_file, then 3 sequential calculator adds, end_turn → 34.15, explained tools used. Answer used Markdown (** and tables) → ugly in terminal: fix with a prompt line in M4 streaming step.
- Observation to teach: tool granularity drives loop length (2-number calculator → one turn per addition; each turn resends history).
- 2026-10-28 · M3 Step 3 sent: test runs, no code: Lisbon vs Oslo (parallel + chain), "Who wrote Romeo and Juliet?" (no tool, 1 turn), MAX_ITERATIONS = 1 (cap message), then back to 10.

- 2026-10-28 · M3 Step 3 done ("done", no output pasted). MAX_ITERATIONS confirmed back to 10.
- 2026-10-28 · M3 Step 4 sent: run_agent(messages: list) now takes the caller's list (mutates it); describe(block) uses block.to_dict() for SDK objects; print_transcript(messages) prints one line per block with the last 6 chars of tool ids so tool_use ↔ tool_result pairs are visible. __main__ builds messages, runs, prints transcript. Check with the Lisbon/Oslo question.

- 2026-10-28 · M3 Step 4 done. run_agent(messages), describe, print_transcript, __main__ all correct (syntax OK).
- 2026-10-28 · M3 Step 5 sent: understanding check. Q1 message 2 role "user": what's in it, who made it, why "user". Q2 what breaks if only Claude's text is appended. Q3 why MAX_ITERATIONS if the loop already stops on != "tool_use".

- 2026-10-28 · M3 Step 5: learner skipped the check ("continue"). Gave short answers.
- 2026-10-28 · M3 Step 6 sent: commit "Milestone 3: hand-written agent loop with iteration cap and transcript" + push.

- 2026-10-28 · M3 Step 6 done. Commit e4e1d41 pushed. **MILESTONE 3 COMPLETE.**

## Milestone 4 steps (expected)
1. handle_tool_calls: try/except around run_tool → tool_result with is_error: True + "[tool error]" trace (errors are data for the model)
2. Clear error messages inside tools: get_weather "no place named X" (ValueError), calculator divide by zero, read_file not found → list available note files (also solves file-name discovery)
3. Input validation: strict: true + additionalProperties: false on all 3 schemas (API guarantees shape); code checks meaning (empty city, etc.), since strict can't express minLength/minimum
4. Conversation history: chat REPL (input() loop, one messages list, "quit"), follow-up questions work
5. Streaming the final answer: client.messages.stream + text_stream inside run_agent; system prompt line "plain text, no Markdown"; leave eager_input_streaming off (tiny inputs, keep strict validation) and say why
6. stop_reason handling: max_tokens / refusal messages; consider fallbacks="default" (beta server-side-fallback-2026-07-01) — check SDK support first
7. Understanding check + commit + push

- 2026-10-28 · M4 Step 1 sent: try/except in handle_tool_calls, is_error, [tool error] trace. Tests: weather in Xyzzyville (KeyError 'results'), notes file groceries.md (FileNotFoundError with full path).

- 2026-10-28 · Learner asked to speed up; chose "compact steps" via question. M4 Step 1 done: handle_tool_calls with try/except + is_error correct.
- 2026-10-28 · M4 Step 2 sent: clear errors in tools.py: get_weather ValueError "No place found named …" (uses .get("results")), calculator ValueError "Cannot divide by zero.", read_file FileNotFoundError listing available files (rglob, relative posix paths). Check: groceries.md → error lists shopping.md → Claude may retry.

- 2026-10-28 · **MODE CHANGE.** Learner: "just do all the steps and tell me, I grasped the essentials of this project." Tutor mode dropped for the rest of the project at the learner's explicit request. Claude wrote M4 steps 2–6 and M5 itself, ran the checks, and gave a key-points summary.
- 2026-10-28 · M4 steps 2–6 done by Claude:
  - tools.py: strict: true + additionalProperties: false on all 3 schemas; clear errors (unknown operation, divide by zero, Decimal overflow/undefined, empty city, unknown city, weather service down via httpx.HTTPError, empty path, file not found listing available files, non-UTF-8 file, unknown tool name).
  - agent.py: streaming via client.beta.messages.stream with fallbacks="default" (beta server-side-fallback-2026-07-01); stop_reason handling (tool_use / max_tokens / refusal / end_turn); empty refusal content not appended; chat REPL with one messages list (memory); API errors caught as a chain (auth, rate limit, connection, status); --transcript flag; system prompt asks for plain text, no Markdown; stdout forced to UTF-8.
  - eager_input_streaming deliberately left off: tool inputs are tiny and strict validation is wanted.
  - Verified live: groceries.md → error lists shopping.md → Claude reads it; chat follow-up "And in Fahrenheit?" uses Lisbon from history; divide by 0 + power in parallel → one error result, one success, clean answer.

## Technical notes (for the tutor)
- anthropic 2.3.0 = API version 2026-10-21: no temperature/top_p/top_k (400). Basic messages.create unchanged.
- claude-sonnet-5-5: adaptive thinking on by default (content may include an empty `thinking` block before `text`), effort default high, forced tool_choice any/tool returns 400 (use auto).
- Server-side fallback on Sonnet 5.5 only retries "cyber" and "frontier_llm" declines (not bio / reasoning_extraction / general_harms).

## Next
- M4 commit + push, then M5 (evaluate.py with 10 questions, eval_log.json, README with results), commit + push, final summary for the learner.
- Design decisions: manual loop (learner's requirement, no tool runner). tool_choice stays auto (Sonnet 5.5 rejects any/tool).
