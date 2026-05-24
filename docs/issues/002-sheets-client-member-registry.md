# Issue 002: SheetsClient + MemberRegistry

**Type:** AFK
**Status:** Ready

## What to build

Build the two foundational modules that all flows depend on:

**SheetsClient** — wraps `gspread` and exposes a clean interface to the rest of the bot. Hides all column indices, sheet names, and API details. Key operations:
- `get_members()` → list of Members (name, share count, monthly amount)
- `write_payment(member, month, date, amount, transfer_type)` → finds the correct row by member + month, fills date, amount, transfer type
- `write_distribution(month, member, amount, method)` → finds and fills the correct Distribution row, marks received
- `update_payment_field(member, month, field, value)` → edits a single Payment field
- `update_distribution_field(month, field, value)` → edits a single Distribution field
- `get_balance(member)` → returns total amount paid by a Member

Row lookup for Payments uses member name + month. Members appear in fixed order each month, so the row ID is deterministic.

**MemberRegistry** — reads the Members sheet at startup via SheetsClient and caches the result. Provides the Member list to all flows for building Discord select menus. Exposes a `refresh()` method in case data changes.

Verifiable independently: a small script that calls `get_members()` and prints the result to the terminal, using real Sheet credentials.

## Acceptance criteria

- [ ] SheetsClient authenticates with the Google Service Account from environment variables
- [ ] `get_members()` returns all 9 Members with correct name, share count, and monthly amount
- [ ] `write_payment()` fills the correct row in the Payments sheet without touching formula-calculated columns
- [ ] `write_distribution()` fills the correct row in the Distributions sheet
- [ ] `get_balance()` returns the correct total paid for a given Member
- [ ] MemberRegistry caches Members at startup and exposes a refresh method
- [ ] SheetsClient has unit tests with mocked `gspread` calls asserting correct cell targets

## Blocked by

- Issue 001: Infrastructure Setup
