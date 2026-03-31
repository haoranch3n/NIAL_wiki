#!/usr/bin/env python3
"""Upload a file as an attachment to a Confluence page."""

import json
import os
import sys
from pathlib import Path

import requests

CONFLUENCE_URL = os.environ.get("CONFLUENCE_URL", "https://wiki.stjude.org")
CONFLUENCE_TOKEN = os.environ.get("CONFLUENCE_PERSONAL_TOKEN")

if not CONFLUENCE_TOKEN:
    mcp_json = Path.home() / ".cursor" / "mcp.json"
    if mcp_json.exists():
        cfg = json.loads(mcp_json.read_text())
        env = cfg.get("mcpServers", {}).get("mcp-atlassian", {}).get("env", {})
        CONFLUENCE_URL = env.get("CONFLUENCE_URL", CONFLUENCE_URL)
        CONFLUENCE_TOKEN = env.get("CONFLUENCE_PERSONAL_TOKEN")

if not CONFLUENCE_TOKEN:
    sys.exit("Error: No Confluence token found.")


def upload(page_id: str, filepath: str, comment: str | None = None):
    headers = {
        "Authorization": f"Bearer {CONFLUENCE_TOKEN}",
        "X-Atlassian-Token": "nocheck",
    }
    fname = os.path.basename(filepath)
    with open(filepath, "rb") as f:
        r = requests.post(
            f"{CONFLUENCE_URL}/rest/api/content/{page_id}/child/attachment",
            headers=headers,
            files={"file": (fname, f, "text/csv")},
            data={"comment": comment or ""},
        )
    print(f"Status: {r.status_code}")
    if r.ok:
        result = r.json()
        results = result.get("results", [])
        if results:
            att = results[0]
            print(f"Attached: {att['title']} (id: {att['id']})")
        else:
            print(r.text[:300])
    else:
        print(r.text[:500])


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(f"Usage: {sys.argv[0]} <page_id> <file_path> [comment]")
    page_id = sys.argv[1]
    filepath = sys.argv[2]
    comment = sys.argv[3] if len(sys.argv) > 3 else None
    upload(page_id, filepath, comment)
