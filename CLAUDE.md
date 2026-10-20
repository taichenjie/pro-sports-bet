# Pro Sports Bet: working notes for Claude Code

Metrics-driven football bet model for J1 League and Serie A, priced against Singapore Pools odds.
Outputs 0–3 picks per day (singles or 2-leg doubles, whole bet at odds >= 1.50).

**Read `docs/design.md` before any design-related work.** It holds every agreed decision (D1–D40).
Do not contradict a decision there; if one looks wrong, raise it with CJ instead of changing it.

## Working rules

- Design before build (D9): new design decisions are agreed with CJ first, then recorded in the
  design doc's decision log and changelog. CJ updates the Claude Docs version; `docs/design.md`
  is an export of it.
- Free data sources only (D4). Scrape gently (few requests, cached, backoff). Never automate bet placement.
- Pre-match only (D21). No live betting.
- No vetoes or pass/fail signals in the model (D25): metrics become continuous features; the only
  yes/no logic is the bet rules.
- Keep changes small and reviewable: one pull request per piece of work; CI must be green.

## Stack

- Python 3.12, package `psb` under `src/psb/` (scrapers, metrics, features, models, rules, picklog).
- Lint/format: `ruff check . && ruff format --check .` · Tests: `pytest -q`.
- AWS ap-southeast-1. Lambda (container images in ECR) for scrapers and scoring; Fargate for
  training and backtests; EventBridge Scheduler; S3 + Parquet + DuckDB, no RDS; SSM for secrets;
  Telegram bot for picks (D40).
- Terraform: `infra/bootstrap` (run locally once by CJ, local state, never in CI),
  `infra/modules/*`, `infra/envs/prod` (applied only by GitHub Actions on merge to main).
  Never run `terraform apply` on `infra/envs/prod` locally.

## Data layout (S3 bucket psb-data-<account id>)

- `raw/<source>/<yyyy-mm-dd>/...` exactly as scraped, never modified.
- `processed/<table>/...` Parquet: metrics, features, odds_snapshots, predictions, picks.

## Current status

- Step 1 (bootstrap): done. `infra/bootstrap` applied 20 Oct 2026; repo variables set;
  environment `prod` restricted to `main`; terraform workflow plans on PRs, applies on merge.
  - The GitHub OIDC provider is shared with CJ's platform10 project, which owns it; bootstrap
    only looks it up. Destroying platform10's bootstrap breaks CI here until it is recreated.
  - Bootstrap state is local (git-ignored); backup at
    `s3://psb-tfstate-<account id>/bootstrap-backup/terraform.tfstate`. Re-copy after any
    bootstrap apply.
  - Repo is public (D41); odds data and model weights never go in the repo.
- Next, step 2 (data): results, HT scores, goal minutes, xG, lineups and injuries per the
  Source map in `docs/design.md`.
  - Singapore Pools odds scraper is on hold: their website T&Cs (clause 2.2.3) prohibit
    scraping. Do not build it until CJ records a decision (likely D42) on how odds are sourced.
