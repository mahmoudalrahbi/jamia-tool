# Issue 004: /pay Flow

**Type:** AFK
**Status:** Ready

## What to build

Implement the `/pay` command end-to-end. The admin records a monthly Payment for a Member without typing anything manually.

Flow:
1. Admin types `/pay`
2. Bot replies with ephemeral Member select menu (from MemberRegistry)
3. Admin selects a Member
4. Bot replies with a Month select menu — rolling window of current month ± 3 months (format: MM/YYYY)
5. Admin selects a Month
6. Bot replies with two buttons: **"اليوم (DD/MM/YYYY)"** and **"تاريخ آخر"**
7a. If "اليوم" → bot records Payment immediately
7b. If "تاريخ آخر" → bot opens a modal with a single date field (DD/MM/YYYY)
8. Bot calls `SheetsClient.write_payment()` with: member, month, date, amount (shares × 20), transfer type ("تحويل")
9. Bot replies with a confirmation message, e.g.:
   > ✓ تم تسجيل دفعة **محمود** لـ **05/2026** — **20 ريال** بتاريخ **21/05/2026**

Amount is derived automatically from the Member's share count — the admin never types it.

## Acceptance criteria

- [ ] `/pay` slash command registered and functional
- [ ] Member select menu populated from MemberRegistry
- [ ] Month select menu shows a rolling window of ± 3 months from today
- [ ] "اليوم" button uses today's date in DD/MM/YYYY format
- [ ] "تاريخ آخر" opens a Discord modal for date entry
- [ ] Amount is calculated as Member's shares × 20 OMR (never typed by admin)
- [ ] Transfer type is written as "تحويل" in the Sheet
- [ ] Correct row is found and filled in the Payments sheet without touching formula columns
- [ ] Confirmation message shown after successful write
- [ ] All interactions are ephemeral

## Blocked by

- Issue 002: SheetsClient + MemberRegistry
