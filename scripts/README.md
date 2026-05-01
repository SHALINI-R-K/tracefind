# scripts/

Ad-hoc developer tooling. **Not** part of the production code or the pytest suite.
All scripts target the deployed AWS environment (`ap-south-1`) and read/write
real DynamoDB tables — run with care.

## Layout

- [`dev/`](dev/) — operational helpers (inspect, clear, retrigger)
- [`manual_tests/`](manual_tests/) — one-shot Lambda invocations against live data; named `test_*` but **not** pytest tests. The real test suite lives in [`backend/tests/`](../backend/tests/).

## dev/

| Script | Purpose |
|---|---|
| [`check_item_status.py`](dev/check_item_status.py) | Scan `tracefind-items` and print id/type/status/description for every row. |
| [`check_items.py`](dev/check_items.py) | Pull one lost + one found item, compare their Titan embeddings, print cosine similarity vs the 0.75 match threshold. |
| [`check_models.py`](dev/check_models.py) | Scan items and report each row's `embedding_model_version` and embedding length — useful when validating a re-embed. |
| [`check_tables.py`](dev/check_tables.py) | Dump the full `tracefind-matches` and `tracefind-notifications` tables as JSON. |
| [`check_user_ids.py`](dev/check_user_ids.py) | Scan items and print `id / type / user_id` per row. |
| [`clear_matches.py`](dev/clear_matches.py) | **Destructive.** Bulk-delete every row in `tracefind-matches`. |
| [`clear_notifications.py`](dev/clear_notifications.py) | **Destructive.** Bulk-delete every row in `tracefind-notifications`. |
| [`compare_embeddings.py`](dev/compare_embeddings.py) | Compute cosine similarity between two specific item ids (ids hard-coded in the script — edit before running). |
| [`retrigger_matching.py`](dev/retrigger_matching.py) | Re-run the matching command for every active item, bypassing DynamoDB Streams. Imports from `backend/src` — run from the repo root. |

## manual_tests/

| Script | Purpose |
|---|---|
| [`test_list_notifications.py`](manual_tests/test_list_notifications.py) | Invoke `notifications_handler.list_handler` with a synthesized JWT-claims event for a hard-coded `user_id`. |
| [`test_notification_fix.py`](manual_tests/test_notification_fix.py) | Scan `tracefind-matches` for `pending` rows, synthesize a DynamoDB Streams event, and invoke `on_match_found.lambda_handler` for each. |
| [`test_notification_trigger.py`](manual_tests/test_notification_trigger.py) | Invoke `on_match_found.lambda_handler` with one hard-coded match payload. |

## Running

These scripts assume:
- AWS credentials in the environment (or default profile) with read/write on the `tracefind-*` tables
- Region `ap-south-1`
- `boto3` installed (`pip install -e backend/[test]` covers it)

Scripts that import from the backend (`retrigger_matching.py`, the `manual_tests/*`) `sys.path.append("backend/src")` and **must be run from the repo root**:

```bash
python scripts/dev/retrigger_matching.py
python scripts/manual_tests/test_list_notifications.py
```

## Adding a new script

If a script becomes recurring, promote it: add a CLI entry in `backend/pyproject.toml` or convert it into a proper test under `backend/tests/`. This folder is for one-off helpers, not durable tooling.
