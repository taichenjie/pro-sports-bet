# Pro Sports Bet

Metrics-driven football bet model for J1 League and Serie A, priced against Singapore Pools odds.
Outputs 0–3 picks per day. Design decisions live in the design doc (Claude Docs: "Pro Sports Bet — Design Doc").

## Layout

```text
infra/
  bootstrap/   one-time setup: state bucket, GitHub OIDC roles, budget alert (run locally)
  modules/     reusable Terraform modules
  envs/prod/   the deployed stack (run by GitHub Actions)
src/psb/
  scrapers/  metrics/  features/  models/  rules/  picklog/
backtest/
tests/
.github/workflows/   ci (lint + tests), terraform (plan on PR, apply on main)
```

## One-time setup

You need: a GitHub account, the AWS CLI signed in to your personal account with admin rights,
Terraform 1.10 or newer, and git.

### 1. Create the GitHub repo

On GitHub: **New repository** → name `pro-sports-bet` → **Public** → no README, no .gitignore.
Public because GitHub Free restricts environment branches only on public repos (D41); odds data
and model weights never go in the repo.

```bash
cd pro-sports-bet
git init -b main
git add .
git commit -m "Initial skeleton"
git remote add origin https://github.com/<your-username>/pro-sports-bet.git
git push -u origin main
```

The first push runs the `ci` workflow. The `terraform` workflow will fail until step 3 is done; that is expected.

### 2. Bootstrap AWS (run once, from your machine)

```bash
cd infra/bootstrap
cp terraform.tfvars.example terraform.tfvars   # fill in GitHub username, numeric owner/repo IDs, email
terraform init
terraform apply
```

Bootstrap looks up the account's GitHub OIDC provider (`token.actions.githubusercontent.com`)
rather than creating it; in this account it is owned by the platform10 project. On a fresh account,
create the provider first. The roles trust ID-based subjects (`repo:<owner>@<id>/<repo>@<id>:...`),
which is why the numeric IDs are needed.

Note the three outputs: `state_bucket`, `plan_role_arn`, `apply_role_arn`.

Keep `infra/bootstrap/terraform.tfstate` safe (it is git-ignored). It is the only record of these resources.
Back it up to `s3://psb-tfstate-<account id>/bootstrap-backup/terraform.tfstate` after every apply.

AWS will email you to confirm the budget alert subscription: accept it.

### 3. Connect GitHub to AWS

In the repo on GitHub:

1. **Settings → Secrets and variables → Actions → Variables** → add:
   - `TF_STATE_BUCKET` = `state_bucket` output
   - `AWS_PLAN_ROLE_ARN` = `plan_role_arn` output
   - `AWS_APPLY_ROLE_ARN` = `apply_role_arn` output
2. **Settings → Environments → New environment** → name `prod` →
   **Deployment branches and tags** → **Selected branches and tags** → add `main`.
   Optional: add yourself as a required reviewer, so every apply waits for your approval.

### 4. First deploy

Re-run the failed `terraform` workflow (Actions tab), or push any change under `infra/`.
It creates the data bucket (`psb-data-<account id>`) and the container repository (`psb-jobs`).

From then on: open a pull request → `terraform plan` runs; merge to `main` → `terraform apply` runs.

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
ruff check . && pytest
```

## Cost

Step 1 resources cost a few cents a month. A budget alert emails you at 80% (forecast) and 100%
(actual) of the monthly limit, US$20 by default.
