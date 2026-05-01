# Technical Design Document (TDD)

## Smart Lost & Found System (TraceFind)

| Field | Value |
|---|---|
| Document | Technical Design Document |
| Product | TraceFind — Smart Lost & Found System |
| Version | 1.0 |
| Date | 2026-04-29 |
| Owner | kparthiban@infiniqon.com |
| Related | [PRD.md](PRD.md), [ARCHITECTURE.md](ARCHITECTURE.md) |
| Status | Draft |

---

## 1. Architecture Overview

### 1.1 High-Level Diagram

```
┌──────────────────┐
│  Next.js Client  │  ← Tailwind UI, Cognito SDK
└────────┬─────────┘
         │ HTTPS + JWT
         ▼
┌──────────────────┐
│   API Gateway    │  ← REST/HTTP API, JWT Authorizer
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│              AWS Lambda (Python)             │
│  create_item │ get_items │ match_items       │
│              │ notify_users                  │
└──┬─────────────────┬───────────────┬─────────┘
   │                 │               │
   ▼                 ▼               ▼
┌────────────┐  ┌──────────┐   ┌────────────┐
│ DynamoDB   │  │ AI / ML  │   │   Gmail    │
│ Items,     │  │ Embedding│   │   SMTP     │
│ Matches    │  │ Service  │   │   (Gmail)  │
└────────────┘  └──────────┘   └────────────┘
```

### 1.2 Architectural Style
- **Serverless, event-driven** for scalability and cost-efficiency.
- **Stateless Lambdas** — all state persisted in DynamoDB.
- **Single-region MVP** with multi-AZ DynamoDB.
- **No persistent image storage** — images are processed in-memory and discarded.
- **Domain-Driven Design** — code is organized by bounded context (`identity_access`, `reporting`, `matching`, `notification`, `claims`) per [ARCHITECTURE.md](ARCHITECTURE.md). Lambdas are thin interface adapters that call into application use cases.

---

## 2. System Components

### 2.1 Frontend (Next.js)
- **Framework:** Next.js 14+ (App Router), React 18.
- **Styling:** Tailwind CSS.
- **Auth:** AWS Amplify Auth or `amazon-cognito-identity-js` for Cognito.
- **Responsibilities:**
  - User registration / login
  - Image capture & client-side resizing (≤ 1024 px, JPEG, ≤ 1 MB)
  - Form validation
  - API calls with JWT in `Authorization: Bearer <token>`
  - Match listing & claim UI

### 2.2 API Gateway
- **Type:** HTTP API (lower latency, cheaper than REST API).
- **Authorizer:** JWT Authorizer pointed at Cognito User Pool.
- **CORS:** Allow Next.js origin only.
- **Throttling:** Default 1000 RPS burst, 500 RPS steady; per-user usage plans for write endpoints.

### 2.3 Lambda Functions

Each Lambda maps to a bounded context as defined in [ARCHITECTURE.md](ARCHITECTURE.md).

| Function | Context | Trigger | Memory | Timeout | Purpose |
|---|---|---|---|---|---|
| `create_item` | reporting | API Gateway POST `/items` | 1024 MB | 15 s | Validate, generate embedding, persist |
| `get_items` | reporting | API Gateway GET `/items`, `/items/{id}` | 256 MB | 5 s | List / read user reports |
| `match_items` | matching | DynamoDB Stream on `Items` (primary); `POST /match` (replay) | 1024 MB | 15 s | Compute similarity, persist matches |
| `get_matches` | matching | API Gateway GET `/items/{id}/matches` | 256 MB | 5 s | Return ranked matches for an item |
| `claim_item` | claims | API Gateway POST `/items/{id}/claim` | 256 MB | 5 s | Confirm claim with conditional writes |
| `notify_users` | notification | DynamoDB Stream on `Matches` | 256 MB | 10 s | Persist `Notifications` row + send Gmail SMTP email |
| `get_notifications` | notification | API Gateway GET `/notifications` | 256 MB | 5 s | Paged in-app feed |
| `mark_notification_read` | notification | API Gateway POST `/notifications/{id}/read` | 256 MB | 5 s | Update read state |
| `admin_moderate` | reporting | API Gateway `/admin/reports`, `/admin/items/{id}/...` | 256 MB | 5 s | Admin moderation; writes `AdminAuditLog` |
| `admin_audit_query` | reporting | API Gateway GET `/admin/audit` | 256 MB | 5 s | Read audit log |

**Decision (resolves PRD open question #6):** matching is **asynchronous via DynamoDB Streams**, not synchronous in `create_item`. `POST /match` exists only for admin replay and is gated by Cognito group membership. This keeps `create_item` p95 below the 2 s target even when the embedding service is slow.

**Cold-start strategy:** Provisioned concurrency (1 instance) on `create_item` in `prod` only. Other Lambdas use on-demand. Frontend shows a "Searching for matches…" state while the async pipeline completes.

#### 2.3.1 `create_item` — Detailed Flow
1. Validate JWT claims, extract `user_id`.
2. Validate payload (size, MIME, required fields).
3. Decode base64 images → in-memory bytes (up to 3).
4. Call embedding service → `image_embedding` (pooled vector from all photos).
5. Call text embedding for description → `text_embedding`.
6. Combine via weighted concat or stored separately.
7. `PutItem` into `Items` with TTL, location, and incident timestamp.
8. Emit event for `match_items` (via DynamoDB Stream or direct invoke).
9. Return `201 Created` with item id.

#### 2.3.2 `match_items` — Detailed Flow
1. Read new item.
2. Query candidate items of opposite `type` and `status = active` (filter by `category` if available).
3. For each candidate compute cosine similarity on combined vector.
4. Filter where score ≥ threshold (default 0.75).
5. Bulk write to `Matches` table.
6. Return top-N matches.

### 2.4 Database (DynamoDB)

#### 2.4.1 Table: `Items`
| Attribute | Type | Notes |
|---|---|---|
| `id` | String (PK) | UUID v4 |
| `user_id` | String | Cognito sub |
| `type` | String | `lost` / `found` |
| `description` | String | Free text |
| `category` | String | Optional (`bag`, `wallet`, …) |
| `embedding` | List<Number> | Concatenated vector |
| `embedding_model_version` | String | e.g. `titan-mm-v1+titan-text-v2` — set at write time so future model swaps are detectable |
| `status` | String | `active` / `matched` / `claimed` |
| `location` | String | Optional (e.g. "Library 2nd Floor") |
| `incident_at`| String | Optional (ISO 8601) |
| `photo_count`| Number | Integer (1-3) |
| `created_at` | String | ISO 8601 |
| `ttl` | Number | Epoch seconds for retention (90 days) |
| `gsi1_pk` | String | `type#<bucket>` where bucket = `created_at` truncated to day |

**GSIs:**
- `GSI1` — PK: `gsi1_pk` (`type#YYYY-MM-DD`), SK: `created_at` — matching scans bounded by recent days
- `GSI2` — PK: `user_id`, SK: `created_at` — user history

#### 2.4.2 Table: `Matches`
| Attribute | Type | Notes |
|---|---|---|
| `id` | String (PK) | UUID |
| `item1_id` | String | Lost item id |
| `item2_id` | String | Found item id |
| `score` | Number | Cosine similarity 0–1 |
| `status` | String | `pending` / `confirmed` / `rejected` |
| `created_at` | String | ISO 8601 |

**GSIs:**
- `GSI1` — PK: `item1_id`
- `GSI2` — PK: `item2_id`

#### 2.4.3 Table: `Claims`
| Attribute | Type | Notes |
|---|---|---|
| `id` | String (PK) | UUID |
| `match_id` | String | FK to `Matches.id` |
| `claimant_user_id` | String | Cognito sub |
| `lost_item_id` | String | |
| `found_item_id` | String | |
| `status` | String | `pending` / `confirmed` / `rejected` |
| `created_at` | String | ISO 8601 |
| `resolved_at` | String | ISO 8601, set on terminal status |

**Concurrency:** `claim_item` uses a `TransactWriteItems` call:
1. Conditional update on `Items[lost_item_id]`: `status = active → claimed` (`ConditionExpression: #status = :active`).
2. Same conditional update on `Items[found_item_id]`.
3. Insert `Claims` row.
A simultaneous second claim fails the condition and the handler returns `409 CONFLICT`.

**GSIs:**
- `GSI1` — PK: `claimant_user_id`, SK: `created_at`
- `GSI2` — PK: `match_id`

#### 2.4.4 Table: `Notifications`
| Attribute | Type | Notes |
|---|---|---|
| `id` | String (PK) | UUID |
| `user_id` | String | Recipient Cognito sub |
| `type` | String | `match_found` / `claim_confirmed` / `claim_rejected` |
| `payload` | Map | Match id, item id, score, etc. |
| `read` | Bool | Default `false` |
| `created_at` | String | ISO 8601 |
| `ttl` | Number | Epoch seconds (90 days) |

**GSIs:**
- `GSI1` — PK: `user_id`, SK: `created_at` — paged feed query

#### 2.4.5 Table: `AdminAuditLog`
| Attribute | Type | Notes |
|---|---|---|
| `id` | String (PK) | UUID |
| `actor_user_id` | String | Admin Cognito sub |
| `action` | String | e.g. `override_match`, `delete_item` |
| `target_id` | String | Affected resource id |
| `before` | Map | Snapshot before mutation |
| `after` | Map | Snapshot after mutation |
| `created_at` | String | ISO 8601 |

**GSIs:**
- `GSI1` — PK: `actor_user_id`, SK: `created_at`
- `GSI2` — PK: `target_id`, SK: `created_at`

> **Note on embedding storage:** DynamoDB is not a vector database. For MVP, embeddings (≤ 1 KB each) are stored inline and compared in-process within `match_items`. Candidate set is bounded by `gsi1_pk` (recent N days of opposite-type items). For >10K active items, migrate to OpenSearch Serverless k-NN or pgvector — gated by metric `match_items.candidate_count > 5000`.

---

## 3. API Design

All endpoints require `Authorization: Bearer <JWT>` unless noted.

### 3.1 `POST /items`
Create a new lost or found report.

**Request**
```json
{
  "type": "lost",
  "description": "black leather backpack with red zipper",
  "category": "bag",
  "location": "Library 2nd Floor",
  "incident_at": "2026-05-01T14:00:00Z",
  "image_data_uris": ["data:image/jpeg;base64,...."]
}
```

**Response 201**
```json
{
  "id": "8f1c…",
  "status": "active",
  "created_at": "2026-04-29T12:34:56Z"
}
```

### 3.2 `GET /items`
List the authenticated user's reports.

**Query:** `?type=lost&status=active&limit=20&cursor=…`

### 3.3 `POST /match`
Trigger matching for a specific item (idempotent).

**Request**
```json
{ "item_id": "8f1c…" }
```

### 3.4 `GET /items/{id}/matches`
Return matches for a specific item owned by the authenticated user.

**Query:** `?min_score=0.75&limit=20&cursor=…`

> Endpoint is `GET /items/{id}/matches` (not `GET /matches`) — aligns with PRD §9.4.

### 3.5 `POST /items/{id}/claim`
Confirm or reject a match and initiate claim.

**Request**
```json
{ "match_id": "…", "decision": "confirm" }
```

**Responses**
- `200 OK` — claim resolved.
- `409 CONFLICT` — another claim already won (conditional write failed).

### 3.6 Notification Endpoints
- `GET /notifications?cursor=…&limit=20` — paged in-app feed for current user.
- `POST /notifications/{id}/read` — mark a notification as read.

### 3.7 Admin Endpoints
- `GET /admin/reports`
- `POST /admin/items/{id}/override-match`
- `DELETE /admin/items/{id}`
- `GET /admin/audit?actor=…&from=…&to=…` — query the audit log.

All admin endpoints require Cognito group `admin` AND a Lambda-level group assertion. Each mutating call writes one `AdminAuditLog` row before returning.

### 3.8 Error Envelope
```json
{ "error": { "code": "INVALID_INPUT", "message": "image too large" } }
```

---

## 4. Authentication & Authorization

### 4.1 Flow
1. User registers / logs in via Cognito Hosted UI or SDK.
2. Cognito issues `id_token` (JWT) and `access_token`.
3. Frontend attaches `Authorization: Bearer <id_token>` to every API call.
4. API Gateway JWT Authorizer validates signature, expiry, audience, issuer.
5. Lambda extracts `sub` (user id) and `cognito:groups` (roles) from claims.

### 4.2 Authorization Rules
- A user can only read / mutate their own items unless they belong to the `admin` group.
- Admin-only routes enforce group check at Lambda level too (defense in depth).
- Cognito **groups**: `user` (default), `admin`. Group membership is in JWT claim `cognito:groups`.
- Sign-up flow includes a captcha challenge (hCaptcha or Cognito's pre-sign-up Lambda trigger).
- Per-user write throttling enforced by API Gateway usage plans:
  - `POST /items`: 30 req/hour per user
  - `POST /match`: 60 req/hour per user (admin only in practice)
  - Read endpoints: default account throttle.

---

## 5. AI Matching Design

### 5.1 Pipeline
1. **Decode image** → bytes.
2. **Preprocess**: resize to 224×224, normalize.
3. **Image embedding**: CLIP-style model (Bedrock Titan Multimodal or self-hosted CLIP) → 512-dim vector.
4. **Text embedding**: Bedrock Titan Text → 384-dim vector.
5. **Combine**: L2-normalize each, concatenate (weighted 0.6 image / 0.4 text) → final vector.
6. **Persist** vector in `Items.embedding`.
7. **Compare** against active opposite-type items using cosine similarity.

### 5.2 Cosine Similarity
```
sim(A, B) = (A · B) / (||A|| * ||B||)
```
- Range: −1 to 1; for normalized vectors: 0 to 1.
- **Threshold:** default `0.75` (configurable per environment).
- **Top-K:** return top 10 candidates.

### 5.3 Threshold Tuning
- Tracked via metrics: precision, recall on a labeled holdout set.
- Threshold stored in SSM Parameter Store for hot-reload.

### 5.4 Model Versioning
- Every `Items` row records `embedding_model_version` at write time.
- `match_items` only compares vectors of equal `embedding_model_version`. Candidates with a different version are skipped.
- Model upgrades are rolled out as a version bump + a one-shot backfill Lambda that re-embeds active items where source descriptions are still available.

### 5.5 Bedrock Cost & Quota
- Estimated per-report cost: ~$0.0008 (Titan Multimodal image) + ~$0.0001 (Titan Text) ≈ $0.001.
- Pilot scale assumption: 5,000 reports/month → ~$5/month embedding spend.
- Bedrock account quota request filed for `bedrock:InvokeModel` 50 RPS (Titan models) before pilot launch.

---

## 6. Data Flow (Happy Path)

```
User → Next.js → POST /items (JWT, base64 image)
                → API Gateway (JWT auth)
                → Lambda create_item
                    → validate + decode
                    → embedding service
                    → DynamoDB Items.PutItem
                    → DynamoDB Stream
                → Lambda match_items
                    → query opposite-type items
                    → cosine similarity
                    → DynamoDB Matches.PutItem(s)
                    → DynamoDB Stream
                → Lambda notify_users
                    → SES email + in-app feed update
```

---

## 7. Error Handling

| Scenario | HTTP | Code |
|---|---|---|
| Missing/invalid fields | 400 | `INVALID_INPUT` |
| Image too large / wrong type | 400 | `INVALID_IMAGE` |
| Missing/expired JWT | 401 | `UNAUTHORIZED` |
| Forbidden (RBAC) | 403 | `FORBIDDEN` |
| Item not found | 404 | `NOT_FOUND` |
| Rate limit exceeded | 429 | `THROTTLED` |
| Embedding service failure | 502 | `UPSTREAM_ERROR` |
| Internal failure | 500 | `INTERNAL_ERROR` |

- Lambdas use a shared error wrapper that converts exceptions into the standard error envelope.
- All errors are logged to CloudWatch with `request_id` correlation.

---

## 8. Scalability

- **Lambda:** auto-scales to account concurrency limit; provisioned concurrency on `create_item` to avoid cold starts.
- **DynamoDB:** on-demand capacity; partition keys chosen to avoid hotspots (UUID-based).
- **API Gateway:** scales horizontally; throttling configured per stage.
- **Embedding service:** Bedrock managed scaling; alternative is a fronting Lambda with cached model in `/tmp`.

---

## 9. Security

- **Transport:** HTTPS only (TLS 1.2+) at API Gateway and CloudFront.
- **AuthN:** Cognito User Pools, JWT validation at gateway.
- **AuthZ:** Cognito groups + per-Lambda role checks.
- **IAM:** least-privilege role per Lambda; only the necessary DynamoDB actions on the necessary tables.
- **Input validation:** JSON schema validation; image size cap (5 MB), MIME whitelist.
- **Rate limiting:** API Gateway usage plans.
- **Secrets:** AWS Secrets Manager / SSM Parameter Store; never in env files.
- **Encryption at rest:** DynamoDB SSE with AWS-owned key (KMS CMK optional).
- **Logging hygiene:** redact PII; never log raw image bytes or full embedding.

---

## 10. Performance Optimization

- Client-side image resizing before upload.
- Lambda memory tuned via Lambda Power Tuning (target 1024 MB for embedding paths).
- DynamoDB GSIs to avoid full scans during matching.
- Connection reuse: instantiate `boto3` clients outside the handler.
- Caching: SSM parameters cached in module scope with TTL.

---

## 11. Testing Strategy

### 11.1 Unit Tests (`pytest`)
- Pure functions: validation, similarity, payload parsing.
- Lambda handlers tested with `moto` for DynamoDB mocking.
- Target ≥ 80% coverage on business logic.

### 11.2 Integration Tests
- API Gateway + Lambda + DynamoDB deployed to a `dev` stack.
- Run via `pytest` with real HTTP calls.

### 11.3 End-to-End Tests
- Playwright tests against the deployed Next.js frontend.
- Scenarios: signup → report lost → report matching found → confirm match → claim.

### 11.4 Test Data
- Synthetic image set with known matches for similarity regression tests.

---

## 12. Deployment

### 12.1 Infrastructure as Code
- **AWS CDK (Python).**
- Stacks:
  - `AuthStack` — Cognito User Pool, App Client.
  - `DataStack` — DynamoDB tables, streams.
  - `ApiStack` — API Gateway, Lambdas, IAM.
  - `FrontendStack` — Amplify Hosting or CloudFront + S3 (frontend static only; not item images).

### 12.2 Environments
- `dev`, `staging`, `prod` — separate AWS accounts or stacks with isolated resources.

### 12.3 CI/CD
- GitHub Actions workflow:
  1. Lint + unit tests.
  2. `cdk synth` and diff.
  3. On merge to `main`: `cdk deploy` to staging.
  4. Manual approval → prod deploy.

### 12.4 Configuration
- Env-specific values in SSM Parameter Store.
- Frontend `.env.local` for Cognito pool id, API URL.

---

## 13. Monitoring & Observability

- **Logs:** CloudWatch Logs per Lambda; structured JSON with `request_id`, `user_id`.
- **Metrics:** CloudWatch custom metrics (match count, average score, embedding latency).
- **Alarms:**
  - 5xx rate > 1% for 5 min → page.
  - p95 latency > 2 s for 10 min → warn.
  - DynamoDB throttling > 0 → warn.
- **Tracing:** AWS X-Ray enabled on API Gateway and Lambda.
- **Dashboards:** CloudWatch dashboard with API, Lambda, DynamoDB, embedding service panels.

---

## 14. Limitations & Trade-offs

- **No persistent image storage:** images cannot be re-processed if the embedding model changes; users would need to re-upload. Mitigated by `embedding_model_version` column + opt-in re-upload prompt on model upgrade.
- **DynamoDB as vector store:** linear scan over candidates limits scale to ~10K active items per type before migration is needed. Migration trigger: `match_items.candidate_count > 5000`.
- **Single-region:** RTO/RPO not optimized for cross-region failover in MVP.
- **Cold starts:** provisioned concurrency on `create_item` in `prod` only — cost-incompatible with free-tier in non-prod.
- **Async matching latency:** users see a "Searching for matches…" state; typical end-to-end latency is 3–5 s from `POST /items` to first match notification.

---

## 15. Resolved Technical Decisions

| # | Question | Decision | Rationale |
|---|---|---|---|
| 1 | Bedrock Titan vs. self-hosted CLIP | **Bedrock Titan Multimodal + Titan Text v2** | Managed scaling, no model-hosting overhead, acceptable cost (~$0.001/report) |
| 2 | DynamoDB Streams vs. EventBridge for `create_item → match_items` | **DynamoDB Streams** | Lower latency, exactly-once per shard, no extra IAM surface |
| 3 | Sync vs. async matching | **Async via DDB Stream** | Keeps `POST /items` p95 < 2 s; user sees progressive UI |
| 4 | Notification channel for MVP | **Gmail SMTP email + in-app feed (DDB)** | Branded, scannable transactional templates |
| 5 | Embedding model versioning | **`embedding_model_version` column on `Items`**, enforced at compare time | Prevents silent corruption when model changes |
| 6 | GSI hot-partition risk on `type` | **Composite key `type#YYYY-MM-DD`** | Spreads load across day-buckets while keeping queries efficient |
| 7 | Claim concurrency | **`TransactWriteItems` with conditional updates** | Prevents double-claim race; loser gets `409` |
