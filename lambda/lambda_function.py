"""
Serverless Contact Form — Lambda Function
=====================================================
Handles two endpoints:
  POST /contact  →  save message to DynamoDB + send email via SES
  GET  /stats    →  return total message count

Environment Variables required:
  TABLE_NAME    = contact-messages
  SENDER_EMAIL  = your-verified-ses-email@domain.com
"""

import json
import os
import uuid
import boto3
from datetime import datetime

# ── AWS clients ────────────────────────────────────────────
dynamodb = boto3.resource("dynamodb")
ses      = boto3.client("ses")

TABLE_NAME   = os.environ["TABLE_NAME"]
SENDER_EMAIL = os.environ["SENDER_EMAIL"]

table = dynamodb.Table(TABLE_NAME)


# ══════════════════════════════════════════════════════════
#  MAIN HANDLER
# ══════════════════════════════════════════════════════════
def lambda_handler(event, context):
    method = event.get("httpMethod", "")
    path   = event.get("path", "")

    # Handle CORS preflight request
    if method == "OPTIONS":
        return _response(200, {"status": "ok"})

    # ── Route: POST /contact ──────────────────────────────
    if method == "POST" and path == "/contact":
        return handle_submit(event)

    # ── Route: GET /stats ──────────────────────────────────
    if method == "GET" and path == "/stats":
        return handle_stats()

    return _response(404, {"error": "Endpoint not found"})


# ══════════════════════════════════════════════════════════
#  POST /contact  —  Save message & send email via SES
# ══════════════════════════════════════════════════════════
def handle_submit(event):
    try:
        # Parse body
        raw  = event.get("body", "{}")
        body = json.loads(raw) if isinstance(raw, str) else raw

        # Validate required fields
        required = ["name", "email", "subject", "message"]
        missing  = [f for f in required if not str(body.get(f, "")).strip()]
        if missing:
            return _response(400, {
                "error": f"Missing required fields: {', '.join(missing)}"
            })

        # Build record
        message_id = str(uuid.uuid4())
        record = {
            "message_id": message_id,
            "name":       body["name"].strip(),
            "email":      body["email"].strip(),
            "subject":    body["subject"].strip(),
            "message":    body["message"].strip(),
            "status":     "new",
            "created_at": datetime.utcnow().isoformat(),
        }

        # Save to DynamoDB
        table.put_item(Item=record)

        # Send email notification via SES
        _send_ses_email(record)

        return _response(200, {
            "message_id": message_id,
            "message":    "Your message has been sent successfully!",
        })

    except Exception as e:
        print(f"Error in handle_submit: {e}")
        return _response(500, {"error": "Internal server error. Please try again."})


# ══════════════════════════════════════════════════════════
#  GET /stats  —  Return total message count
# ══════════════════════════════════════════════════════════
def handle_stats():
    try:
        result = table.scan(Select="COUNT")
        total  = result.get("Count", 0)
        return _response(200, {"total_messages": total})
    except Exception as e:
        print(f"Error in handle_stats: {e}")
        return _response(500, {"error": str(e)})


# ══════════════════════════════════════════════════════════
#  SES Email Notification
# ══════════════════════════════════════════════════════════
def _send_ses_email(record):
    """Sends an email to the site owner via Amazon SES."""
    email_subject = f"[Contact Form] New message: {record['subject']}"

    email_body = f"""
You received a new message via Contact Form!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  From     : {record['name']}
  Email    : {record['email']}
  Subject  : {record['subject']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Message:
{record['message']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Message ID : {record['message_id']}
Received   : {record['created_at']} UTC
    """.strip()

    ses.send_email(
        Source=SENDER_EMAIL,
        Destination={
            "ToAddresses": [SENDER_EMAIL]
        },
        Message={
            "Subject": {
                "Data": email_subject,
                "Charset": "UTF-8"
            },
            "Body": {
                "Text": {
                    "Data": email_body,
                    "Charset": "UTF-8"
                }
            }
        },
        ReplyToAddresses=[record["email"]]
    )


# ══════════════════════════════════════════════════════════
#  Helper: standard HTTP response
# ══════════════════════════════════════════════════════════
def _response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type":                 "application/json",
            "Access-Control-Allow-Origin":  "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body_dict, ensure_ascii=False),
    }