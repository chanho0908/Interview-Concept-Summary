import os
import requests
import json

# ENV
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
GITHUB_EVENT_PATH = os.environ["GITHUB_EVENT_PATH"]

# Load GitHub event payload
with open(GITHUB_EVENT_PATH, "r", encoding="utf-8") as f:
    event = json.load(f)

issue = event.get("issue")
if issue is None:
    print("No issue payload found")
    exit(0)

# Ignore pull requests
if "pull_request" in issue:
    print("PR detected, skipping")
    exit(0)

# -------------------------
# Category mapping rule
# -------------------------
def extract_category(labels):
    for label in labels:
        name = label["name"].lower()
        if name in ["kotlin", "coroutine", "android", "compose"]:
            return name.capitalize()
    return "Uncategorized"

labels = issue.get("labels", [])
category = extract_category(labels)

# Supabase upsert payload
data = {
    "id": issue["number"],                       # GitHub issue number
    "title": issue["title"],
    "body": issue.get("body", ""),
    "category": category,
    "labels": [l["name"] for l in labels],
    "source_url": issue["html_url"],
    "created_at": issue["created_at"],
    "updated_at": issue["updated_at"],
    "synced_at": "now()"
}

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

response = requests.post(
    f"{SUPABASE_URL}/rest/v1/questions",
    headers=headers,
    json=data
)

if response.status_code not in (200, 201):
    print("❌ Supabase sync failed")
    print(response.status_code, response.text)
    exit(1)
