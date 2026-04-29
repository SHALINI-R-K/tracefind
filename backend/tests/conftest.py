import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("ITEMS_TABLE", "test-items")
os.environ.setdefault("MATCHES_TABLE", "test-matches")
os.environ.setdefault("CLAIMS_TABLE", "test-claims")
os.environ.setdefault("NOTIFICATIONS_TABLE", "test-notifications")
os.environ.setdefault("AUDIT_TABLE", "test-audit")
