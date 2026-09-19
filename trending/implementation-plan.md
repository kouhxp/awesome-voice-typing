# Minimal implementation plan: Trending in the Last 30 Days

Follow [vision.md](vision.md). Build one standard-library Python script, one small test file, and one daily workflow. Keep all supporting code in `trending/`; only the workflow and the README presentation live elsewhere.

## 1. Generate the README section — complete

**Files:** `trending/update.py`, `README.md`. **Scope:** Small. **Depends on:** Nothing.

- [x] Read only the Directory table's tool links. Accept root GitHub URLs with an optional trailing slash; deduplicate case-insensitively, keeping the first name. Skip subdirectory links such as Epicenter Whispering. Ignore badges and other README sections.
- [x] Fetch history and current count sequentially using `urllib.request` and `GITHUB_TOKEN`. Request `/repos/{owner}/{repo}/stargazers/history?per_page=6` and `/repos/{owner}/{repo}/stargazers/count`. Six recent weeks cover the window without pagination. Sum dates from UTC today minus 30 days through yesterday. Use a request timeout and two retries with short fixed delays; skip a repository if either result remains unavailable. Log failures to the workflow console.
- [x] During implementation, add **Trending in the Last 30 Days**, its Contents link, and block markers immediately before Directory. The script replaces only the content between `<!-- trending:start -->` and `<!-- trending:end -->`. Show `Tool | Stars gained (30 days) | Total stars | Growth`, linked names, integer counts, and `Last updated: YYYY-MM-DD` using the UTC run date. Sort by gained stars descending, then name case-insensitively; take `TOP_N = 5`. Growth is `gained / (current_total - gained) * 100`, rounded to one decimal, or `—` for a nonpositive denominator. If all repositories fail, leave the existing block untouched; otherwise publish available rows without coverage notes.

Keep this as a few functions in one file: discover, fetch, calculate, render, replace. Resolve the README relative to the script. Missing block markers should cause a clear error instead of guessing where to write.

**Verify:** Run `python3 trending/update.py` with a token in the environment, inspect `git diff -- README.md`, and preview the table. The first change adds the section and Contents link; subsequent changes stay inside the markers.

Both endpoints are documented in the [GitHub starring API](https://docs.github.com/en/rest/activity/starring) and returned HTTP 200 for Handy during planning on 2026-09-17. UTC interpretation and approximate growth remain intentional simplifications.

Verified 2026-09-17: 47 repositories fetched; table generated; outside-block preservation and focused checks passed.

## 2. Check the behavior that matters — complete

**File:** `trending/test_update.py`. **Scope:** Small. **Depends on:** Task 1.

- [x] A compact `unittest` suite checks directory-only discovery, trailing slashes, deduplication, and subdirectory exclusion.
- [x] Fixed dates and sample responses check the 30-day boundaries, alphabetical ties, configurable row count, and growth including zero/negative denominators.
- [x] Mocked requests check retries, skipped repositories, and all-failed preservation; rendering checks identical output for identical inputs and preservation outside the block.

**Verify / checkpoint:** `python3 -m unittest discover -s trending` passes without network access. Review one live README result before connecting automation. No extra test framework or exhaustive error matrix.

Verified: all 7 offline tests pass.

## 3. Run daily and commit changes — complete

**File:** `.github/workflows/trending.yml`. **Scope:** Small. **Depends on:** Tasks 1–2.

- [x] Run on `schedule` with cron `3 0 * * *` and `workflow_dispatch`, using `ubuntu-latest`. Use one concurrency group to avoid overlapping updater runs.
- [x] Check out `main` with `actions/checkout`, retain its default token credentials, run the tests and script with the runner's Python 3, and pass `GITHUB_TOKEN: ${{ github.token }}` to the script. No dependency installation.
- [x] Grant `contents: write`. Configure Git as `github-actions[bot]` with email `41898282+github-actions[bot]@users.noreply.github.com`. Stage only `README.md`; if its staged diff is nonempty, commit and `git push origin HEAD:main`. A rejected push can wait for the next daily run; no force push or conflict-recovery machinery.

**Verify / final checkpoint:** Once installed on `main`, manually run the workflow from the Actions tab. Confirm a bot commit updates only the generated block. Confirm a run with unchanged generated content makes no commit.

Verified 2026-09-17: deployed to `main`; two live runs passed (47 repositories, README-only bot commits). Unchanged-output/no-commit behavior passed in a temporary Git repository; live data changed between runs. [Latest run](https://github.com/primaprashant/awesome-voice-typing/actions/runs/35178225986).

## Setup for unattended commits

Checked this repository through the GitHub API on **2026-09-17**:

| Setting | Current state |
| --- | --- |
| Default branch | `main` |
| Actions | Enabled; all actions allowed |
| `main` protection | Unprotected; no effective branch rules returned |
| Default workflow token permissions | Read-only |

**No repository settings change appears necessary.** Add this to the workflow:

```yaml
permissions:
  contents: write
```

Explicit workflow permissions can override the read-only default. Keep that default as-is; the broader “Read and write permissions” setting is unnecessary. GitHub supplies the token automatically, so no personal access token, custom secret, GitHub App, or PR-approval setting is needed. See [workflow permissions](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository) and the official [checkout push example](https://github.com/actions/checkout#push-a-commit-using-the-built-in-token).

The one-time setup is to put the script, tests, README markers, and workflow on `main`, then perform the manual verification above. Future [branch protection rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) must continue to permit the bot's direct push; `contents: write` does not bypass them.

GitHub schedules are best-effort, so 00:03 UTC is the requested time, not a precision guarantee. Public-repository schedules can be disabled after 60 days without repository activity. Accept occasional maintenance instead of adding a keepalive system. See [scheduled workflow behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

That completes the MVP: no database, snapshots, cache, charts, external services, separate repository registry, or generalized framework.
