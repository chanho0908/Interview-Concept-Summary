import os
import json
import requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
GITHUB_EVENT_PATH = os.environ["GITHUB_EVENT_PATH"]

# -------------------------------------------------
# Load GitHub event payload
# -------------------------------------------------
with open(GITHUB_EVENT_PATH, "r", encoding="utf-8") as f:
    event = json.load(f)

issue = event.get("issue")

# workflow_dispatch (전체 마이그레이션) 대비
if issue is None:
    print("No single issue in payload. Skipping.")
    exit(0)

# PR 제외
if "pull_request" in issue:
    print("Pull request detected. Skipping.")
    exit(0)

# -------------------------------------------------
# Category mapping (label → category)
# -------------------------------------------------
def extract_category(labels):
    for label in labels:
        name = label["name"].lower()
        if name in ["kotlin", "coroutine", "android", "compose"]:
            return name.capitalize()
    return "Uncategorized"

category = extract_category(issue.get("labels", []))

# -------------------------------------------------
# Supabase UPSERT payload (스키마 정합)
# -------------------------------------------------
payload = {
    "id": issue["number"],
    "title": issue["title"],
    "category": category,
    "source_url": issue["html_url"],
    "created_at": issue["created_at"],
    "updated_at": issue["updated_at"],
}

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

response = requests.post(
    f"{SUPABASE_URL}/rest/v1/questions",
    headers=headers,
    json=payload,
)

if response.status_code not in (200, 201):
    print("❌ Supabase sync failed")
    print("Status:", response.status_code)
    print("Response:", response.text)
    exit(1)
