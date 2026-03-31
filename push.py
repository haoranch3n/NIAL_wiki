#!/usr/bin/env python3
"""Push cached Confluence pages via REST API without piping content through the LLM."""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

CACHE_DIR = Path(__file__).parent
CONFLUENCE_URL = os.environ.get("CONFLUENCE_URL", "https://wiki.stjude.org")
CONFLUENCE_TOKEN = os.environ.get("CONFLUENCE_PERSONAL_TOKEN")

# Fall back to reading from mcp.json if env vars aren't set
if not CONFLUENCE_TOKEN:
    mcp_json = Path.home() / ".cursor" / "mcp.json"
    if mcp_json.exists():
        cfg = json.loads(mcp_json.read_text())
        env = cfg.get("mcpServers", {}).get("mcp-atlassian", {}).get("env", {})
        CONFLUENCE_URL = env.get("CONFLUENCE_URL", CONFLUENCE_URL)
        CONFLUENCE_TOKEN = env.get("CONFLUENCE_PERSONAL_TOKEN")

if not CONFLUENCE_TOKEN:
    sys.exit("Error: No Confluence token found. Set CONFLUENCE_PERSONAL_TOKEN or configure ~/.cursor/mcp.json")

HEADERS = {
    "Authorization": f"Bearer {CONFLUENCE_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def find_cached_file(identifier: str) -> Path:
    """Find a cache file by page ID, slug, or full filename."""
    # Direct path
    p = CACHE_DIR / identifier
    if p.exists():
        return p

    # Search by page ID suffix
    for f in CACHE_DIR.glob("*.html"):
        if f.stem.endswith(f"-{identifier}"):
            return f

    # Partial slug match
    for f in CACHE_DIR.glob("*.html"):
        if identifier in f.stem:
            return f

    sys.exit(f"Error: No cached file matching '{identifier}' in {CACHE_DIR}")


def extract_page_id(filename: str) -> str:
    """Extract numeric page ID from filename like 'cursor-getting-started-265978362.html'."""
    m = re.search(r"-(\d+)\.html$", filename)
    if not m:
        sys.exit(f"Error: Cannot extract page ID from '{filename}'. Expected format: <slug>-<pageId>.html")
    return m.group(1)


def get_page(page_id: str) -> dict:
    """Fetch current page metadata (title, version)."""
    r = requests.get(
        f"{CONFLUENCE_URL}/rest/api/content/{page_id}",
        headers=HEADERS,
        params={"expand": "version"},
    )
    r.raise_for_status()
    return r.json()


def update_page(page_id: str, title: str, body_storage: str, current_version: int, comment: str | None = None) -> dict:
    """Push new content to the page."""
    payload = {
        "id": page_id,
        "type": "page",
        "title": title,
        "body": {"storage": {"value": body_storage, "representation": "storage"}},
        "version": {"number": current_version + 1},
    }
    if comment:
        payload["version"]["message"] = comment

    r = requests.put(
        f"{CONFLUENCE_URL}/rest/api/content/{page_id}",
        headers=HEADERS,
        json=payload,
    )
    r.raise_for_status()
    return r.json()


def main():
    parser = argparse.ArgumentParser(description="Push a cached .html file to Confluence")
    parser.add_argument("identifier", help="Page ID, slug, or filename (e.g. 265978362 or cursor-getting-started)")
    parser.add_argument("-m", "--message", help="Version comment", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Show what would be pushed without pushing")
    args = parser.parse_args()

    cached = find_cached_file(args.identifier)
    page_id = extract_page_id(cached.name)
    body = cached.read_text(encoding="utf-8")

    print(f"Cache file : {cached.name}")
    print(f"Page ID    : {page_id}")
    print(f"Content    : {len(body):,} chars")

    page = get_page(page_id)
    title = page["title"]
    version = page["version"]["number"]
    print(f"Live title : {title}")
    print(f"Live ver   : {version}")

    if args.dry_run:
        print("\n[dry-run] Would update to version", version + 1)
        return

    result = update_page(page_id, title, body, version, args.message)
    new_ver = result["version"]["number"]
    print(f"\nPushed v{new_ver}: {CONFLUENCE_URL}/pages/viewpage.action?pageId={page_id}")


if __name__ == "__main__":
    main()
