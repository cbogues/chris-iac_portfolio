"""
Wires Claude tool-calling to the explain_plan tool from server.py.

Implemented 2026-07-14 (Day 7). The loop: send the question with the
explain_plan tool schema attached, and if Claude's response comes back with
stop_reason == "tool_use", run the real explain_plan() function locally
(never shell out, never let Claude execute anything itself), send the
result back as a tool_result block, and repeat until Claude has enough to
give a final plain-English answer.

Reference: Anthropic's Messages API tool use docs (docs.claude.com).
"""

import os

from anthropic import Anthropic
from dotenv import load_dotenv

from server import explain_plan  # reuse the same function server.py exposes

load_dotenv()

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

MODEL = "claude-sonnet-5"

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
    Tool-calling loop: send the question to Claude, and if it decides it
    needs the explain_plan tool to answer, run that tool locally and hand
    the result back so Claude can produce a final natural-language answer.
    """
    messages = [{"role": "user", "content": question}]

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=TOOLS,
        messages=messages,
    )

    # Claude may need one or more tool calls before it's ready to answer.
    # Loop until it stops asking for tools.
    while response.stop_reason == "tool_use":
        tool_use_block = next(
            block for block in response.content if block.type == "tool_use"
        )

        # Run the real function locally. This is the only place actual code
        # executes, Claude never runs anything itself, it just requests a
        # tool call and we decide whether/how to fulfill it.
        if tool_use_block.name == "explain_plan":
            tool_result = explain_plan(**tool_use_block.input)
        else:
            tool_result = f"Unknown tool: {tool_use_block.name}"

        # Feed the assistant's tool request and our tool result back in,
        # so Claude has the full exchange to reason from on the next turn.
        messages.append({"role": "assistant", "content": response.content})
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_block.id,
                        "content": tool_result,
                    }
                ],
            }
        )

        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

    final_text = "".join(
        block.text for block in response.content if block.type == "text"
    )
    return final_text


if __name__ == "__main__":
    print(ask("Summarize what would change based on sample_plan.json"))
