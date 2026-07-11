"""
MCP server exposing one tool: explain_plan.

Reads a `terraform plan -json` output file and returns a plain-English
summary of what would change (resources added, changed, destroyed), in the
same spirit as the runbook voice used elsewhere in this repo: plain
practitioner English, no padding, specific about what's actually changing.

Run standalone for local testing:
    python server.py

This is the Day 6 deliverable per the repo root README's phase breakdown:
a working MCP server you can test directly, before wiring Claude tool-calling
on top of it in claude_agent.py.
"""

import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("terraform-explainer")


def _load_plan(plan_path: str) -> dict:
    path = Path(plan_path)
    if not path.exists():
        raise FileNotFoundError(
            f"No plan file at {plan_path}. Generate one with: "
            f"terraform plan -out=tfplan.binary && terraform show -json tfplan.binary > plan.json"
        )
    return json.loads(path.read_text())


def _summarize(plan: dict) -> dict:
    """Pull create/update/delete counts and resource addresses out of a
    `terraform show -json` plan document. Returns a plain dict so it's easy
    to test without going through the MCP tool-calling layer."""
    changes = plan.get("resource_changes", [])

    creates, updates, deletes, no_ops = [], [], [], []
    for rc in changes:
        actions = rc.get("change", {}).get("actions", [])
        address = rc.get("address", "unknown")
        if actions == ["create"]:
            creates.append(address)
        elif actions == ["update"]:
            updates.append(address)
        elif actions == ["delete"]:
            deletes.append(address)
        elif actions == ["no-op"]:
            no_ops.append(address)
        elif "delete" in actions and "create" in actions:
            deletes.append(f"{address} (replace)")
            creates.append(f"{address} (replace)")

    return {
        "total_resources_changed": len(creates) + len(updates) + len(deletes),
        "creates": creates,
        "updates": updates,
        "deletes": deletes,
        "unchanged": len(no_ops),
    }


@mcp.tool()
def explain_plan(plan_path: str) -> str:
    """Summarize a terraform plan JSON file in plain English.

    Args:
        plan_path: path to a JSON file produced by
            `terraform show -json tfplan.binary > plan.json`
    """
    plan = _load_plan(plan_path)
    summary = _summarize(plan)

    lines = [
        f"{summary['total_resources_changed']} resource(s) would change, "
        f"{summary['unchanged']} unchanged."
    ]
    if summary["creates"]:
        lines.append(f"Create ({len(summary['creates'])}): " + ", ".join(summary["creates"]))
    if summary["updates"]:
        lines.append(f"Update ({len(summary['updates'])}): " + ", ".join(summary["updates"]))
    if summary["deletes"]:
        lines.append(f"Destroy ({len(summary['deletes'])}): " + ", ".join(summary["deletes"]))
    if not (summary["creates"] or summary["updates"] or summary["deletes"]):
        lines.append("No changes. Infrastructure matches configuration.")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run()
