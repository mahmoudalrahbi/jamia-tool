# Issue 005: /distribute Flow

**Type:** AFK
**Status:** Ready

## What to build

Implement the `/distribute` command end-to-end. The admin records a bi-monthly Distribution payout to a Member.

Flow:
1. Admin types `/distribute`
2. Bot replies with ephemeral Member select menu (recipient of this Distribution)
3. Admin selects a Member
4. Bot replies with a Month select menu — rolling window of current month ± 3 months (format: MM/YYYY)
5. Admin selects the distribution Month
6. Bot replies with two buttons for Distribution Method: **"حجز"** and **"قرعة"**
7. Admin selects the method
8. Bot calls `SheetsClient.write_distribution()` with: month, member, amount (440 OMR default), method
9. Bot replies with confirmation, e.g.:
   > ✓ تم تسجيل توزيع **05/2026** — المستفيد: **حنان** — **440 ريال** (حجز)

The Distribution row is pre-existing in the Sheet (months are pre-filled). The bot finds the row by month and fills: beneficiary, amount, distribution method, and marks "تم الاستلام" as true.

## Acceptance criteria

- [ ] `/distribute` slash command registered and functional
- [ ] Member select menu populated from MemberRegistry
- [ ] Month select menu shows rolling window of ± 3 months from today
- [ ] Distribution Method buttons show "حجز" and "قرعة"
- [ ] Amount defaults to 440 OMR
- [ ] Correct Distribution row found by month and filled in the Distributions sheet
- [ ] "تم الاستلام" checkbox marked as received after write
- [ ] Confirmation message shown after successful write
- [ ] All interactions are ephemeral

## Blocked by

- Issue 002: SheetsClient + MemberRegistry
