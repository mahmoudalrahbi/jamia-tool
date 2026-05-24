# ADR 0003: Balance Is Total Paid, Not Net of Distributions

## Status
Accepted

## Context
When the admin queries `/balance [name]`, two definitions are possible:
- **Gross balance:** total amount the Member has paid in (sum of Payments).
- **Net balance:** total paid minus total Distributions received.

The net balance would show how much a Member is "ahead" or "behind" financially. However, in a Jamia, receiving a Distribution is not a debt — it is the purpose of participation. Subtracting it from the balance would create a misleading negative figure for Members who have already received their payout.

## Decision
Balance is defined as the total amount a Member has paid into the Jamia (sum of their Payments only). Distributions received are not subtracted.

## Consequences
- The balance command gives a clear answer to "how much has this person paid so far?"
- To know how much a Member has received, the admin must check the Distribution sheet directly (or a future `/received` command could be added).
- This matches how the existing Google Sheet presents the data in the Members summary tab.
