import os
import json
import requests

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
GITHUB_EVENT_PATH = os.environ["GITHUB_EVENT_PATH"]
GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS_GH = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates",
}

# -------------------------
# Category mapping
# -------------------------
CATEGORY_MAP = {
    "kotlin": "Kotlin",
    "android": "Android",
    "compose": "Compose",
    "coroutine": "Coroutine",
    "oop": "OOP",
    "os": "OS",
}


def extract_category(labels):
    for label in labels:
        name = label["name"].lower()
        if name in CATEGORY_MAP:
            return CATEGORY_MAP[name]
    return "Uncategorized"


# -------------------------
# Upsert to Supabase
# -------------------------
def upsert_issue(issue):
    payload = {
        "id": issue["number"],
        "title": issue["title"],
        "category": extract_category(issue.get("labels", [])),
        "source_url": issue["html_url"],
        "created_at": issue["created_at"],
        "updated_at": issue["updated_at"],
    }

    res = requests.post(
        f"{SUPABASE_URL}/rest/v1/questions",
        headers=HEADERS_SB,
        json=payload,
    )

    if res.status_code not in (200, 201):
        print("❌ Supabase upsert failed:", res.text)
        exit(1)

    print(f"✅ Synced issue #{issue['number']}")


# -------------------------
# Main
# -------------------------
with open(GITHUB_EVENT_PATH, "r", encoding="utf-8") as f:
    event = json.load(f)

# 1️⃣ Issue 이벤트 기반
if "issue" in event:
    issue = event["issue"]

    if "pull_request" in issue:
        print("PR detected. Skipping.")
        exit(0)

    upsert_issue(issue)
    exit(0)

# 2️⃣ workflow_dispatch → 전체 이슈 마이그레이션
print("🚀 Manual trigger detected. Syncing ALL issues...")

owner, repo = GITHUB_REPOSITORY.split("/")

page = 1
while True:
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {
        "state": "all",
        "per_page": 100,
        "page": page,
    }

    res = requests.get(url, headers=HEADERS_GH, params=params)
    res.raise_for_status()

    issues = res.json()
    if not issues:
        break

    for issue in issues:
        if "pull_request" in issue:
            continue
        upsert_issue(issue)

    page += 1

print("🎉 All issues synced successfully")
