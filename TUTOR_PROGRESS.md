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

## Technical notes (for the tutor)
- anthropic 2.3.0 = API version 2026-10-21: no temperature/top_p/top_k (400). Basic messages.create unchanged.
- claude-sonnet-5-5: adaptive thinking on by default (content may include an empty `thinking` block before `text`), effort default high, forced tool_choice any/tool returns 400 (use auto).
- Plan for M4: handle stop_reason "refusal" and mention server-side fallbacks (beta server-side-fallback-2026-07-01, fallbacks="default").

## Next
- Verify commit (git log, git ls-files: .env must NOT be listed). Then M1 Step 7b: gh repo create tool-using-assistant --public --source=. --push. Then Milestone 2. Old line for reference: M1 Step 7: git init, first commit, public GitHub repo, push (check .env is NOT staged).
