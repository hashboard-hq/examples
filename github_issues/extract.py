import os
import requests
import pandas as pd
import numpy as np


def get_github_issues(owner, repo, token, per_page=30):
    issues = []
    page = 1
    headers = {"Authorization": f"token {token}"}
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&page={page}&per_page={per_page}"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to retrieve issues, status code: {response.status_code}")
            break

        page_issues = response.json()
        if not page_issues:
            break

        issues.extend(page_issues)
        page += 1

    return issues


# get issues
OWNER = os.getenv("GITHUB_REPO_OWNER")
REPO_NAME = os.getenv("GITHUB_REPO_NAME")
API_TOKEN = os.getenv("GITHUB_API_TOKEN")
issues = get_github_issues(OWNER, REPO_NAME, API_TOKEN)

df = pd.DataFrame.from_records(issues)

## clean up columns and values
df["author"] = df["user"].apply(lambda node: node["login"])
df["type"] = df["pull_request"].apply(
    lambda pr_data: "issue" if pr_data is np.NaN else "pull request"
)
df["assignee"] = df.loc[~df["assignee"].isnull()]["assignee"].apply(
    lambda node: node["login"]
)
df["milestone"] = df.loc[~df["milestone"].isnull()]["milestone"].apply(
    lambda node: node["title"]
)
df["labels"] = df["labels"].apply(lambda labels: [label["name"] for label in labels])
df["labels"] = df["labels"].apply(lambda labels: ", ".join(labels))
df["assignees"] = df["assignees"].apply(
    lambda assignees: [assignee["login"] for assignee in assignees]
)
df["reactions_count"] = df["reactions"].apply(
    lambda reactions: reactions["total_count"]
)
df["is_bug"] = df.labels.apply(lambda labels: "bug" in labels)
df["is_enhancement"] = df.labels.apply(lambda labels: "enhancement" in labels)
df["is_tech_debt"] = df.labels.apply(lambda labels: "tech_debt" in labels)
df["url"] = df["html_url"]
df["issue_number"] = df["number"]


column_order = [
    "issue_number",
    "type",
    "state",
    "state_reason",
    "title",
    "url",
    "created_at",
    "updated_at",
    "closed_at",
    "author",
    "author_association",
    "assignee",
    "body",
    "is_bug",
    "is_enhancement",
    "is_tech_debt",
    "comments",
    "active_lock_reason",
    "draft",
    "performed_via_github_app",
    "reactions_count",
    "locked",
    "labels",
    "milestone",
]

df = df[column_order]

# export to parquet file
df.to_parquet("./github_issues.parquet")
