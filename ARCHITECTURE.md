# TraceFind — DDD Architecture & Folder Structure

This project follows **Domain-Driven Design (DDD)** with explicit **bounded contexts**, a **layered architecture** (domain → application → infrastructure → interfaces), and a **shared kernel** for cross-cutting primitives.

---

## 1. Bounded Contexts

| Context | Responsibility | Aggregate Roots |
|---|---|---|
| `identity_access` | User registration, authentication, RBAC | `User` |
| `reporting` | Lost / found item reports lifecycle | `ItemReport` |
| `matching` | AI-driven similarity matching between reports | `Match` |
| `notification` | Outbound notifications (email, in-app) | `Notification` |
| `claims` | Confirmation and claim workflow | `Claim` |

Each context is **autonomous**: it owns its domain model, its persistence, and its API surface. Contexts communicate through **domain events** published on a shared event bus, never through direct database reads of another context's tables.

### Context Map

```
identity_access ──(provides UserId)──▶ reporting
                                       │
                                       │ publishes ItemReported
                                       ▼
                                    matching ──publishes MatchFound──▶ notification
                                       │
                                       │ publishes MatchFound
                                       ▼
                                     claims ──publishes ItemClaimed──▶ notification
```

---

## 2. Layered Architecture (per context)

```
contexts/<context>/
├── domain/              ← Pure business logic, zero framework deps
│   ├── entities/        ← Aggregate roots & entities
│   ├── value_objects/   ← Immutable, equality-by-value
│   ├── repositories/    ← Repository interfaces (ports)
│   ├── events/          ← Domain events
│   └── services/        ← Domain services (logic that doesn't fit one entity)
│
├── application/         ← Use cases / orchestration
│   ├── commands/        ← Write use cases (CreateItemReport, ClaimItem, …)
│   ├── queries/         ← Read use cases (GetItemReport, ListMatches, …)
│   └── dtos/            ← Data transfer objects in/out of application layer
│
├── infrastructure/      ← Adapters: implements domain ports
│   ├── persistence/     ← DynamoDB repositories
│   ├── cognito/ | ses/ | embedding/   ← External service adapters
│   └── ...
│
└── interfaces/          ← Inbound adapters / driving side
    ├── http/            ← Lambda handlers behind API Gateway
    └── events/          ← Event subscribers (DynamoDB Stream / EventBridge)
```

**Dependency rule:** outer layers depend on inner layers, never the reverse.
`interfaces → application → domain ← infrastructure`

---

## 3. Repository Layout

```
TraceFind/
├── PRD.md
├── TDD.md
├── ARCHITECTURE.md
│
├── backend/
│   ├── src/
│   │   ├── contexts/
│   │   │   ├── identity_access/
│   │   │   │   ├── domain/
│   │   │   │   │   ├── entities/        # user.py
│   │   │   │   │   ├── value_objects/   # email.py, role.py
│   │   │   │   │   ├── repositories/    # user_repository.py (interface)
│   │   │   │   │   ├── events/          # user_registered.py
│   │   │   │   │   └── services/
│   │   │   │   ├── application/
│   │   │   │   │   ├── commands/        # register_user.py, login.py
│   │   │   │   │   ├── queries/         # get_user_profile.py
│   │   │   │   │   └── dtos/
│   │   │   │   ├── infrastructure/
│   │   │   │   │   ├── persistence/     # dynamo_user_repository.py
│   │   │   │   │   └── cognito/         # cognito_auth_provider.py
│   │   │   │   └── interfaces/
│   │   │   │       └── http/            # signup_handler.py, login_handler.py
│   │   │   │
│   │   │   ├── reporting/
│   │   │   │   ├── domain/
│   │   │   │   │   ├── entities/        # item_report.py (aggregate root)
│   │   │   │   │   ├── value_objects/   # report_type.py, description.py, image_payload.py, category.py
│   │   │   │   │   ├── repositories/    # item_report_repository.py
│   │   │   │   │   ├── events/          # item_reported.py, report_status_changed.py
│   │   │   │   │   └── services/
│   │   │   │   ├── application/
│   │   │   │   │   ├── commands/        # create_item_report.py, archive_report.py
│   │   │   │   │   ├── queries/         # list_user_reports.py, get_report.py
│   │   │   │   │   └── dtos/
│   │   │   │   ├── infrastructure/
│   │   │   │   │   └── persistence/     # dynamo_item_report_repository.py
│   │   │   │   └── interfaces/
│   │   │   │       └── http/            # create_item_handler.py, get_items_handler.py
│   │   │   │
│   │   │   ├── matching/
│   │   │   │   ├── domain/
│   │   │   │   │   ├── entities/        # match.py (aggregate root)
│   │   │   │   │   ├── value_objects/   # embedding.py, similarity_score.py, match_threshold.py
│   │   │   │   │   ├── repositories/    # match_repository.py, embedding_repository.py
│   │   │   │   │   ├── events/          # match_found.py
│   │   │   │   │   └── services/        # similarity_calculator.py, matching_service.py
│   │   │   │   ├── application/
│   │   │   │   │   ├── commands/        # run_matching.py
│   │   │   │   │   ├── queries/         # list_matches_for_item.py
│   │   │   │   │   └── dtos/
│   │   │   │   ├── infrastructure/
│   │   │   │   │   ├── persistence/     # dynamo_match_repository.py
│   │   │   │   │   └── embedding/       # bedrock_embedding_client.py, clip_embedding_client.py
│   │   │   │   └── interfaces/
│   │   │   │       ├── http/            # trigger_match_handler.py, get_matches_handler.py
│   │   │   │       └── events/          # on_item_reported.py (DDB Stream subscriber)
│   │   │   │
│   │   │   ├── notification/
│   │   │   │   ├── domain/
│   │   │   │   │   ├── entities/        # notification.py
│   │   │   │   │   ├── value_objects/   # channel.py, recipient.py
│   │   │   │   │   ├── repositories/    # notification_repository.py
│   │   │   │   │   └── events/          # notification_sent.py
│   │   │   │   ├── application/
│   │   │   │   │   ├── commands/        # send_match_notification.py
│   │   │   │   │   └── dtos/
│   │   │   │   ├── infrastructure/
│   │   │   │   │   ├── ses/             # ses_email_sender.py
│   │   │   │   │   └── persistence/     # dynamo_notification_repository.py
│   │   │   │   └── interfaces/
│   │   │   │       └── events/          # on_match_found.py
│   │   │   │
│   │   │   └── claims/
│   │   │       ├── domain/
│   │   │       │   ├── entities/        # claim.py (aggregate root)
│   │   │       │   ├── value_objects/   # claim_status.py
│   │   │       │   ├── repositories/    # claim_repository.py
│   │   │       │   └── events/          # item_claimed.py, claim_rejected.py
│   │   │       ├── application/
│   │   │       │   ├── commands/        # confirm_claim.py, reject_claim.py
│   │   │       │   ├── queries/         # get_claim.py
│   │   │       │   └── dtos/
│   │   │       ├── infrastructure/
│   │   │       │   └── persistence/     # dynamo_claim_repository.py
│   │   │       └── interfaces/
│   │   │           └── http/            # claim_item_handler.py
│   │   │
│   │   └── shared/                      # Shared kernel — minimal, stable
│   │       ├── domain/
│   │       │   ├── value_objects/       # user_id.py, item_id.py, timestamp.py
│   │       │   ├── events/              # domain_event.py (base class)
│   │       │   └── exceptions/          # domain_exception.py
│   │       ├── application/             # base command/query, unit_of_work
│   │       └── infrastructure/
│   │           ├── event_bus/           # eventbridge_publisher.py
│   │           ├── logging/             # structured_logger.py
│   │           └── aws/                 # boto3_clients.py
│   │
│   ├── tests/
│   │   ├── unit/contexts/<ctx>/
│   │   ├── integration/
│   │   └── e2e/
│   ├── pyproject.toml
│   └── requirements.txt
│
├── infra/                                # CDK Infrastructure as Code
│   ├── cdk/
│   │   ├── stacks/
│   │   │   ├── auth_stack.py             # Cognito
│   │   │   ├── data_stack.py             # DynamoDB tables, streams
│   │   │   ├── api_stack.py              # API Gateway + Lambdas
│   │   │   └── frontend_stack.py         # Amplify / CloudFront
│   │   └── constructs/                   # Reusable CDK constructs
│   ├── config/                           # env config (dev/staging/prod)
│   ├── app.py                            # CDK app entrypoint
│   └── cdk.json
│
└── frontend/                             # Next.js — DDD-aligned feature folders
    ├── src/
    │   ├── app/                          # Next.js App Router pages
    │   ├── contexts/
    │   │   ├── identity_access/
    │   │   │   ├── components/           # LoginForm, SignupForm
    │   │   │   ├── hooks/                # useAuth
    │   │   │   └── api/                  # auth client
    │   │   ├── reporting/
    │   │   │   ├── components/           # ReportItemForm, ItemList
    │   │   │   ├── hooks/                # useReports
    │   │   │   └── api/                  # reports client
    │   │   ├── matching/
    │   │   │   ├── components/           # MatchList, MatchCard
    │   │   │   ├── hooks/                # useMatches
    │   │   │   └── api/
    │   │   ├── notification/
    │   │   │   ├── components/           # NotificationFeed
    │   │   │   └── hooks/                # useNotifications
    │   │   └── claims/
    │   │       ├── components/           # ClaimDialog
    │   │       └── hooks/                # useClaim
    │   └── shared/
    │       ├── components/               # Button, Modal, Toast
    │       ├── lib/                      # http client, auth helpers
    │       └── types/                    # cross-cutting types
    ├── package.json
    ├── tailwind.config.ts
    └── next.config.js
```

---

## 4. Tactical DDD Patterns Used

| Pattern | Where |
|---|---|
| **Aggregate Root** | `User`, `ItemReport`, `Match`, `Claim`, `Notification` |
| **Value Object** | `Email`, `Role`, `ReportType`, `Description`, `ImagePayload`, `Embedding`, `SimilarityScore`, `MatchThreshold`, `Channel` |
| **Domain Event** | `UserRegistered`, `ItemReported`, `MatchFound`, `ItemClaimed`, `NotificationSent` |
| **Repository (Port)** | Interfaces in `domain/repositories/`, implementations in `infrastructure/persistence/` |
| **Application Service / Use Case** | `commands/*` for writes, `queries/*` for reads (CQRS-lite) |
| **Anti-Corruption Layer** | `infrastructure/cognito/`, `infrastructure/embedding/`, `infrastructure/ses/` translate external models to domain |
| **Shared Kernel** | `shared/domain/value_objects/` (`UserId`, `ItemId`) — only ids and base types, no business logic |
| **Domain Event Bus** | `shared/infrastructure/event_bus/` (EventBridge or DynamoDB Streams) |

---

## 5. Inter-Context Communication Rules

1. A context never calls another context's repository or database directly.
2. Cross-context coordination happens via **domain events** published on the event bus.
3. Synchronous reads across contexts go through the other context's **application query** (use case), not its persistence.
4. Shared identifiers (`UserId`, `ItemId`) live in `shared/domain/value_objects/` to avoid duplication.

---

## 6. Lambda Packaging Strategy

Each Lambda function maps to **one interface adapter** in a single context:

| Lambda | Entrypoint |
|---|---|
| `create_item` | `contexts/reporting/interfaces/http/create_item_handler.py` |
| `get_items` | `contexts/reporting/interfaces/http/get_items_handler.py` |
| `match_items` | `contexts/matching/interfaces/events/on_item_reported.py` |
| `get_matches` | `contexts/matching/interfaces/http/get_matches_handler.py` |
| `claim_item` | `contexts/claims/interfaces/http/claim_item_handler.py` |
| `notify_users` | `contexts/notification/interfaces/events/on_match_found.py` |

Handlers are **thin** — they parse input, call the application command/query, and serialize the result. No business logic in handlers.
