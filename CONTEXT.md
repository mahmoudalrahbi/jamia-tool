# Jamia Tool — Domain Glossary

## Jamia
A family savings association managed by a single admin. Members contribute fixed monthly amounts per Share. Every two months, the accumulated pool is distributed to one Member via lottery.

## Member
A person participating in a Jamia. A Member may hold one or more Shares. Members are identified by their Arabic name as registered in the Google Sheet.

## Payment
A monthly transfer made by a Member for one Share. A Payment records the Member name, amount (20 OMR), and the month it covers.

## Distribution
The bi-monthly payout of the accumulated pool to one Member. A Distribution records the recipient Member, the amount, the distribution method, and whether it has been received.

## Distribution Method
How the recipient of a Distribution was selected. Two values:
- **حجز** — the Member reserved their turn in advance before the lottery.
- **قرعة** — the Member was selected randomly by lottery.

## Balance
The total amount a Member has paid into the Jamia (sum of their Payments). Does not subtract Distributions received.

## Commands
Bot commands issued by the admin only via Discord. All commands use interactive components (select menus, buttons, modals) — no free-text format required.

- `/pay` — guided flow: select Member → select Month → confirm or enter Date → bot writes Payment.
- `/distribute` — guided flow: select Member → select Month → select Distribution Method → bot writes Distribution.
- `/edit` — guided flow: select record type (Payment/Distribution) → select record → select field → enter new value.
- `/balance` — guided flow: select Member → bot replies with total paid.

## Share
The unit of participation in a Jamia. One Share costs 20 OMR per month. A Member may hold more than one Share. Payments and distributions are tracked per Share.

