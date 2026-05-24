# Issue 001: Infrastructure Setup

**Type:** HITL
**Status:** Ready

## What to build

Set up all external services required before any code can run:

1. **Google Cloud** — create a project, enable the Google Sheets API, create a Service Account, download credentials JSON, and share the Jamia Google Sheet with the Service Account email.
2. **Discord** — create a new application in the Discord Developer Portal, add a Bot, copy the bot token, and invite the bot to the admin's private Discord server with `applications.commands` and `Send Messages` permissions.
3. **Render** — create a new Web Service (free tier), connect it to the GitHub repo (to be created), and add the following environment variables: `DISCORD_TOKEN`, `GOOGLE_SHEET_ID`, `GOOGLE_CREDENTIALS_JSON`.
4. **GitHub repo** — initialise a git repository in the project folder and push to GitHub so Render can deploy from it.

This slice produces no code. It is complete when the admin can confirm all credentials are in hand and Render is connected to the repo.

## Acceptance criteria

- [ ] Google Service Account created and credentials JSON downloaded
- [ ] Jamia Google Sheet shared with the Service Account email (Editor access)
- [ ] Discord bot created, token copied, bot invited to admin's private server
- [ ] GitHub repo created and connected to Render
- [ ] Environment variables set in Render: `DISCORD_TOKEN`, `GOOGLE_SHEET_ID`, `GOOGLE_CREDENTIALS_JSON`

## Blocked by

None — can start immediately.
