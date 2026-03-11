import requests
import os

REPO = "chanho0908/Interview-Concept-Summary"
TOKEN = os.environ["GITHUB_TOKEN"]

LABEL_MAP = {
    "Kotlin": "Kotlin",
    "Android": "Android",
    "Compose": "Compose",
    "Coroutine": "Coroutine",
    "OOP": "OOP",
    "OS": "OS",
}

headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

issues = requests.get(
    f"https://api.github.com/repos/{REPO}/issues?state=open&per_page=100",
    headers=headers
).json()

grouped = {v: [] for v in LABEL_MAP.values()}

for issue in issues:
    if "pull_request" in issue:
        continue

    labels = [l["name"] for l in issue["labels"]]
    for label in labels:
        if label in LABEL_MAP:
            grouped[LABEL_MAP[label]].append(
                f"- [{issue['title']}]({issue['html_url']})"
            )

readme = """## Interview-Concept-Summary

### ✅ 면접 질문 모음집
📍 안드로이드 개발자 면접을 대비해  
내가 이해한 개념들을 **면접에서 설명할 수 있는 답변 형태**로 정리하기 위한 공간입니다.

---

"""

for category in ["Kotlin", "Android", "Compose", "Coroutine", "OOP", "OS"]:
    items = grouped.get(category, [])
    if not items:
        continue

    readme += f"""
<details>
  <summary><strong> {category}</strong></summary>

{chr(10).join(items)}

</details>
"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
