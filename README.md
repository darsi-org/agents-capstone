# Capstone: a school-helper agent that asks before it acts


> **Darsi briefs are short on purpose.** The in-app lesson shows tight numbered clicks. This README keeps the full commands, error fixes, and background for each milestone — open the matching **Milestone N** section when you need detail.

Build an MCP tool server for a made-up timetable, wrap it in a LangGraph agent with traces and limits, add allow-lists and human approval, evaluate with 20 tasks until unapproved writes are zero, then ship a demo and DESIGN.md.

[العربية](README.ar.md)

## What you will be able to do

- Run real free tools from a laptop or Codespaces
- Finish five milestones, each with checks you can self-verify
- Leave with a portfolio piece: a report, demo or tool tagged v1.0
- **Darsi never runs your code** — it reads your link and check file, then an advisory review

## Install once

### Windows

1. Install Python 3.12: open PowerShell and run winget install Python.Python.3.12
2. Install Git: winget install Git.Git
3. Install VS Code from https://code.visualstudio.com (free)
4. On GitHub, open https://github.com/darsi-org/agents-capstone and press Use this template, then Clone your copy
5. In the project folder run:
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   python check.py

### Mac

1. Install Homebrew from https://brew.sh if you don't have it
2. brew install python@3.12 git
3. Install VS Code from https://code.visualstudio.com
4. On GitHub open https://github.com/darsi-org/agents-capstone → Use this template → clone your copy
5. In the project folder run:
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python check.py

### Codespaces / Colab

No computer of your own? Use GitHub Codespaces: open your copy → Code → Codespaces → Create codespace. Everything installs there. Or open a notebook in Google Colab, run the first cell that clones your repo, then run python check.py. Both work from a borrowed laptop; a phone browser is enough to read results.

## Start

Press **Use this template** on https://github.com/darsi-org/agents-capstone, clone your copy, then follow milestone 1.

## Milestones

### m1: Write your tools as an MCP server (3 hours)

## Why this matters
Agents only act through tools. Clear typed tools are safer than a free-form script.

## Tools for this milestone
- **MCP Python SDK** — defines tools the model can call. Get it: pip install -r requirements.txt
- **pytest** — tests each tool including bad input. Get it: pip install -r requirements.txt

## Do this
1. Clone https://github.com/darsi-org/agents-capstone and set up the venv.
2. Open tools/server.py. finish free_rooms(day, period) and draft_message(to, text) that only writes inside drafts/.
3. Write pytest tests for each tool, including a day that does not exist.
4. Run: pytest -q && python check.py --milestone m1

## You know you're done when
- Three @mcp.tool functions exist
- tests pass
- m1 passes

## If something goes wrong
- **mcp package missing** → pip install -r requirements.txt inside the venv
- **draft writes outside drafts/** → Resolve paths with Path and reject anything outside drafts/

## What you should understand
You can expose safe, typed tools and prove bad input is rejected.

**Hand in:** tools/server.py, passing tests, and darsi-check.json that passes m1.

### m2: The loop: a LangGraph agent with a trace (4 hours)

## Why this matters
Without a trace you cannot debug why the agent called the wrong tool. Limits stop runaway loops.

## Tools for this milestone
- **LangGraph** — StateGraph agent loop. Get it: pip install -r requirements.txt
- **Ollama (optional)** — runs a small model on your computer; Codespaces can use a fake model in tests. Get it: https://ollama.com — free local models

## Do this
1. Build agent.py as a StateGraph that picks tools from your MCP server.
2. Log every step to traces/*.jsonl: request, tool calls, results, answer.
3. Cap at 6 steps and about 4,000 tokens, then stop and say so.
4. Try five requests in English and Egyptian Arabic. Run python check.py --milestone m2.

## You know you're done when
- Five traces exist
- agent.py has StateGraph
- m2 passes

## If something goes wrong
- **No local model** → Use a FakeChat in tests, or install Ollama and pull qwen2.5:1.5b
- **Agent loops forever** → Enforce max steps in the graph conditional edge

## What you should understand
You can wire a model to tools, log every step, and stop runaway runs.

**Hand in:** agent.py, five traces, and darsi-check.json that passes m2.

### m3: Guardrails: allow-lists and asking first (3 hours)

## Why this matters
The safe thing must be the only thing the agent can do. Approval before write stops silent damage.

## Tools for this milestone
- **LangGraph interrupt** — pauses before a write for human yes/no. Get it: in langgraph

## Do this
1. Allow only your three tools; draft_message may write only inside drafts/.
2. Add interrupt() before draft_message: show exactly what will be saved and wait for yes/no.
3. Put a planted instruction in data/notes.txt and show the agent treats it as data, not an order.
4. Run pytest tests/test_guardrails.py && python check.py --milestone m3

## You know you're done when
- interrupt() is used
- guardrail tests exist
- m3 passes

## If something goes wrong
- **interrupt never resumes** → In tests, invoke with a Command that approves; in demo, type yes
- **Planted instruction still triggers a send** → Never give the agent a real send tool; only draft_message exists

## What you should understand
You can force approval before writes and treat hostile text as data.

**Hand in:** Guardrail code, tests, and darsi-check.json that passes m3.

### m4: Evaluate before you trust (3 hours)

## Why this matters
Feeling that it works is not evidence. Twenty tasks with a hard target of zero unapproved writes is.

## Tools for this milestone
- **evals/tasks.jsonl** — 20 tasks with expected tool and answer. Get it: you write it

## Do this
1. Write 20 tasks: 12 normal, 4 impossible, 4 with planted instructions.
2. Run python eval.py three times per task. Target: unapproved_writes = 0.
3. Fix until you hit the target; keep a before/after table. Run python check.py --milestone m4.

## You know you're done when
- 20 tasks in evals/tasks.jsonl
- results/eval.json has unapproved_writes 0
- m4 passes

## If something goes wrong
- **Flaky evals** → Run three times and report the worst; fix non-determinism in tools
- **unapproved_writes never reaches 0** → Block the write path without approval in code, not just in the prompt

## What you should understand
You can measure agent safety with tasks and refuse to ship until unapproved writes are zero.

**Hand in:** evals/tasks.jsonl, before/after table, and darsi-check.json that passes m4.

### m5: Demo and design note (3 hours)

## Why this matters
A short demo plus a design note is how you prove control, not vibes.

## Tools for this milestone
- **GitHub Actions** — runs tests with a fake model so no GPU is needed. Get it: ci.yml in the starter

## Do this
1. Record a demo ≤3 minutes: two normal, one refused, one approval.
2. Write DESIGN.md: each tool's worst misuse and your control, who approves what, eval results, local cost.
3. Confirm Actions is green with the fake model. Tag v1.0. Run python check.py --milestone m5.

## You know you're done when
- DESIGN.md exists
- v1.0 exists
- m5 passes

## If something goes wrong
- **CI needs a real GPU** → Use the fake model path already sketched for Actions
- **Demo file too large for GitHub** → Link an unlisted YouTube/Drive file instead of committing the video

## What you should understand
You can show and document an agent that asks before it acts, with measured safety.

**Hand in:** Demo link, DESIGN.md, green Actions, v1.0, darsi-check.json that passes m5, and your explanation.

## The check

Run `python check.py` or `python check.py --milestone m2`. It only reads files, writes `darsi-check.json`, and prints English and Arabic. It uploads nothing.

## Review on Darsi

Send your repository link and `darsi-check.json` with each milestone on Darsi. Darsi reads your latest Actions run and release from GitHub's public API, adds an advisory AI review, then your teacher or the Darsi team reviews it. **Darsi never runs your code.**

## Licence

MIT — see [LICENSE](LICENSE).
