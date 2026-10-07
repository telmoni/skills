#!/usr/bin/env bash
# The starting project: a sync that treats every non-2xx answer as fatal.
set -euo pipefail
cat > sync.py <<'EOF'
"""Nightly: mirror the Telmoni project roster into the CRM."""

import os
import sys

import requests

ENDPOINT = os.environ.get("TELMONI_ENDPOINT", "https://telmoni.com")


def fetch_members():
    resp = requests.get(
        f"{ENDPOINT}/v1/members",
        headers={"Authorization": f"Bearer {os.environ['TELMONI_API_KEY']}"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["members"]


def main():
    try:
        members = fetch_members()
    except requests.HTTPError as err:
        print(f"sync failed: {err}", file=sys.stderr)
        sys.exit(1)
    for member in members:
        print(member["member_id"], member["role"])  # stands in for the CRM upsert


if __name__ == "__main__":
    main()
EOF
