# PRD: Jamia Tool — Discord Bot for Family Savings Association

## Problem Statement

The admin of a family Jamia manually enters every Payment and Distribution into a Google Sheet. This involves opening the sheet, finding the right row, and typing multiple fields for each transaction. Because the process is tedious, the admin sometimes forgets to log entries, resulting in missing or inaccurate financial records for the family.

## Solution

A Discord bot that the admin interacts with through guided tap-through flows (select menus and buttons). The admin triggers a command, selects options from menus, and the bot writes the correct data directly into the Google Sheet. No manual sheet editing required for routine operations.

Family Members continue to view the Google Sheet as before — the bot writes behind the scenes via the Google Sheets API.

## User Stories

1. As the admin, I want to trigger a payment recording flow from Discord, so that I don't have to open Google Sheets manually.
2. As the admin, I want to select a Member from a dropdown list when recording a Payment, so that I never mistype an Arabic name.
3. As the admin, I want to select the month a Payment covers from a list, so that I don't have to remember the date format.
4. As the admin, I want the Payment date to default to today, so that I can confirm it in one tap for same-day entries.
5. As the admin, I want to enter a custom date when a Member paid on a different day, so that the record is accurate.
6. As the admin, I want the Payment amount to be calculated automatically from the Member's Share count, so that I never enter a wrong amount.
7. As the admin, I want the transfer type to default to "تحويل", so that I don't have to select it every time.
8. As the admin, I want to see a confirmation message after a Payment is recorded, so that I know the Sheet was updated successfully.
9. As the admin, I want to trigger a distribution recording flow from Discord, so that I can log bi-monthly payouts without opening the Sheet.
10. As the admin, I want to select the recipient Member from a dropdown when recording a Distribution, so that I don't mistype their name.
11. As the admin, I want to select the Distribution Method (حجز or قرعة) from buttons, so that the record reflects how the recipient was chosen.
12. As the admin, I want the Distribution amount to default to 440 OMR, so that I don't have to type it for standard distributions.
13. As the admin, I want to edit a previously recorded Payment through a guided flow, so that I can correct mistakes without touching the Sheet directly.
14. As the admin, I want to edit a previously recorded Distribution through a guided flow, so that I can correct the beneficiary, amount, or method if needed.
15. As the admin, I want to select which field to edit from a list, so that I don't have to remember field names.
16. As the admin, I want to query a Member's Balance from Discord, so that I can answer family questions without opening the Sheet.
17. As the admin, I want the Balance query to show total amount paid (not net of Distributions), so that the figure is always positive and meaningful.
18. As the admin, I want all bot interactions to be private (ephemeral), so that the Discord channel doesn't get cluttered.
19. As the admin, I want the bot to be available at all times on my Android phone, so that I can log entries immediately when I receive a bank SMS.

## Implementation Decisions

### Module: SheetsClient
Wraps the Google Sheets API (via `gspread`). Exposes a clean interface that hides all column indices and sheet names. Other modules never touch the Sheets API directly.

Key operations:
- `get_members()` → list of Members with name, share count, monthly amount
- `write_payment(member, month, date, amount, transfer_type)` → finds the correct row by member + month, fills date, amount, transfer type
- `write_distribution(month, member, amount, method)` → finds the correct row in the Distributions sheet, fills all fields and marks received
- `update_payment_field(member, month, field, value)` → edits a single field in a Payment row
- `update_distribution_field(month, field, value)` → edits a single field in a Distribution row
- `get_balance(member)` → returns total paid by member

Row lookup for Payments uses member name + month (members appear in fixed order each month, so the row ID is deterministic).

Authentication uses a Google Service Account with a credentials JSON file. The Sheet ID is read from an environment variable.

### Module: MemberRegistry
Reads and caches the Members sheet at bot startup. Provides the Member list to all flows for building select menus. Refreshes on demand if a member is not found.

### Module: FlowEngine
Manages multi-step Discord interaction state. Each command (pay, distribute, edit, balance) is a Flow — a sequence of steps. The engine tracks which step the admin is on and what data has been collected so far, keyed by Discord user ID.

State is held in memory (not persisted). If the bot restarts mid-flow, the flow is abandoned silently.

### Flows
One flow class per command:
- **PayFlow** — steps: select Member → select Month → confirm/enter Date → write Payment
- **DistributeFlow** — steps: select Member → select Month → select Distribution Method → write Distribution
- **EditFlow** — steps: select record type → select Member → select Month → select field → enter new value → write update
- **BalanceFlow** — steps: select Member → display Balance

### Discord Bot
Registers four slash commands: `/pay`, `/distribute`, `/edit`, `/balance`. All interactions are ephemeral (visible only to the admin). Entry point delegates immediately to FlowEngine.

### Infrastructure
- Language: Python 3.11+
- Libraries: `discord.py`, `gspread`, `google-auth`
- Hosting: Render free tier (may sleep after inactivity; acceptable for single-admin use)
- Config: environment variables for `DISCORD_TOKEN`, `GOOGLE_SHEET_ID`, `GOOGLE_CREDENTIALS_JSON`

### Month Select Menu
Displays a rolling window of months: 3 months back, current month, and 3 months forward. This keeps the menu short regardless of how long the Jamia has been running.

## Testing Decisions

Good tests verify external behavior (what the bot writes to the Sheet and what it replies to Discord), not internal implementation steps.

**SheetsClient** is the highest-value module to test: mock the `gspread` API and assert that the correct cells are written for each operation. This catches column-index bugs early without needing a real Sheet.

**FlowEngine** state transitions can be tested by simulating a sequence of Discord interaction callbacks and asserting the final state and Sheet writes.

No tests for the Discord Bot entry point — it is thin glue code.

## Out of Scope

- Lottery / draw logic for selecting Distribution recipients
- Notifications or reminders to Members when a Payment is late
- Member onboarding (adding/removing Members from the bot)
- Multi-admin access
- Audit log or history view inside Discord
- Mobile app or web UI

## Further Notes

- The Google Sheets structure (column order, sheet names) must remain stable. Any restructuring of the Sheet requires a corresponding update to SheetsClient.
- Discord select menus support a maximum of 25 options. The current 9-Member count is well within this limit.
- The Render free tier spins the bot down after inactivity. The first interaction after a sleep period may take 30–60 seconds to respond. This is acceptable for single-admin use.
- Google Service Account credentials must never be committed to version control. Use environment variables or Render's secret management.
