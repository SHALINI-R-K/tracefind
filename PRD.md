# Product Requirements Document (PRD)

## Smart Lost & Found System (AI-Based)

| Field | Value |
|---|---|
| Product Name | TraceFind — Smart Lost & Found System |
| Document Version | 1.0 |
| Date | 2026-04-29 |
| Owner | kparthiban@infiniqon.com |
| Status | Draft |
| Related | [TDD.md](TDD.md), [ARCHITECTURE.md](ARCHITECTURE.md) |

---

## 1. Executive Summary

TraceFind is a cloud-based, AI-driven Lost & Found platform that automates the process of reporting, matching, and recovering misplaced items. By combining image embeddings with textual descriptions, the system computes similarity scores between lost and found reports and notifies users in real time when a probable match is identified. The product targets campuses, offices, and public facilities where manual lost-and-found processes are slow and yield low recovery rates.

---

## 2. Problem Statement

Traditional lost-and-found workflows rely on manual logs, physical noticeboards, or fragmented communication channels. As a result:

- Items are rarely reunited with owners.
- Administrators spend significant effort moderating reports.
- Users have no visibility into the status of their lost items.
- There is no systematic way to compare descriptions and images at scale.

TraceFind solves this by providing a centralized, AI-assisted matching service with real-time notifications.

---

## 3. Goals & Objectives

### 3.1 Product Goals
- Automate the end-to-end lost & found workflow.
- Use AI (image + text embeddings) to match reports automatically.
- Deliver real-time notifications when a match is found.
- Provide a secure, scalable, serverless backend.

### 3.2 Success Metrics (KPIs)
| Metric | Target |
|---|---|
| Match accuracy (precision @ threshold) | > 80% |
| Average API response time | < 2 seconds |
| System uptime | > 99% |
| Recovery rate (claimed / reported) | Improve baseline by ≥ 30% |
| Manual administrator overrides | < 10% of matches |

---

## 4. Target Users & Personas

| Persona | Description | Primary Need |
|---|---|---|
| Student | Campus user reporting lost backpacks, IDs, electronics | Quick recovery with minimal effort |
| Office Employee | Reports items lost in workplace common areas | Privacy-respecting, fast match |
| Public Facility User | Travelers, visitors at malls/airports | Easy reporting without prior account |
| Admin / Moderator | Lost & Found office staff | Oversight, moderation, analytics |

---

## 5. Scope

### 5.1 In Scope (MVP)
- User registration & authentication via Cognito
- Lost item reporting (description + image)
- Found item reporting (description + image)
- AI-based matching with similarity score
- Match listing & user confirmation
- Notification system (in-app + optional email)
- Admin moderation dashboard
- Basic analytics

### 5.2 Out of Scope (MVP)
- Native mobile applications
- Face recognition
- SMS / push notifications
- Geo-location-based matching
- Long-term image storage (S3)

---

## 6. User Flow

1. User signs up / logs in via Cognito.
2. User submits a lost or found report (description + image).
3. Backend extracts embeddings from the image and text.
4. Matching service compares against existing reports of opposite type.
5. If similarity exceeds threshold, candidate matches are surfaced.
6. Both parties are notified.
7. Users confirm; claim flow is triggered.
8. Admin can override or moderate any step.

---

## 7. Functional Requirements

### 7.1 Authentication & User Management
- FR-1: Users register with email and password via AWS Cognito.
- FR-2: JWT tokens are issued for authenticated API calls.
- FR-3: Roles supported: `user`, `admin`.

### 7.2 Item Reporting
- FR-4: Users can create a report with: `type` (lost/found), `description`, `image` (base64 or external URL), `location`, `timestamp`, `category`.
- FR-5: Images are processed in-memory; no persistent S3 storage.
- FR-6: Reports are stored in DynamoDB with a TTL for retention compliance.

### 7.3 AI Matching
- FR-7: System generates embeddings for each new report (image + text).
- FR-8: A new lost report is compared against active found reports (and vice versa).
- FR-9: A similarity score is computed; matches above the configurable threshold are returned.
- FR-10: Match results are ranked by score.

### 7.4 Notifications
- FR-11: When a match exceeds threshold, both the reporter and counterparty are notified.
- FR-12: Email channel via SES is the sole MVP delivery channel; web push is post-MVP.
- FR-13: In-app notification feed shows match history; backed by a `Notifications` table with read/unread state and a `GET /notifications` paged endpoint.
- FR-13a: Notifications are persisted with a 90-day TTL.

### 7.5 Claim Flow
- FR-14: Reporter can confirm or reject a suggested match.
- FR-15: On confirmation, both items are marked `claimed` and removed from active matching.
- FR-15a: Claim writes are protected by DynamoDB conditional updates so two simultaneous claims cannot both succeed; the loser receives `409 CONFLICT`.
- FR-15b: A `Claims` aggregate persists the full lifecycle (`pending` → `confirmed` / `rejected`) for auditability.

### 7.6 Admin Features
- FR-16: Admin can list, search, and moderate reports.
- FR-17: Admin can override or force a match.
- FR-18: Admin dashboard shows volume, match rate, recovery rate.
- FR-19: All admin mutations write to an immutable `AdminAuditLog` (actor, action, target, timestamp, before/after).
- FR-20: Admin role is enforced by Cognito group membership AND verified per-Lambda (defense in depth).

### 7.7 Anonymous & Public Reporting (Decision)
- FR-21: MVP requires authentication for all reports. Anonymous reporting is **deferred to post-MVP**; the open question is hereby closed.

### 7.8 Captcha & Abuse Protection
- FR-22: Sign-up flow integrates a captcha (hCaptcha or Cognito's native challenge) to mitigate bot abuse.
- FR-23: Per-user rate limit on `POST /items` is 30 requests / hour; `POST /match` is 60 / hour.

---

## 8. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | API p95 latency < 2s; matching pipeline < 5s end-to-end |
| Availability | ≥ 99% monthly uptime |
| Scalability | Serverless auto-scaling via Lambda + DynamoDB on-demand |
| Security | HTTPS only, JWT auth, RBAC, input validation, image size cap |
| Privacy | No long-term image storage; PII encrypted at rest |
| Observability | CloudWatch logs, metrics, alarms |
| Cost | Stay within free tier where feasible during pilot |

---

## 9. Technical Architecture

### 9.1 Frontend
- **Framework:** Next.js (App Router)
- **Styling:** Tailwind CSS
- **Auth:** Cognito-hosted UI / SDK
- **Hosting:** Static export or Amplify Hosting

### 9.2 Backend
- **Runtime:** Python 3.12 on AWS Lambda
- **API Layer:** API Gateway (REST/HTTP API)
- **IaC:** AWS CDK (TypeScript or Python)
- **Database:** DynamoDB (single-table design)
- **Auth:** AWS Cognito (User Pools)
- **AI:** Embedding model invoked via Bedrock or external inference endpoint

### 9.3 Data Model (DynamoDB — illustrative)

| Attribute | Type | Notes |
|---|---|---|
| PK | String | `USER#<id>` or `ITEM#<id>` |
| SK | String | `PROFILE` or `REPORT#<timestamp>` |
| type | String | `lost` / `found` |
| description | String | Free text |
| embedding | List<Number> | Vector for similarity (or stored externally) |
| status | String | `active` / `matched` / `claimed` |
| createdAt | String | ISO timestamp |
| ttl | Number | Epoch seconds (retention) |

### 9.4 Key API Endpoints

Authentication (sign-up, login, password reset) is handled by the **Cognito Hosted UI** and is not exposed as application endpoints.

| Method | Path | Purpose |
|---|---|---|
| POST | `/items` | Create lost/found report |
| GET | `/items` | List authenticated user's reports |
| GET | `/items/{id}` | Get item details |
| GET | `/items/{id}/matches` | List candidate matches for an item |
| POST | `/items/{id}/claim` | Confirm or reject a claim |
| GET | `/notifications` | List in-app notifications (paged) |
| POST | `/notifications/{id}/read` | Mark notification read |
| POST | `/match` | Admin/replay-only trigger for the matching pipeline |
| GET | `/admin/reports` | Admin moderation list |
| POST | `/admin/items/{id}/override-match` | Force/override a match |
| GET | `/admin/audit` | Admin audit log |

---

## 10. Security Requirements

- JWT-based authentication on all protected endpoints.
- HTTPS / TLS 1.2+ enforced at API Gateway.
- Role-based access control (`user`, `admin`).
- Strict input validation (size, type, MIME).
- Image payload size cap (e.g., 5 MB) to mitigate abuse.
- Rate limiting via API Gateway usage plans.
- Encryption at rest for DynamoDB; secrets in AWS Secrets Manager.

---

## 11. Constraints

- No persistent image storage (no S3 in MVP).
- Images are processed transiently to extract embeddings; raw bytes are discarded.
- DynamoDB TTL governs report retention.
- **Item retention TTL: 90 days** from `created_at` (configurable via SSM).
- **Notification retention TTL: 90 days**.
- **Embedding model version** is recorded on every item record so future model changes do not silently invalidate stored vectors.
- **Cost stance:** Provisioned concurrency is enabled only on `create_item` in `prod`; `dev`/`staging` rely on on-demand to stay near free-tier. The free-tier target in NFRs applies to non-prod environments.

---

## 12. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| False-positive matches | User frustration, wrong claims | Tune threshold, require confirmation, admin override |
| Large image payloads | Latency, cost | Enforce size limits; resize client-side |
| Embedding model drift | Match quality decay | Versioned model; periodic evaluation |
| Cold-start latency | Slow first response | Provisioned concurrency for hot Lambdas |
| Abuse / spam reports | Data pollution | Rate limiting, moderation, captcha on signup |

---

## 13. Assumptions

- Users provide reasonably accurate descriptions and clear images.
- The chosen embedding model produces useful similarity signals for everyday objects.
- Users have stable internet connectivity.
- The pilot scope (single facility / campus) keeps volume manageable.

---

## 14. Future Enhancements

- Native mobile applications (iOS / Android).
- Face recognition for personal items (with explicit consent).
- Real-time SMS / push notifications.
- Geo-location-based matching radius.
- Multi-language description support.
- Reward / incentive program for finders.

---

## 15. Milestones (Indicative)

| Phase | Deliverable | Target |
|---|---|---|
| M1 | CDK skeleton, Cognito, basic CRUD | Week 2 |
| M2 | Embedding + matching service | Week 4 |
| M3 | Notifications + claim flow | Week 6 |
| M4 | Admin dashboard + analytics | Week 8 |
| M5 | Pilot launch | Week 10 |

---

## 16. Resolved Decisions

| # | Question | Decision |
|---|---|---|
| 1 | Embedding model | **Bedrock Titan Multimodal** (image) + **Bedrock Titan Text v2** (text). Self-hosted CLIP deferred. |
| 2 | Similarity threshold default | **0.75** (cosine), tunable per-environment via SSM. |
| 3 | Anonymous reporting | **Deferred** post-MVP. All MVP reports require authentication. |
| 4 | Report retention TTL | **90 days** from `created_at`. |
| 5 | Notification channel for MVP | **Email (SES) + in-app feed.** Web push deferred. |
| 6 | Matching trigger | **Asynchronous via DynamoDB Streams.** `POST /match` exists only as an admin / replay tool. |
| 7 | Auth endpoints | **Cognito Hosted UI** owns sign-up/login. PRD §9.4 `/auth/*` rows are removed; only token refresh proxy is exposed. |
| 8 | Image retention | **Zero persistence.** Raw bytes discarded after embedding extraction. |
