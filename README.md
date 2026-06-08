# my-claude-agents

A personal collection of Claude skills and agents — built to automate daily workflows using the Claude desktop app (Cowork mode).

## Repo Structure

my-claude-agents/
├── skills/
│   └── daily-briefing/
│       └── SKILL.md
└── agents/
    └── (coming soon)

## What's a Skill?

A skill is a markdown prompt file (SKILL.md) that teaches Claude how to handle a specific task. When installed, Claude automatically recognises trigger phrases and follows the instructions in the skill.

## What's an Agent?

An agent is a more complex workflow — often involving multiple tools, conditional logic, or multi-step automation. Agents are stored in the agents/ folder.

## Skills

| Skill | Trigger phrases | Description |
|-------|----------------|-------------|
| daily-briefing | "give me my briefing", "morning update", "what's on today" | Pulls today's calendar + unread emails into a clean digest |

## Roadmap

- [ ] Meeting prep
- [ ] Email triage
- [ ] Standup generator
- [ ] PR review agent