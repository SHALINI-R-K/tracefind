# TraceFind

Smart Lost & Found System — AI-driven item matching across campuses, offices, and public facilities.

- [PRD.md](PRD.md) — product requirements
- [TDD.md](TDD.md) — technical design
- [ARCHITECTURE.md](ARCHITECTURE.md) — DDD bounded contexts and folder layout

## Repository layout

```
TraceFind/
├── backend/    # Python serverless (DDD: 5 bounded contexts)
│   ├── src/contexts/{identity_access,reporting,matching,claims,notification}
│   ├── src/shared/
│   └── tests/
├── infra/      # AWS CDK (Python) — Auth, Data, Api stacks
└── frontend/   # Next.js + Tailwind, Cognito Hosted UI via Amplify
```

## Backend

```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows: .venv/Scripts/activate
pip install -e ".[test]"
pytest
```

Each Lambda is a thin interface adapter at `src/contexts/<ctx>/interfaces/{http,events}/`.
Aggregate roots, value objects, and repository ports live under `domain/`.
DynamoDB and Bedrock adapters live under `infrastructure/`.

## Infrastructure

```bash
cd infra
python -m venv .venv && source .venv/Scripts/activate
pip install -r requirements.txt
npm i -g aws-cdk
cdk bootstrap
cdk deploy --all
```

After deploy, capture the Cognito user pool id, app client id, and API URL into
`frontend/.env.local`. Ensure `SMTP_FROM_EMAIL` and `FRONTEND_URL` are set during
deployment to enable branded match notifications.

## Frontend

```bash
cd frontend
cp .env.example .env.local      # fill in values from CDK outputs
npm install
npm run dev
```

Visit `http://localhost:3000`. Cognito Hosted UI handles sign-up/sign-in.

## Bounded contexts

| Context | Responsibility | Aggregate |
|---|---|---|
| `identity_access` | Cognito-backed user directory | `User` |
| `reporting` | Lost/found report lifecycle | `ItemReport` |
| `matching` | AI similarity matching (Bedrock Titan + cosine) | `Match` |
| `claims` | Two-party claim flow with TransactWriteItems lock | `Claim` |
| `notification` | In-app feed + Gmail SMTP email | `Notification` |

Cross-context coordination is **event-driven**: DynamoDB Streams on the Items
table trigger matching; streams on the Matches table trigger notifications.
