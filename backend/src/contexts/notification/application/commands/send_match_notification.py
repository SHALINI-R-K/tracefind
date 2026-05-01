from __future__ import annotations

import html
import logging
import os
from dataclasses import dataclass
from typing import Any

from shared.infrastructure.logging.structured_logger import get_logger, log

from contexts.notification.domain.entities.notification import Notification
from contexts.notification.domain.repositories.notification_repository import (
    NotificationRepository,
)
from contexts.notification.domain.services.email_sender import EmailSender
from shared.domain.exceptions.domain_exception import ConflictError
from shared.domain.value_objects.identifier import UserId

_logger = get_logger("notification.send_match_notification")


@dataclass
class SendMatchNotificationCommand:
    repository: NotificationRepository
    email_sender: EmailSender
    ttl_seconds: int

    def execute(self, *, user_id: str, payload: dict[str, Any]) -> None:
        match_id = payload.get("match_id")
        if not match_id:
            raise ValueError("payload.match_id is required for idempotent send")

        notification = Notification.for_match(
            user_id=UserId(user_id),
            match_id=str(match_id),
            payload=payload,
            ttl_seconds=self.ttl_seconds,
        )
        try:
            self.repository.save(notification)
        except ConflictError:
            # Stream retry / batch redelivery — already notified this user for
            # this match. Skip email so we don't double-send.
            log(
                _logger,
                logging.INFO,
                "duplicate_notification_skipped",
                user_id=user_id,
                match_id=match_id,
            )
            return

        try:
            self.email_sender.send(
                to_user_id=user_id,
                subject=_email_subject(payload),
                body_html=_render_email(payload),
            )
        except Exception as exc:
            # We log but don't re-raise, so in-app notification is still considered successful
            log(_logger, logging.WARNING, "email_delivery_failed", user_id=user_id, error=str(exc))


def _email_subject(payload: dict[str, Any]) -> str:
    score = payload.get("score", 0)
    pct = int(round(float(score) * 100))
    item_type = payload.get("item_type", "item")
    if item_type == "lost":
        return f"TraceFind: a found item may match yours ({pct}% similarity)"
    return f"TraceFind: someone may have lost the item you reported ({pct}% similarity)"


def _render_email(payload: dict[str, Any]) -> str:
    """Render the match-found email.

    Email-client constraints honored:
      - inline CSS only (Gmail strips <style>)
      - <table>-based layout (Outlook ignores flex/grid)
      - 600px max width, system-font stack
      - light theme (Gmail dark-mode auto-inverts safely)
      - no external images or webfonts (silent failures otherwise)
    """
    score = float(payload.get("score") or 0)
    pct = int(round(score * 100))
    score_label = _score_label(score)

    other_email = payload.get("other_party_email") or "Contact via app"
    other_desc = payload.get("other_item_description") or "No description provided"
    item_type = payload.get("item_type") or "item"

    # Frame: I lost X → someone may have FOUND it (counterpart is "found")
    counterpart_label = "found" if item_type == "lost" else "lost"
    intro = (
        "Someone reported a found item that may be yours."
        if item_type == "lost"
        else "Someone reported losing an item that matches what you found."
    )

    # Frontend URL for the CTA — fallback to a clear placeholder if unset
    dashboard_url = os.environ.get(
        "FRONTEND_URL", "https://tracefind.app"
    ).rstrip("/") + "/dashboard"

    # Escape user-controlled fields to prevent HTML injection in the email body
    safe_other_email = html.escape(str(other_email))
    safe_other_desc = html.escape(str(other_desc))
    safe_item_type = html.escape(str(item_type))
    safe_counterpart_label = html.escape(counterpart_label)

    return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>TraceFind — possible match</title>
  </head>
  <body style="margin:0;padding:0;background:#f5f5f4;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:#1a1f2e;line-height:1.55;-webkit-font-smoothing:antialiased;">
    <!-- Preheader (preview text in inbox list) -->
    <div style="display:none;max-height:0;overflow:hidden;color:#f5f5f4;">
      {pct}% match on your {safe_item_type} report — sign in to confirm.
    </div>

    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f5f5f4;padding:32px 16px;">
      <tr>
        <td align="center">
          <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(26,31,46,0.08);">
            <!-- Brand bar -->
            <tr>
              <td style="background:#1a1f2e;padding:20px 28px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="color:#ffffff;font-weight:700;font-size:18px;letter-spacing:-0.01em;">
                      <span style="display:inline-block;width:24px;height:24px;background:#f2a02e;border-radius:6px;vertical-align:middle;margin-right:10px;text-align:center;line-height:24px;color:#1a1f2e;font-size:14px;">⌖</span>
                      TraceFind
                    </td>
                    <td align="right" style="color:#9ca3af;font-size:11px;font-family:Menlo,Consolas,monospace;text-transform:uppercase;letter-spacing:0.18em;">
                      AI-powered recovery
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <!-- Hero -->
            <tr>
              <td style="padding:40px 28px 8px;">
                <p style="margin:0 0 12px;font-size:11px;font-family:Menlo,Consolas,monospace;text-transform:uppercase;letter-spacing:0.22em;color:#f2a02e;font-weight:600;">
                  Match found
                </p>
                <h1 style="margin:0;font-size:28px;line-height:1.2;letter-spacing:-0.02em;font-weight:700;color:#1a1f2e;">
                  We may have found your {safe_item_type} item.
                </h1>
                <p style="margin:14px 0 0;font-size:15px;color:#4b5563;">
                  {intro} Review the details below and reach out to the other
                  party to confirm.
                </p>
              </td>
            </tr>

            <!-- Score capsule -->
            <tr>
              <td style="padding:24px 28px 8px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#fff7ed;border:1px solid #fde2b8;border-radius:10px;">
                  <tr>
                    <td style="padding:18px 22px;">
                      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                          <td style="vertical-align:middle;">
                            <p style="margin:0;font-size:11px;font-family:Menlo,Consolas,monospace;text-transform:uppercase;letter-spacing:0.18em;color:#92400e;font-weight:600;">
                              Similarity
                            </p>
                            <p style="margin:4px 0 0;font-size:32px;line-height:1;font-weight:700;color:#1a1f2e;letter-spacing:-0.02em;">
                              {pct}<span style="font-size:18px;color:#9a6a1f;">%</span>
                            </p>
                          </td>
                          <td align="right" style="vertical-align:middle;">
                            <span style="display:inline-block;background:#f2a02e;color:#1a1f2e;font-weight:700;font-size:12px;padding:8px 14px;border-radius:999px;letter-spacing:-0.005em;">
                              {score_label}
                            </span>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <!-- Item details -->
            <tr>
              <td style="padding:24px 28px 8px;">
                <p style="margin:0 0 14px;font-size:11px;font-family:Menlo,Consolas,monospace;text-transform:uppercase;letter-spacing:0.22em;color:#6b7280;font-weight:600;">
                  Their {safe_counterpart_label} item
                </p>
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;">
                  <tr>
                    <td style="padding:18px 22px;">
                      <p style="margin:0;font-size:14px;color:#374151;font-style:italic;line-height:1.55;">
                        &ldquo;{safe_other_desc}&rdquo;
                      </p>
                    </td>
                  </tr>
                  <tr>
                    <td style="padding:0 22px 18px;">
                      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                        <tr>
                          <td style="font-size:11px;font-family:Menlo,Consolas,monospace;text-transform:uppercase;letter-spacing:0.18em;color:#6b7280;padding-top:10px;border-top:1px solid #e5e7eb;">
                            Contact
                          </td>
                        </tr>
                        <tr>
                          <td style="padding-top:6px;">
                            <a href="mailto:{safe_other_email}" style="color:#1a1f2e;font-weight:600;font-size:15px;text-decoration:none;border-bottom:2px solid #f2a02e;">
                              {safe_other_email}
                            </a>
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <!-- CTA -->
            <tr>
              <td style="padding:28px 28px 8px;" align="center">
                <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td align="center" style="background:#1a1f2e;border-radius:8px;">
                      <a href="{html.escape(dashboard_url)}" style="display:inline-block;padding:14px 28px;color:#ffffff;font-weight:600;font-size:15px;text-decoration:none;letter-spacing:-0.005em;">
                        Review match in TraceFind &rarr;
                      </a>
                    </td>
                  </tr>
                </table>
                <p style="margin:14px 0 0;font-size:13px;color:#6b7280;">
                  Or reply directly to the other party using the email above.
                </p>
              </td>
            </tr>

            <!-- Tips -->
            <tr>
              <td style="padding:32px 28px 16px;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid #e5e7eb;">
                  <tr>
                    <td style="padding-top:18px;">
                      <p style="margin:0 0 8px;font-size:11px;font-family:Menlo,Consolas,monospace;text-transform:uppercase;letter-spacing:0.22em;color:#6b7280;font-weight:600;">
                        Before you meet
                      </p>
                      <ul style="margin:0;padding:0 0 0 18px;font-size:14px;color:#4b5563;line-height:1.7;">
                        <li>Confirm a distinctive detail only the rightful owner would know.</li>
                        <li>Meet in a public, well-lit place — campus security desk, café, lobby.</li>
                        <li>If the match isn&rsquo;t right, reject it on the dashboard so the matcher learns.</li>
                      </ul>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>

            <!-- Footer -->
            <tr>
              <td style="padding:18px 28px 24px;background:#fafaf9;border-top:1px solid #e5e7eb;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td style="font-size:11px;color:#9ca3af;font-family:Menlo,Consolas,monospace;text-transform:uppercase;letter-spacing:0.18em;">
                      Sent because you reported a {safe_item_type} item
                    </td>
                  </tr>
                  <tr>
                    <td style="padding-top:6px;font-size:11px;color:#9ca3af;">
                      TraceFind &middot; AI-powered lost &amp; found
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""".strip()


def _score_label(score: float) -> str:
    """Human-readable confidence band for the similarity score."""
    if score >= 0.90:
        return "Very strong"
    if score >= 0.80:
        return "Strong"
    if score >= 0.70:
        return "Likely"
    return "Possible"
