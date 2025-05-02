import os
import requests

repo = os.environ['REPO']
pr_number = os.environ['PR_NUMBER']
token = os.environ['GITHUB_TOKEN']
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json"
}

# Получаем описание PR
pr_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}"
res = requests.get(pr_url, headers=headers)
res.raise_for_status()
pr_data = res.json()

# Считаем 👍 реакции
likes = sum(1 for r in pr_data.get("reactions", {}).values() if r == "+1") \
    if isinstance(pr_data.get("reactions"), dict) else pr_data.get("reactions", {}).get("+1", 0)

print(f"👍 Likes: {likes}")

if likes >= 50:
    # Мёрджим PR
    merge_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/merge"
    merge_res = requests.put(merge_url, headers=headers, json={
        "commit_title": f"Auto-merged PR #{pr_number} on 50+ likes 👍",
        "merge_method": "squash"
    })
    if merge_res.status_code == 200:
        print("✅ PR successfully merged!")
    else:
        print(f"❌ Merge failed: {merge_res.status_code} {merge_res.text}")
else:
    print("⏳ Not enough likes to merge.")
