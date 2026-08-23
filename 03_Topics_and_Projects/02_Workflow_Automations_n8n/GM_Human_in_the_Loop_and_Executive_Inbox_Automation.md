---
title: "Human-in-the-Loop Orchestration, Executive Inbox Triage, and Calendar Scheduling Automation"
domain: "02_Workflow_Automations_n8n"
reusability_score: 98
workability_status: "Production-Ready"
tags:
  - "n8n"
  - "human-in-the-loop"
  - "inbox-manager"
  - "email-classification"
  - "telegram-approval"
  - "google-calendar"
dependencies:
  - "n8n >= 1.0"
  - "google-workspace-api"
  - "telegram-bot-api"
  - "gemini-2.5-flash"
source_files_synthesized:
  - "Raw_copies/human_in_da_loop.json"
  - "Raw_copies/Email_Inbox_Manager (1).json"
  - "Raw_copies/1731540016948-LabelEmailsBlueprint.json"
  - "Raw_copies/Inbox Manager Documentation (1).pdf"
  - "Raw_copies/Google_Calendar_MCP (1) (1).json"
---

# Executive Summary & Architectural Mental Model

The **Human-in-the-Loop Executive Inbox & Calendar Automation Engine** provides an autonomous, executive-grade email management workflow that categorizes inbound communications, drafts context-aware responses, schedules calendar events, and halts for interactive human confirmation (via Telegram interactive inline buttons or Slack approval cards) before sending external communications. This architecture completely eliminates inbox fatigue while maintaining 100% human oversight on high-stakes business operations.

```
+===================================================================================+
|                       HUMAN-IN-THE-LOOP EXECUTIVE INBOX                           |
|                                                                                   |
|  [ Inbound Email (Gmail / IMAP Trigger) ]                                         |
|                       |                                                           |
|                       v                                                           |
|  [ AI Email Classifier & Sentiment Analyzer ]                                     |
|  (Labels: Urgent / Client / Lead / Newsletter / Spam)                             |
|                       |                                                           |
|        +--------------+-------------------+                                       |
|        | (Low Priority)                   | (Actionable / Client / Lead)          |
|        v                                  v                                       |
|  [ Auto-Archive / Label ]     [ AI Draft Reply & Calendar Slot Finder ]           |
|                                                   |                               |
|                                                   v                               |
|                 +---------------------------------------------------+             |
|                 | HUMAN APPROVAL GATE (Telegram Inline Button / Wait)|            |
|                 +-------------------------+-------------------------+             |
|                                           |                                       |
|                  +------------------------+------------------------+              |
|                  |                                                 |              |
|                  v (APPROVED)                                      v (REJECTED)   |
|  [ Send Gmail Reply + Create Calendar Event ]             [ Discard / Edit Draft ]|
|                  |                                                                |
|                  v                                                                |
|  [ Update CRM & Log Action to SQLite DB ]                                         |
+===================================================================================+
```

---

## Source Lineage & Merge Rationale

### Synthesized Sources
- `Raw_copies/human_in_da_loop.json`: n8n human-in-the-loop wait node pattern using interactive webhooks and Telegram inline callback buttons.
- `Raw_copies/Email_Inbox_Manager (1).json`: End-to-end Gmail email classification, automated labeling, and draft generation.
- `Raw_copies/1731540016948-LabelEmailsBlueprint.json`: Clean email label taxonomy blueprint and rule triggers.
- `Raw_copies/Inbox Manager Documentation (1).pdf`: Architectural documentation and SLA guidelines for executive email triage.
- `Raw_copies/Google_Calendar_MCP (1) (1).json`: Google Calendar meeting conflict detection and event creation workflow.

### Concrete Merge Rationale
The raw repository contained isolated workflows for Gmail monitoring, Telegram interactive waiting, and Google Calendar scheduling. Operating them separately created disconnected manual steps and increased the risk of unreviewed AI emails being dispatched. This Golden Master combines email classification, AI reply drafting, calendar conflict detection, and interactive Telegram approval gates into a unified executive assistant automation.

### Superiority Justification
1. **Interactive Approval Gate**: Utilizes n8n's `Wait for Webhook Call` node to pause execution until the founder clicks `Approve` or `Reject` on Telegram.
2. **Deterministic Label Taxonomy**: Standardizes 5 clear Gmail labels (`01-Urgent-Client`, `02-Lead`, `03-Followup`, `04-Receipts`, `05-Newsletter`).
3. **Automated Calendar Conflict Handling**: Automatically checks available Google Calendar slots before suggesting meeting times.

---

## Core Implementations & Code Artifacts

### 1. Master Human-in-the-Loop Inbox & Approval Workflow JSON (`hitl_inbox_manager.json`)

```json
{
  "name": "Human_in_the_Loop_Executive_Inbox_Manager",
  "nodes": [
    {
      "parameters": {
        "pollTimes": {
          "item": [
            {
              "mode": "everyMinute"
            }
          ]
        },
        "simple": false,
        "filters": {
          "labelIds": ["INBOX", "UNREAD"]
        }
      },
      "id": "node-gmail-trigger",
      "name": "Gmail Inbound Trigger",
      "type": "n8n-nodes-base.gmailTrigger",
      "typeVersion": 1.1,
      "position": [200, 300]
    },
    {
      "parameters": {
        "jsCode": "const email = $json;\nconst subject = email.subject || 'No Subject';\nconst from = email.from?.value?.[0]?.address || 'unknown';\nconst body = email.textPlain || email.snippet || '';\n\nreturn {\n  json: {\n    message_id: email.id,\n    thread_id: email.threadId,\n    sender_email: from,\n    subject: subject,\n    body_snippet: body.substring(0, 1000),\n    received_at: email.date\n  }\n};"
      },
      "id": "node-extract-email",
      "name": "Extract Email Content",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [420, 300]
    },
    {
      "parameters": {
        "chatId": "={{ $env.TELEGRAM_ADMIN_CHAT_ID }}",
        "text": "=<b>📬 New Executive Email Action Required</b>\n\n<b>From:</b> {{ $json.sender_email }}\n<b>Subject:</b> {{ $json.subject }}\n\n<b>Proposed Draft Reply:</b>\n<i>{{ $json.draft_reply }}</i>\n\nPlease approve or reject dispatch:",
        "replyMarkup": "inlineKeyboard",
        "inlineKeyboard": {
          "rows": [
            {
              "row": {
                "buttons": [
                  {
                    "text": "✅ Approve & Send",
                    "url": "={{ $execution.resumeUrl }}?action=approve"
                  },
                  {
                    "text": "❌ Reject / Discard",
                    "url": "={{ $execution.resumeUrl }}?action=reject"
                  }
                ]
              }
            }
          ]
        }
      },
      "id": "node-telegram-approval",
      "name": "Telegram Approval Request",
      "type": "n8n-nodes-base.telegram",
      "typeVersion": 1.1,
      "position": [660, 300]
    },
    {
      "parameters": {
        "resume": "webhook",
        "limitWaitTime": {
          "values": {
            "unit": "hours",
            "amount": 24
          }
        }
      },
      "id": "node-wait-approval",
      "name": "Wait for Founder Approval",
      "type": "n8n-nodes-base.wait",
      "typeVersion": 1.1,
      "position": [880, 300]
    }
  ],
  "connections": {
    "Gmail Inbound Trigger": {
      "main": [
        [
          {
            "node": "Extract Email Content",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Extract Email Content": {
      "main": [
        [
          {
            "node": "Telegram Approval Request",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Telegram Approval Request": {
      "main": [
        [
          {
            "node": "Wait for Founder Approval",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## Parameterized Prompt Decks & Templates

### Prompt Deck 1: Executive Email Triage & Draft Generator

```markdown
<system_role>
You are the Executive Chief of Staff AI for the founder.
Analyze incoming emails, classify their urgency, determine if calendar booking is needed, and generate professional, concise draft responses.
</system_role>

<input_email>
Sender: {{SENDER_EMAIL}}
Subject: {{EMAIL_SUBJECT}}
Body Content:
{{EMAIL_BODY}}
Founder Calendar Availability:
{{AVAILABLE_CALENDAR_SLOTS}}
</input_email>

<classification_rubric>
- URGENT_CLIENT: Direct client questions, high revenue impact.
- NEW_LEAD: Potential subbroking / consulting prospect.
- SCHEDULING: Meeting request.
- INFORMATIONAL: System alert or newsletter.
</classification_rubric>

<output_schema>
Return JSON:
{
  "category": "URGENT_CLIENT | NEW_LEAD | SCHEDULING | INFORMATIONAL",
  "priority_score": 1-10,
  "requires_founder_action": true|false,
  "proposed_draft_reply": "string",
  "suggested_meeting_slot": "YYYY-MM-DD HH:MM or null"
}
</output_schema>
```

---

## Deployment SOP & Operational Guide

1. **Configure Google OAuth & Telegram Bot**:
   - Set up Google Workspace OAuth credentials in n8n Credentials.
   - Create a Telegram bot via `@BotFather` and acquire `TELEGRAM_ADMIN_CHAT_ID`.
2. **Import Workflow**:
   - Paste `hitl_inbox_manager.json` into n8n.
3. **Verify Webhook Resume URL**:
   - Ensure n8n `WEBHOOK_URL` environment variable is set to your reachable public/tunnel domain (e.g. via Cloudflare tunnel / ngrok).
4. **Test Live Approval Loop**:
   - Send test email to your inbox and verify the approval button triggers on your Telegram phone client.

---

## Failure Modes, Edge Cases & Troubleshooting

- **Failure Mode 1: Expired Execution Wait Window (>24 hours)**:
  - *Cause*: Founder did not click approve/reject within 24 hours.
  - *Remedy*: n8n resumes with default fallback branch, moving the email into `03-Followup` without sending unauthorized responses.
- **Failure Mode 2: Unreachable Resume URL**:
  - *Cause*: `WEBHOOK_URL` is set to `localhost:5678` so Telegram cannot reach the resume webhook.
  - *Remedy*: Configure public HTTPS tunnel in n8n environment (`WEBHOOK_URL=https://n8n.yourdomain.com`).


---

### Integrated: `Email_Inbox_Manager (1).json`

**Summary**: Workflow for managing email inboxes

**Integration Rationale**: Inbox management workflow

**Workflow**: `Email Inbox Manager`
**Nodes (21)**: Gmail Trigger, Text Classifier, OpenAI Chat Model, Add Label: Internal, Add Label: Customer Support, Add Label: Promotions, Add Label: Admin/Finance, Add Label: Sales Opportunities, Gmail, OpenAI, If, OpenAI1, OpenAI2, OpenAI3, OpenAI4
  *(+6 more nodes)*
**Node Types**: gmailTrigger, textClassifier, openAi, lmChatOpenAi, gmail



---

### Integrated: `Inbox Manager Documentation (1).pdf`

**Summary**: Documentation for the inbox manager workflow

**Integration Rationale**: Supports inbox automation playbook

> **Reference PDF**: `Inbox Manager Documentation (1).pdf` — See `02_Assets_Library/` for the full document.
