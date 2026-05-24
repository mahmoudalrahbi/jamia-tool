# Issue 003: /balance Flow

**Type:** AFK
**Status:** Ready

## What to build

Implement the `/balance` command end-to-end. This is the simplest flow and serves as the tracer bullet that validates the full pipeline: Discord slash command → select menu interaction → Google Sheets read → Discord reply.

Flow:
1. Admin types `/balance` in Discord
2. Bot replies with an ephemeral select menu listing all 9 Members (names from MemberRegistry)
3. Admin selects a Member
4. Bot calls `SheetsClient.get_balance(member)` and replies with the total paid amount

All interactions are ephemeral (visible only to the admin). The reply should be clear and human-readable, e.g.:
> **خالد** — إجمالي المدفوع: **560 ريال**

The FlowEngine is introduced in this slice to manage the two-step interaction (command → select → reply). Its state is held in memory keyed by Discord user ID.

## Acceptance criteria

- [ ] `/balance` slash command is registered and visible in the admin's Discord server
- [ ] Bot responds with an ephemeral Member select menu
- [ ] Selecting a Member returns the correct Balance in a readable Arabic message
- [ ] Interaction is ephemeral (not visible to other server members)
- [ ] FlowEngine correctly handles the two-step state for this flow

## Blocked by

- Issue 002: SheetsClient + MemberRegistry
