# Trending in the Last 30 Days

## Problem Statement

How might we help first-time visitors and returning enthusiasts quickly see which voice typing tools are attracting the most recent attention?

## Recommended Direction

Add a small, automatically refreshed section immediately before the README directory. Rank tools by absolute stars gained over the preceding 30 days, with total stars and percentage growth providing context.

The feature measures momentum. Its success is a useful, readable signal that requires no daily manual work. It helps first-time visitors shortlist tools worth investigating and returning readers stay up to date with the landscape.

## MVP Scope

### README presentation

- Title: **Trending in the Last 30 Days**. Add a contents link.
- Table columns: **Tool | Stars gained (30 days) | Total stars | Growth**.
- Show ten entries by default; expose the count as a Python configuration constant.
- Rank by absolute stars gained, descending; break ties alphabetically by tool name.
- Show the reporting date, integer star counts, and growth rounded to one decimal place.

### Repository discovery

Read entries directly from the README's **Directory** table. Accept root GitHub repository links, allowing a trailing slash; skip links into subdirectories, including Epicenter Whispering. Deduplicate repositories. No separately maintained registry or exclusion list.

### Data collection and calculation

Use a Python standard-library script to fetch each eligible repository's star history and current count:

- History: `GET /repos/{owner}/{repo}/stargazers/history`.
- Current count: `GET /repos/{owner}/{repo}/stargazers/count`.
- Sum daily history buckets for the preceding 30 calendar dates, excluding today, using UTC date interpretation as a practical convention.
- Calculate growth as `gained / (current_total - gained) × 100`. Display `—` when the denominator is zero or negative.
- Label the column simply **Growth**; accept small discrepancies from timing and historical-count estimation.
- Retry each failed request twice with short delays, then skip repositories lacking either result.
- Publish up to the configured number of successfully fetched entries without coverage notes. If every repository fails, retain the existing section.

API reference: [GitHub REST API endpoints for starring](https://docs.github.com/en/rest/activity/starring).

### Automation

Run through GitHub Actions daily at **00:03 UTC**, with a manual trigger. Replace only a marked generated README block and commit changes directly to `main` when the content changes. Use the workflow token; no third-party Python dependencies.

## Validated Assumptions

- [x] **Star momentum is useful to readers.** Review the rendered table for quick comparison and clear ordering.
- [x] **Approximate growth is sufficient.** Exact historical totals, timezone alignment, and synchronization differences do not justify additional infrastructure.
- [x] **Root repository links are a sufficient eligibility rule.** Accept that this is a lightweight heuristic for excluding shared repositories.
- [x] **Routine automation is enough.** Occasional maintenance remains possible; direct workflow commits assume repository permissions allow them.

## Validation

Validate parsing against the current directory, then test date-window boundaries, sorting, configurable row counts, zero denominators, retries, and skipped repositories. Verify that generation preserves the rest of the README and produces identical output for identical inputs. Finish with a manual workflow run.

## Not Doing (and Why)

- **Quality, reliability, usage, or maintenance scores** — these require different evidence.
- **Hidden-gem discovery, percentage-based ranking, or platform leaderboards** — the objective is absolute momentum.
- **Historical snapshots, rank-change tracking, charts, or dashboards** — the daily table is sufficient.
- **Exclusion databases, external services, or third-party Python libraries** — derive inputs from the directory and keep the implementation small.
- **Precision disclaimers or partial-coverage notices** — keep the reader experience minimal.

## Open Questions

None blocking the agreed MVP.
