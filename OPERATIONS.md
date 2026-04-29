# TraceFind — Deployment & Operations Guide

This document covers everything that comes **after** the code was written: local development, deployment to AWS, smoke testing, day-2 operations, troubleshooting, and the roadmap for hardening beyond MVP.

| Field | Value |
|---|---|
| Related | [README.md](README.md), [PRD.md](PRD.md), [TDD.md](TDD.md), [ARCHITECTURE.md](ARCHITECTURE.md) |

---

## Table of contents

1. [Prerequisites](#1-prerequisites)
2. [Local development](#2-local-development)
3. [AWS account preparation](#3-aws-account-preparation)
4. [First-time deployment](#4-first-time-deployment)
5. [Per-environment configuration](#5-per-environment-configuration)
6. [Frontend deployment](#6-frontend-deployment)
7. [Post-deploy smoke test](#7-post-deploy-smoke-test)
8. [CI/CD setup](#8-cicd-setup)
9. [Day-2 operations](#9-day-2-operations)
10. [Monitoring & alerting](#10-monitoring--alerting)
11. [Troubleshooting runbook](#11-troubleshooting-runbook)
12. [Cost guardrails](#12-cost-guardrails)
13. [Security checklist](#13-security-checklist)
14. [Disaster recovery](#14-disaster-recovery)
15. [Roadmap & known follow-ups](#15-roadmap--known-follow-ups)

---

## 1. Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12+ | Backend + CDK |
| Node.js | 20+ | Frontend + CDK CLI |
| AWS CLI | v2 | Auth + diagnostics |
| AWS CDK | 2.140+ | IaC |
| Git | any | Version control |
| Playwright (optional) | 1.46+ | E2E tests; install via `npx playwright install` |

```bash
node -v && python --version && aws --version && cdk --version
```

---

## 2. Local development

### 2.1 Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate         # Windows Git-Bash
pip install -e ".[test]"
pytest                                # 21 tests, ~5s
```

Run a single test file:

```bash
pytest tests/integration/test_claim_concurrency.py -v
```

Coverage:

```bash
pytest --cov=src --cov-report=html
# open htmlcov/index.html
```

### 2.2 Frontend

```bash
cd frontend
cp .env.example .env.local            # fill in values from CDK outputs
npm install
npm run dev                           # http://localhost:3000
npm run test                          # vitest unit tests
npm run typecheck
```

Without a deployed backend, API calls will return network errors but the static
pages still render and unit tests still pass.

### 2.3 CDK synth (no AWS credentials needed)

```bash
cd infra
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements.txt
cdk synth --quiet                     # validates the stack
```

---

## 3. AWS account preparation

Do these **once per AWS account / region** before the first deploy.

### 3.1 Bootstrap CDK

```bash
cdk bootstrap aws://<ACCOUNT_ID>/us-east-1
```

### 3.2 Request Bedrock model access

In the AWS console → Bedrock → Model access → request access to:

- `amazon.titan-embed-image-v1`
- `amazon.titan-embed-text-v2:0`

Approval is usually instant for Titan. Without this, `create_item` returns `502 UPSTREAM_ERROR`.

### 3.3 Verify SES

For non-prod, put SES into the sandbox state and verify both the `SES_FROM_EMAIL`
sender address **and** every recipient you want to send to. For prod, request
SES production access (24–48 h SLA).

```bash
aws ses verify-email-identity --email-address no-reply@your-domain.example
```

### 3.4 (Optional) Provision an hCaptcha site

If you want captcha enforcement on sign-up:

1. Sign up at https://www.hcaptcha.com/.
2. Create a site, copy the **secret key**.
3. Set `HCAPTCHA_SECRET` on the `tracefind-pre-signup` Lambda environment after deploy.
4. Make the frontend pass the token via `clientMetadata.captchaToken` on sign-up (TODO — see §15).

If `HCAPTCHA_SECRET` is unset, the pre-signup trigger logs a warning and lets sign-ups through (dev-friendly).

---

## 4. First-time deployment

```bash
cd infra
source .venv/Scripts/activate
export CDK_DEFAULT_ACCOUNT=<your-account-id>
export CDK_DEFAULT_REGION=us-east-1
export ALARM_EMAIL=ops@your-domain.example   # optional, for SNS alarms

cdk deploy --all --context env=dev
```

The deploy provisions, in order:

1. **`TraceFind-Auth-dev`** — Cognito user pool, app client, admin group, pre-signup Lambda.
2. **`TraceFind-Data-dev`** — 5 DynamoDB tables (Items, Matches, Claims, Notifications, AuditLog) with GSIs and streams.
3. **`TraceFind-Api-dev`** — HTTP API Gateway, JWT authorizer, 14 Lambdas, alarms, dashboard.

### 4.1 Capture outputs

After deploy, the CLI prints values you'll need for the frontend `.env.local`:

```bash
aws cloudformation describe-stacks --stack-name TraceFind-Auth-dev \
  --query "Stacks[0].Outputs"
aws cloudformation describe-stacks --stack-name TraceFind-Api-dev \
  --query "Stacks[0].Outputs"
```

Map them:

| CloudFormation export | Frontend env var |
|---|---|
| User pool id | `NEXT_PUBLIC_USER_POOL_ID` |
| User pool client id | `NEXT_PUBLIC_USER_POOL_CLIENT_ID` |
| API endpoint | `NEXT_PUBLIC_API_URL` |

### 4.2 Create your first admin user

```bash
USER_POOL_ID=us-east-1_xxxxxxxxx
EMAIL=admin@your-domain.example

aws cognito-idp admin-create-user \
  --user-pool-id $USER_POOL_ID \
  --username $EMAIL \
  --user-attributes Name=email,Value=$EMAIL Name=email_verified,Value=true \
  --message-action SUPPRESS

aws cognito-idp admin-set-user-password \
  --user-pool-id $USER_POOL_ID \
  --username $EMAIL \
  --password 'Tmp-Pass-1234!' \
  --permanent

aws cognito-idp admin-add-user-to-group \
  --user-pool-id $USER_POOL_ID \
  --username $EMAIL \
  --group-name admin
```

---

## 5. Per-environment configuration

Three environments are supported via `--context env=<name>`:

| Env | Stack name suffix | Provisioned concurrency | Recommended account |
|---|---|---|---|
| `dev` | `-dev` | none | shared dev account |
| `staging` | `-staging` | none | shared staging account |
| `prod` | `-prod` | 1 instance on `create_item` | dedicated prod account |

```bash
cdk deploy --all --context env=staging
cdk deploy --all --context env=prod
```

Per-environment overrides go in `infra/config/<env>.yaml` (create as needed) or
the SSM Parameter Store path `/tracefind/<env>/...`.

Configurable via Lambda env vars (set them in [api_stack.py](infra/cdk/stacks/api_stack.py) `common_env`):

| Variable | Default | Notes |
|---|---|---|
| `MATCH_THRESHOLD` | `0.75` | Cosine threshold |
| `EMBEDDING_MODEL_VERSION` | `titan-mm-v1+titan-text-v2` | Bump when changing models |
| `ITEM_TTL_SECONDS` | `7776000` (90 d) | Report retention |
| `SES_FROM_EMAIL` | `no-reply@tracefind.local` | Override per env |
| `LOG_LEVEL` | `INFO` | `DEBUG` for diagnostics |

---

## 6. Frontend deployment

The frontend is **not** deployed by the CDK stacks. Pick one of:

### 6.1 AWS Amplify Hosting (recommended)

```bash
cd frontend
amplify hosting create
amplify publish
```

Or via the Amplify console: connect the repo, set `frontend/` as the app root, set the env vars from §4.1, and let it auto-build on push.

### 6.2 Vercel

```bash
npx vercel
# set NEXT_PUBLIC_* env vars in the Vercel dashboard
```

### 6.3 Self-host (CloudFront + S3)

```bash
npm run build
# deploy `out/` to S3 + CloudFront — see Next.js static export docs
```

### 6.4 Configure CORS

Once the frontend is on a real origin, replace the `*` in
[api_stack.py](infra/cdk/stacks/api_stack.py) `cors_preflight.allow_origins`
with your actual domain and redeploy.

---

## 7. Post-deploy smoke test

### 7.1 Unauthenticated

```bash
curl -i $API_URL/items
# Expect: 401 with {"error":{"code":"FORBIDDEN","message":"missing user identity"}}
```

### 7.2 Authenticated end-to-end

```bash
# 1. Get an id token (for testing only — the UI uses Hosted UI normally)
TOKEN=$(aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id $CLIENT_ID \
  --auth-parameters USERNAME=$EMAIL,PASSWORD='Tmp-Pass-1234!' \
  --query "AuthenticationResult.IdToken" --output text)

# 2. Create a lost report
curl -X POST "$API_URL/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"lost","description":"black backpack with red zipper","category":"bag","image":"data:image/png;base64,iVBORw0KGgo...truncated..."}'

# 3. List your items
curl "$API_URL/items" -H "Authorization: Bearer $TOKEN"

# 4. Wait ~5s for async matching, then list matches
curl "$API_URL/items/<item_id>/matches" -H "Authorization: Bearer $TOKEN"
```

### 7.3 Run E2E suite against deployed env

```bash
cd frontend
E2E_BASE_URL=https://your-app.example npm run e2e
# To run authenticated tests:
E2E_USERNAME=admin@example.com E2E_PASSWORD='Tmp-Pass-1234!' npm run e2e
```

---

## 8. CI/CD setup

The repo ships two GitHub Actions workflows:

- [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — runs on every PR (backend pytest + coverage, frontend typecheck/test/build, `cdk synth`).
- [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml) — manual workflow_dispatch, OIDC role assumption, `cdk diff` then `cdk deploy`.

### 8.1 Configure repo secrets

In **Settings → Secrets and variables → Actions** add:

| Secret | Used by |
|---|---|
| `AWS_DEPLOY_ROLE_ARN` | `deploy.yml` — IAM role with trust policy for GitHub OIDC |
| `AWS_REGION` | both |
| `ALARM_EMAIL` | `deploy.yml` (optional) |

### 8.2 Create the OIDC deploy role

```yaml
# Trust policy
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::<ACCOUNT>:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:<org>/<repo>:environment:*"
      }
    }
  }]
}
```

Permissions: attach `AdministratorAccess` for simplicity in dev; in prod scope it down to the CDK-managed CloudFormation stacks and the bootstrap roles.

### 8.3 Configure GitHub Environments

Create three environments — `dev`, `staging`, `prod` — and require manual approval for `prod`.

---

## 9. Day-2 operations

### 9.1 Roll out a new embedding model

1. Update `EMBEDDING_MODEL_VERSION` in CDK (or via SSM).
2. Deploy the new value.
3. New reports get the new version automatically.
4. Optional: re-embed historical reports by calling
   `POST /admin/items/{id}/reembed` (admin-only) once the user re-uploads
   the image. Bulk backfill is a manual operator task — there is **no** automated
   migration because images are not stored.

### 9.2 Tune the match threshold

```bash
aws ssm put-parameter \
  --name "/tracefind/dev/match-threshold" \
  --value "0.78" \
  --type String --overwrite
```

Then bump the Lambda env var via redeploy, or read SSM at runtime (TODO — see §15).

### 9.3 Promote a user to admin

```bash
aws cognito-idp admin-add-user-to-group \
  --user-pool-id $USER_POOL_ID \
  --username $EMAIL \
  --group-name admin
```

The user must sign out and back in to refresh their JWT before admin routes work.

### 9.4 Rotate a leaked secret

- **Cognito app client secret**: not used (public client).
- **Bedrock**: no static credentials; uses Lambda execution role.
- **hCaptcha secret**: rotate at hCaptcha → update env var on `tracefind-pre-signup` Lambda → redeploy.

---

## 10. Monitoring & alerting

The CDK creates the following automatically:

| Alarm | Threshold | Notifies |
|---|---|---|
| API 5xx | > 5 in 5 min | SNS topic |
| API p95 latency | > 2 s for 10 min | SNS topic |
| Lambda errors per handler | > 3 in 5 min (each of: create_item, match_items, claim_item, notify_users) | SNS topic |
| DynamoDB throttles | ≥ 1 throttled request | SNS topic |

Subscribe ops to the SNS topic by setting `ALARM_EMAIL` at deploy time.

CloudWatch dashboard `tracefind-<env>` shows API latency, 5xx, Lambda invocations and errors at a glance.

### 10.1 Useful Logs Insights queries

**Slowest create_item requests:**

```
fields @timestamp, @duration
| filter @logStream like /tracefind-createitem-/
| sort @duration desc
| limit 20
```

**Match scores over time:**

```
fields @timestamp, item_id, matches
| filter msg = "matching_complete"
| stats avg(matches), max(matches) by bin(5m)
```

**Claim conflicts:**

```
fields @timestamp, error
| filter error_type = "ConflictError"
| stats count() by bin(1h)
```

---

## 11. Troubleshooting runbook

| Symptom | Likely cause | Fix |
|---|---|---|
| `POST /items` returns `502 UPSTREAM_ERROR` | Bedrock access not approved or model id wrong | Console → Bedrock → Model access; verify region matches Lambda |
| `POST /items` returns `400 INVALID_IMAGE` | Frontend sent payload over 5 MB | Verify `fileToResizedDataUri` is being called |
| `POST /items/{id}/claim` returns `409` | Another claim already won the race | Expected — refresh and pick a different match |
| New reports never get matches | Wrong `EMBEDDING_MODEL_VERSION` between writers and matcher | Check Lambda env vars across all functions |
| `notify_users` Lambda errors with `cognito-idp:AdminGetUser` denied | IAM policy not attached after fresh deploy | Re-run `cdk deploy`; check the role inline policy |
| Sign-up fails with "captcha verification failed" | `HCAPTCHA_SECRET` set but frontend isn't sending token | Either remove the secret or wire `clientMetadata.captchaToken` in the Authenticator |
| DynamoDB throttle alarm triggers | Burst write traffic | DDB is on-demand — alarm is informational. Check for runaway loops in matching |
| Frontend gets CORS error | API still has `allow_origins=["*"]` and browser blocks credentials | Replace with explicit origin and redeploy |

### 11.1 Cold start observed in dev

Expected. Provisioned concurrency is **only** enabled for `prod`. To enable in
another environment, edit the `if env_name == "prod":` block in
[api_stack.py](infra/cdk/stacks/api_stack.py).

### 11.2 Tail Lambda logs live

```bash
aws logs tail /aws/lambda/tracefind-createitem-dev --follow
aws logs tail /aws/lambda/tracefind-matchitems-dev --follow
```

---

## 12. Cost guardrails

Pilot scale (≈ 5,000 reports/month) cost estimate, us-east-1:

| Service | Estimate | Notes |
|---|---|---|
| Lambda | < $1 | Free tier covers most invocations |
| DynamoDB on-demand | $1–3 | Reads dominate; small TTL'd dataset |
| API Gateway HTTP API | < $1 | First million requests $1 |
| Bedrock Titan | ~$5 | $0.001 per report (image + text) |
| SES | ~$0.10 | $0.10 per 1k emails |
| CloudWatch logs/metrics | $1–2 | 30-day retention |
| **Total** | **~$10/month** | excluding Cognito (free under 50k MAU) |

### 12.1 Cost alerts

```bash
aws budgets create-budget --account-id <ACCOUNT> --budget '{
  "BudgetName": "TraceFind-Pilot",
  "BudgetLimit": {"Amount": "25", "Unit": "USD"},
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}'
```

### 12.2 Cost anti-patterns to watch

- **Provisioned concurrency in non-prod** — costs ~$5/month per Lambda even if idle.
- **DynamoDB Streams batch size** — default 10; do not set to 1 unless debugging.
- **Bedrock retries** — every retry doubles spend; ensure `botocore` retry mode is `standard`, not `adaptive` with high attempts.

---

## 13. Security checklist

Before going live, verify each item:

- [ ] All API Gateway routes require JWT (default authorizer is set).
- [ ] CORS origin is the explicit frontend URL, not `*`.
- [ ] DynamoDB encryption at rest is on (default with `BillingMode.PAY_PER_REQUEST`).
- [ ] Lambda IAM roles use the principle of least privilege (CDK grants are table-scoped).
- [ ] No secrets in env vars committed to git; use SSM Parameter Store or Secrets Manager.
- [ ] CloudTrail is enabled in the account.
- [ ] AWS GuardDuty is enabled.
- [ ] Cognito password policy is at least 10 chars with mixed case and digits (already configured).
- [ ] SES production access requested with a clear use-case description.
- [ ] hCaptcha enabled on production sign-up.
- [ ] Frontend domain is HTTPS-only with HSTS.
- [ ] `RemovalPolicy` is `RETAIN` for items, matches, claims, audit (already set).
- [ ] Point-in-time recovery is enabled on items, matches, claims, audit (already set).

### 13.1 Pen-test scope before launch

- Auth bypass: try calling each route without a token and with an admin-group claim forged.
- IDOR: call `GET /items/{id}` with another user's id.
- File upload: send a payload that's `image/jpeg` MIME but contains an executable.
- Replay: re-submit the same `POST /items/{id}/claim` after success.
- Rate limit: exceed 30/hour `POST /items` from one user.

---

## 14. Disaster recovery

| Scenario | RPO | RTO | Procedure |
|---|---|---|---|
| Single Lambda failure | 0 | seconds | Auto-recovers; alarm fires if persistent |
| DynamoDB table corruption | up to 35 days | < 30 min | PITR restore: `aws dynamodb restore-table-to-point-in-time` |
| Region outage | up to 24 h | hours | Re-deploy CDK in a peer region; restore tables from PITR snapshots |
| Account compromise | 0 | hours | Rotate IAM credentials; check CloudTrail; re-deploy from clean account |

PITR is enabled on Items, Matches, Claims, and AuditLog. Notifications has TTL
and `RemovalPolicy.DESTROY` — it is treated as ephemeral.

### 14.1 Test the restore path

Quarterly:

```bash
aws dynamodb restore-table-to-point-in-time \
  --source-table-name tracefind-items \
  --target-table-name tracefind-items-restored-$(date +%Y%m%d) \
  --use-latest-restorable-time
```

---

## 15. Roadmap & known follow-ups

These are tracked for after MVP. Each links to where it would slot in.

### 15.1 Functional

| Item | Owner | Notes |
|---|---|---|
| Wire `clientMetadata.captchaToken` from frontend Authenticator | TBD | Override Amplify Authenticator's signUp form to inject the token |
| Web push notifications | TBD | Add a `web_push_subscription` aggregate to `notification` context; service worker on frontend |
| Geo-location matching radius | TBD | New value object `Location`; filter candidates by haversine before similarity |
| Multi-language descriptions | TBD | Detect language; index per-language; consider multilingual embedding model |
| Mobile app (iOS / Android) | TBD | React Native sharing the existing API contracts |
| Face-recognition opt-in | TBD | New context `face_recognition` — must be feature-flagged and consent-gated |

### 15.2 Operational

| Item | Notes |
|---|---|
| Hot-reload `MATCH_THRESHOLD` from SSM at runtime | Currently env var; would let admins tune without redeploy |
| Bulk re-embed Lambda triggered by EventBridge | When upgrading the embedding model en masse |
| OpenSearch Serverless k-NN migration | Trigger when `match_items.candidate_count > 5000` consistently |
| Per-tenant data isolation | If we sell to multiple campuses, partition by `tenant_id` |
| Per-user usage plans (real Cognito-mapped throttles) | API Gateway usage plans require API keys; HTTP API now uses route throttling |

### 15.3 Quality

| Item | Notes |
|---|---|
| Coverage gates in CI | Fail under 80% on `src/` |
| Mutation testing | `mutmut` on the matching service |
| Load test | k6 at 50 RPS sustained on `POST /items` |
| Chaos | Lambda fault injection on `notify_users` to verify retries |
| Visual regression | Playwright + percy on the dashboard pages |

### 15.4 Documentation

| Item | Notes |
|---|---|
| Architecture decision records (ADRs) | One per resolved open question in PRD §16 / TDD §15 |
| Threat model | STRIDE walk-through of the 5 contexts |
| Customer-facing FAQ / help docs | Pre-launch task for marketing |

---

## Quick reference

| Command | Purpose |
|---|---|
| `cd backend && pytest` | Run all 21 backend tests |
| `cd frontend && npm run dev` | Start the UI on port 3000 |
| `cd frontend && npm run e2e` | Run Playwright smoke tests |
| `cd infra && cdk synth` | Validate the CDK stacks (no AWS calls) |
| `cd infra && cdk deploy --all --context env=dev` | Deploy everything to dev |
| `cd infra && cdk diff --context env=prod` | Preview prod changes before deploy |
| `cd infra && cdk destroy --all --context env=dev` | Tear down dev (data tables RETAIN — must delete manually) |

If you delete a data table by mistake, restore from PITR within 35 days.

---

**Owner contact:** kparthiban@infiniqon.com
**Issues:** open a ticket in the repo with the `ops` label.
