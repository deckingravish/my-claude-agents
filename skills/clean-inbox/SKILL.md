---
name: Clean Inbox
description: Find and delete unwanted promotional and automated notification emails
triggers:
  - clean my inbox
  - delete unwanted emails
  - clear promotions
  - tidy my inbox
  - remove junk emails
---

# Clean Inbox Skill

## Purpose
Find and trash unwanted promotional/marketing emails and automated notifications.

## Steps

1. **Search for unwanted emails** using Gmail with these queries:
   - Promotions: category:promotions
   - Automated senders: noreply, marketing domains
   - Known senders to target: Temu, National Lottery, LinkedIn job alert confirmations

2. **List what was found** — show the user a summary:
   - How many emails matched
   - Which senders they are from
   - A few example subject lines

3. **Ask for confirmation** before trashing:
   "Found X emails to delete from these senders: [list]. Shall I move them all to Trash?"

4. **Move to Trash** only after the user says yes

## Rules
- ALWAYS show a summary and ask for confirmation before deleting anything
- Never delete emails from real people — only automated/marketing senders
- Never delete emails containing words like "invoice", "receipt", "order confirmation", "booking"
- Preserve anything from banks, government, or healthcare senders
- Tell the user how many emails were trashed when done