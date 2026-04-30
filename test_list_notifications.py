import os
import json
from decimal import Decimal

# Set env vars
os.environ["NOTIFICATIONS_TABLE"] = "tracefind-notifications"
os.environ["AWS_REGION"] = "ap-south-1"

# Mock event with the user ID found in our previous scan
user_id = "11b32d9a-10d1-708a-8fa3-f446c4b3ef27"
event = {
    "requestContext": {
        "authorizer": {
            "jwt": {
                "claims": {
                    "sub": user_id
                }
            }
        }
    }
}

import sys
sys.path.append("backend/src")

from contexts.notification.interfaces.http.notifications_handler import list_handler

print(f"Calling list_handler for user {user_id}...")
try:
    result = list_handler(event, None)
    print(f"Status: {result['statusCode']}")
    print(f"Body: {result['body']}")
except Exception as e:
    import traceback
    print(f"Crash: {e}")
    traceback.print_exc()
