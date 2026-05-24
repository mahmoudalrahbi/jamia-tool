# ADR 0004: Interactive Discord Components Over Text Commands

## Status
Accepted

## Context
The bot needs to be quick and error-free for daily use on a mobile device. A text command format (e.g., `/pay أحمد 05/2026 24/05/2026`) requires the admin to remember the exact syntax and type Arabic names correctly every time. Typos or wrong formats cause failures and add friction.

Discord supports interactive UI components: select menus (dropdowns), buttons, and modals (pop-up forms). These can guide the admin through each operation step-by-step with tappable options.

## Decision
All four operations (Pay, Distribute, Edit, Balance) are implemented as guided interactive flows using Discord select menus and buttons. Free-text input is only used where unavoidable (e.g., entering a custom date). Member names are always chosen from a select menu, eliminating Arabic typing errors.

## Consequences
- Significantly less friction for daily mobile use — no syntax to remember.
- Implementation is more complex than plain slash commands (requires handling interaction callbacks and maintaining ephemeral state between steps).
- Discord select menus support a maximum of 25 options per menu — well within the current 9-Member limit.
- If the number of months to display grows large, the month select menu will need pagination or a default window (e.g., current month ± 3).
