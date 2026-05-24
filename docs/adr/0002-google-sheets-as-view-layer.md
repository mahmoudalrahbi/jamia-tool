# ADR 0002: Google Sheets as the View Layer

## Status
Accepted

## Context
The Jamia data needs to be visible to all family Members at any time, without requiring them to install or learn a new tool. The admin already maintains a Google Sheet with formulas that calculate balances, payment counts, and distribution totals automatically.

Replacing Google Sheets entirely with a dedicated database and UI would require building a read interface for all Members and migrating existing formula logic.

## Decision
Keep Google Sheets as the primary view layer for all Members. The bot writes raw data (Payments and Distributions) to the Sheet via the Google Sheets API using a Service Account. Existing formulas in the Sheet continue to handle all derived calculations (balance, totals, status).

The bot does not replicate or re-implement any formula logic — it only writes raw records.

## Consequences
- All Members can view live data with no new tools required.
- The bot depends on the Sheet's structure (column positions, sheet names). Restructuring the Sheet requires updating the bot.
- A Google Cloud Service Account must be set up once and its credentials kept secure.
- The bot's write operations must match the exact format expected by existing formulas.
