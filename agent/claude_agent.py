"""
Wires Claude tool-calling to the explain_plan tool from server.py.

This file is intentionally incomplete. Filling in the TODOs is the Day 7-8
work in the repo root README's phase breakdown, that's the actual "AI agent"
rep this project is meant to give you, not something to skip by having it
pre-built.

Reference for the tool-calling pattern: Anthropic's Messages API tool use
docs (docs.claude.com). The shape is:
  1. Send a message with `tools=[...]` describing explain_plan.
  2. If Claude's response has stop_reason == "tool_use", pull out the tool
     call, run the actual Python function (import _summarize/explain_plan
     from server.py, don't shell out), and send the result back in a new
     message with role "user" and a tool_result content block.
  3. Claude's next response is the final plain-English answer.
"""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

from server import explain_plan  # reuse the same function server.py exposes

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

TOOLS = [
    {
        "name": "explain_plan",
        "description": "Summarize a terraform plan JSON file in plain English: what's being created, updated, or destroyed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "plan_path": {
                    "type": "string",
                    "description": "Path to a JSON file produced by `terraform show -json tfplan.binary > plan.json`",
                }
            },
            "required": ["plan_path"],
        },
    }
]


def ask(question: str) -> str:
    """
    TODO (Day 7): implement the tool-calling loop.

    1. messages = [{"role": "user", "content": question}]
    2. response = client.messages.create(model=..., max_tokens=1024, tools=TOOLS, messages=messages)
    3. If response.stop_reason == "tool_use": find the tool_use block,
       call explain_plan(**tool_use_block.input), append the assistant
       response and a user message containing a tool_result block to
       `messages`, then call client.messages.create again.
    4. Return the text from the final response.

    Test with: ask("What would change if I applied my terraform plan?
    The plan file is at sample_plan.json")
    """
    raise NotImplementedError("Fill this in, see the TODO above and the repo root README, Phase 3, Day 7.")


if __name__ == "__main__":
    print(ask("Summarize what would change based on sample_plan.json"))
