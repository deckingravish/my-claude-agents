---
name: Daily Briefing
description: Generate a morning briefing with today's calendar events and unread emails
triggers:
  - give me my briefing
  - morning update
  - what's on today
  - daily digest
  - what do I have today
---

# Daily Briefing Skill

## Purpose
Generate a concise morning briefing covering today's calendar events and unread emails.

## Steps

1. **Fetch calendar events** — get all events for today using the Google Calendar tool
2. **Fetch emails** — get unread emails from the last 24 hours using Gmail
3. **Format and return** the briefing using the template below

## Output Format

Good morning, [name]! Here's your briefing for [Day, Date].

📅 TODAY'S AGENDA
──────────────────
- HH:MM – Event Title (duration)
[If no events: "No meetings today — clear schedule!"]

📬 EMAIL HIGHLIGHTS
────────────────────
- [Sender] | [Subject] — one-line summary
[If no unread emails: "Inbox is clear."]

⚠️  ACTION NEEDED
──────────────────
[List any emails flagged urgent or requesting a reply — max 3]

## Rules
- Keep each email summary to one line
- Do not list more than 8 emails — group the rest as "and X more"
- Always include all three sections even if empty
- Flag emails containing "urgent", "ASAP", "please reply", or "deadline"
- Do not include calendar events that have already passed