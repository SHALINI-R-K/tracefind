import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from contexts.notification.interfaces.events.on_match_found import lambda_handler

@patch("contexts.notification.interfaces.events.on_match_found._command")
@patch("contexts.notification.interfaces.events.on_match_found._get_reports")
@patch("contexts.notification.interfaces.events.on_match_found.CognitoUserDirectory")
def test_on_match_found_success(mock_user_dir, mock_get_reports, mock_command):
    # Mock reports
    lost_report = MagicMock()
    lost_report.user_id = "user-lost"
    lost_report.description.value = "lost item"
    
    found_report = MagicMock()
    found_report.user_id = "user-found"
    found_report.description.value = "found item"
    
    mock_get_reports.return_value = (lost_report, found_report)
    
    # Mock user directory
    mock_user_dir_instance = mock_user_dir.return_value
    mock_user_dir_instance.email_for.side_effect = lambda uid: f"{uid}@example.com"
    
    # Mock event
    event = {
        "Records": [{
            "eventName": "INSERT",
            "dynamodb": {
                "NewImage": {
                    "id": {"S": "match-123"},
                    "score": {"N": "0.85"},
                    "lost_item_id": {"S": "item-lost"},
                    "found_item_id": {"S": "item-found"}
                }
            }
        }]
    }
    
    result = lambda_handler(event, None)
    
    assert result["sent"] == 2
    assert mock_command.execute.call_count == 2
    
    # Verify first call (to lost owner)
    args, kwargs = mock_command.execute.call_args_list[0]
    assert kwargs["user_id"] == "user-lost"
    assert kwargs["payload"]["other_party_email"] == "user-found@example.com"
    assert kwargs["payload"]["other_item_description"] == "found item"
    
    # Verify second call (to found owner)
    args, kwargs = mock_command.execute.call_args_list[1]
    assert kwargs["user_id"] == "user-found"
    assert kwargs["payload"]["other_party_email"] == "user-lost@example.com"
    assert kwargs["payload"]["other_item_description"] == "lost item"

@patch("contexts.notification.interfaces.events.on_match_found._get_reports")
def test_on_match_found_missing_reports(mock_get_reports):
    mock_get_reports.return_value = (None, None)
    
    event = {
        "Records": [{
            "eventName": "INSERT",
            "dynamodb": {
                "NewImage": {
                    "id": {"S": "match-123"},
                    "score": {"N": "0.85"},
                    "lost_item_id": {"S": "item-lost"},
                    "found_item_id": {"S": "item-found"}
                }
            }
        }]
    }
    
    result = lambda_handler(event, None)
    assert result["sent"] == 0
