# Executive Chief of Staff: Claude + ChatGPT Setup

One shared persona ("core prompt"), installed in both assistants so they behave identically.
Edit `core-prompt.md` once, then paste it into each platform.

## 1. Core prompt
See [core-prompt.md](core-prompt.md). Fill in the `[MY CONTEXT]` block first.

## 2. Install in Claude
| Where | How |
|---|---|
| **Claude.ai Project** (recommended) | Projects → New project → "Set custom instructions" → paste core prompt. Upload context files (bio, org chart, goals, writing samples). |
| **Profile preferences** | Settings → Profile → "What preferences should Claude consider" → paste a 5-line summary of the core prompt. |
| **Claude Code** | Save the core prompt as `CLAUDE.md` in your working folder. |
| **Connectors** | Settings → Connectors: Gmail, Google Calendar, Google Drive (start read-only). |
| **Recurring work** | Use scheduled tasks for a daily brief and a Friday weekly review. |

## 3. Install in ChatGPT
| Where | How |
|---|---|
| **Custom GPT** (recommended) | Explore GPTs → Create → Instructions → paste core prompt. Upload the same context files under Knowledge. |
| **Custom Instructions** | Settings → Personalization → paste the core prompt (split across the two boxes if over the limit). |
| **Connectors** | Settings → Connectors: Gmail, Google Calendar, Google Drive (read-only first). |
| **Recurring work** | Use Tasks for a 7:30 AM daily brief and a Friday review. |

## 4. Keep them in sync
- Single source of truth: `core-prompt.md` in this repo. Update it, then re-paste into both.
- Use a shared "Context pack" folder in Google Drive (goals, key people, style guide, voice samples) and give both assistants access to it.
- Split the work: **Claude** for connected actions (inbox, calendar, Drive, documents). **ChatGPT** for second opinions, brainstorming, and drafting.
- Use the same starter commands in both: `Morning brief`, `Triage inbox`, `Prep me for [meeting]`, `Weekly review`, `Decision memo on [X]`.

## 5. Safety rules (both)
- Draft only. Nothing is sent, booked, paid, or deleted without explicit approval.
- Start connectors read-only; grant write access only when trust is earned.
- Don't paste passwords, banking details, or highly sensitive data.
- Neither assistant can operate your iMac on its own. Anything beyond its connectors needs a separate tool.
