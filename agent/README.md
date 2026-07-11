# Phase 3: Claude + MCP agent (explain_plan only, baseline scope)

`explain-resource` (the second tool) is a stretch goal, see repo root README. This phase is scoped to one tool: `explain_plan`.

## Prerequisites

- Python 3.10+
- An Anthropic API key (console.anthropic.com), set as `ANTHROPIC_API_KEY` in a local `.env` file (gitignored, never commit it)
- `pip install -r requirements.txt`
- A `terraform plan` JSON file to test against. Use `sample_plan.json` in this folder for a zero-setup test, or generate a real one from Phase 1/2:
  ```bash
  cd ../okta   # or ../aws
  terraform plan -out=tfplan.binary
  terraform show -json tfplan.binary > ../agent/my_plan.json
  ```

## Steps

**Day 6: get the MCP server working standalone.**
1. `python -c "from server import explain_plan; print(explain_plan('sample_plan.json'))"`
2. Confirm it prints a plain-English summary (2 creates, 1 update, 1 no-op, based on `sample_plan.json`). If this works, the tool logic itself is solid before Claude enters the picture at all, easier to debug in isolation.
3. Optional: run `python server.py` to start it as an actual MCP server over stdio, and connect with any MCP-compatible client (e.g. Claude Desktop's local MCP config) to confirm it's discoverable as a tool.

**Day 7: wire Claude tool-calling.**
4. Open `claude_agent.py`. The `TOOLS` schema and imports are done, `ask()` is a stub with a `TODO` and a numbered outline of the loop.
5. Implement the loop: send the question with `tools=TOOLS`, check `stop_reason == "tool_use"`, call the real `explain_plan()` function, send the result back as a `tool_result` block, get Claude's final answer.
6. Test: `python claude_agent.py` should print a natural-language answer referencing the actual resources in `sample_plan.json`.

**Day 8: test against real plans, tune.**
7. Point it at a real plan from Phase 1 or 2 (see Prerequisites step above).
8. Try a few different phrasings of the question, confirm Claude reliably calls the tool rather than guessing from its own knowledge.

## Expected output

`claude_agent.py` prints a natural-language summary mentioning specific resource addresses (e.g. "This plan creates two Okta groups, `it_engineering` and `it_admins`, and updates one AWS security group"), not a generic non-answer.

## Rollback

No infrastructure to tear down, this phase only reads plan files, it never runs `terraform apply`. Revoke the Anthropic API key from the console if you're done and want to be tidy.

## Edge cases

- **Don't let the agent call `terraform apply`.** This tool is read-only by design, it summarizes a plan file, it never executes Terraform. Keep it that way, an agent with write access to infrastructure is a much bigger scope than this project.
- **Large plans.** `sample_plan.json` is tiny on purpose. A real plan with 50+ resources will produce a long tool result, if that happens, consider truncating or grouping in `_summarize()` before returning it to Claude, otherwise you're burning context on resource names Claude doesn't need individually.
- **Missing `ANTHROPIC_API_KEY`.** `claude_agent.py` will raise a `KeyError` on import if the env var isn't set. Confirm your `.env` file is in the `agent/` directory and `load_dotenv()` is finding it (it looks in the current working directory by default).
