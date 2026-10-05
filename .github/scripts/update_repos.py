#!/usr/bin/env python3
# .github/scripts/update_repos.py — README ke LATEST REPOS block ko regenerate karta hai
# GitHub public API se non-fork repos (recent pushed first). Markers ke beech ka
# content replace hota hai — block ke bahar ka README untouched rehta hai.
import json
import os
import urllib.request

OWNER = "Sudhanshu-00"
SKIP_NAMES = {OWNER}  # profile README repo khud list nahi hoga
START = "<!-- REPOS:START -->"
END = "<!-- REPOS:END -->"
MAX_REPOS = 8

api = f"https://api.github.com/users/{OWNER}/repos?per_page=100&sort=pushed"
req = urllib.request.Request(api, headers={
    "User-Agent": "profile-auto",
    "Accept": "application/vnd.github+json",
})
token = os.environ.get("GH_TOKEN")
if token:
    req.add_header("Authorization", f"Bearer {token}")
repos = json.load(urllib.request.urlopen(req))

repos = [r for r in repos if not r.get("fork") and r["name"] not in SKIP_NAMES]
repos.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
repos = repos[:MAX_REPOS]

lines = []
for r in repos:
    name = (r["name"] or "?")[:20].ljust(20)
    lang = (r.get("language") or "-")[:10].ljust(10)
    stars = str(r.get("stargazers_count") or 0)[:4].ljust(4)
    desc = (r.get("description") or "-").replace("`", "'").replace("\n", " ")[:48]
    lines.append(f"  {name}  {lang}  *{stars}  {desc}")

block = (
    START + "\n"
    "### ⟫ LATEST REPOS `[auto-synced every 6h]`\n\n"
    "```bash\n"
    "┌──(root\U0001F480kali)-[~]\n"
    "└─$ ./repos --list --sort=pushed | head -8\n\n"
    + "\n".join(lines)
    + "\n```\n"
    + END
)

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

s = readme.find(START)
e = readme.find(END)
if s == -1 or e == -1 or e < s:
    raise SystemExit("ERROR: REPOS markers missing in README.md")

new = readme[:s] + block + readme[e + len(END):]
if new == readme:
    print("no changes — README already up to date")
else:
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new)
    print(f"README updated — {len(repos)} repos listed")
