# Issue 006: /edit Flow

**Type:** AFK
**Status:** Ready

## What to build

Implement the `/edit` command end-to-end. The admin corrects a previously recorded Payment or Distribution without touching the Sheet directly.

**Edit Payment flow:**
1. Admin types `/edit`
2. Bot replies with record type buttons: **"دفعة (Payment)"** and **"توزيع (Distribution)"**
3. Admin selects "دفعة"
4. Bot replies with Member select menu
5. Admin selects a Member
6. Bot replies with Month select menu
7. Admin selects a Month
8. Bot replies with field select menu: **"التاريخ"**, **"المبلغ"**, **"نوع التحويل"**
9. Admin selects a field
10. Bot opens a modal for the new value
11. Bot calls `SheetsClient.update_payment_field()` and replies with confirmation

**Edit Distribution flow:**
1–3. Same as above, admin selects "توزيع"
4. Bot replies with Month select menu
5. Admin selects a Month
6. Bot replies with field select menu: **"المستفيد"**, **"المبلغ"**, **"طريقة التوزيع"**
7. Admin selects a field
8. Bot opens a modal (or button set for Distribution Method) for the new value
9. Bot calls `SheetsClient.update_distribution_field()` and replies with confirmation

## Acceptance criteria

- [ ] `/edit` slash command registered and functional
- [ ] Record type selection (Payment / Distribution) works correctly
- [ ] For Payment: Member → Month → field → new value flow completes and updates Sheet
- [ ] For Distribution: Month → field → new value flow completes and updates Sheet
- [ ] Field select menus show only the editable fields for each record type
- [ ] Distribution Method field uses buttons (حجز / قرعة) instead of a text modal
- [ ] Confirmation message shown after successful update
- [ ] All interactions are ephemeral

## Blocked by

- Issue 004: /pay Flow
- Issue 005: /distribute Flow
