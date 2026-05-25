# Jamia Tool

A Discord bot for managing a family savings group (جمعية), integrated with Google Sheets for transparent record-keeping.

## Features

- **Member management** — add, edit, and remove members
- **Payment tracking** — record monthly contributions with confirmation prompts
- **Distribution** — manage payout turns and record distributions
- **Summaries** — instant balance and status reports via Discord commands
- **Google Sheets sync** — all data stored and readable in a shared spreadsheet

## Requirements

- Python 3.10+
- A Discord bot token
- A Google Cloud service account with Sheets API access
- A Google Spreadsheet shared with the service account

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/mahmoudalrahbi/jamia-tool.git
   cd jamia-tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Add credentials:
   - Place your Google service account key at `credentials.json`
   - Create a `.env` file with:
     ```
     DISCORD_TOKEN=your_discord_bot_token
     SPREADSHEET_ID=your_google_sheet_id
     ```

4. Run the bot:
   ```bash
   python main.py
   ```

## Usage

All commands are slash commands in Discord:

| Command | Description |
|---|---|
| `/pay` | Record a member's payment |
| `/distribute` | Record a distribution to a member |
| `/edit` | Edit an existing transaction |
| `/summary` | View current balances and status |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

To report a vulnerability, see [SECURITY.md](SECURITY.md).

## License

MIT License — see [LICENSE](LICENSE).
