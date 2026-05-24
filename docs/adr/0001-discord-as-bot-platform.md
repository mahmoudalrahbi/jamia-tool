# ADR 0001: Discord as the Bot Platform

## Status
Accepted

## Context
The admin needs a messaging interface to send commands to the bot from a mobile device. Telegram is the most common choice for bot development in the region due to its free API and wide adoption. However, Telegram is officially banned in Oman and requires a VPN to access, making it unreliable for daily use.

WhatsApp was considered but requires paid third-party APIs or unofficial workarounds. A custom web app was also considered but adds friction (requires opening a browser manually each time).

## Decision
Use Discord as the bot platform. Discord has a free, well-documented bot API, works without restrictions in Oman, and supports slash commands natively. The bot is admin-only, so Discord's lower regional adoption compared to Telegram is not a concern.

## Consequences
- The admin must have Discord installed on their Android device.
- Family members do not interact with the bot — they view data via Google Sheets.
- Migrating to another platform later would require rewriting the command interface.
