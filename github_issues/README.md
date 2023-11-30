# Github Issues

This project extracts all Github issues a repo and uploads the data as a parquet file to Hashboard for use in charts and dashboards.

Pull Requests are included as a type of issue.

The ETL and dashboard building happen in a Github action, `github_issues_etl.yml`.

## Secrets Setup

The Github action depends on a set of 6 secrets:

1. `GITHUB_API_TOKEN`: Used to authenticate requests to get issues from Github ([docs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens))
2. `GITHUB_REPO_NAME`: The name of the repo to retrieve issues for
3. `GITHUB_REPO_OWNER`: The name of the owner of the repo to retrieve issues for, since repo names are not unique.

The following Hashboard secrets are all provided as part of a generated access key ([docs](https://docs.hashboard.com/docs/data-ops/cli/credentials)). 4. `GITHUB_HASHBOARD_PROJECT_ID` 5. `GITHUB_HASHBOARD_ACCESS_KEY_ID` 6. `GITHUB_HASHBOARD_SECRET_ACCESS_KEY_TOKEN`

Hashboard is hosting a version of this example at demo.hashboard.com for issues from the dbt-core repo.
