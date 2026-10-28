# Tutor progress: Tool-using assistant

Roadmap: AI agents · Level 1 of 5 (Foundations) · Project 2 of 26
Mode: tutor mode. The learner types every project file. Claude only writes this file.
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

## Technical notes (for the tutor)
- anthropic 2.3.0 = API version 2026-10-21: no temperature/top_p/top_k (400). Basic messages.create unchanged.
- claude-sonnet-5-5: adaptive thinking on by default (content may include an empty `thinking` block before `text`), effort default high, forced tool_choice any/tool returns 400 (use auto).
- Plan for M4: handle stop_reason "refusal" and mention server-side fallbacks (beta server-side-fallback-2026-07-01, fallbacks="default").

## Next
- Verify M2 commit + push (notes/shopping.md, tools.py, see_tool_call.py tracked; no __pycache__/.env). Then **Milestone 3 Step 1**: agent.py, the loop. Plan: messages list → create(tools=TOOLS) → if stop_reason == "tool_use": append assistant content, run each tool_use via run_tool, append ONE user message with all tool_result blocks (tool_use_id) → repeat; stop on end_turn; MAX_ITERATIONS cap. Keep blocks under 40 lines (split loop across 2 steps if needed). Commit TUTOR_PROGRESS.md updates with the M2 commit.
- Design decisions: manual loop (learner's requirement, no tool runner). tool_choice stays auto (Sonnet 5.5 rejects any/tool). strict: true + additionalProperties: false saved for M4 input validation.
