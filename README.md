# CFFStatus

Automate Codeforces online/offline checks and post the latest status to Discord.

## Setup

### 1) Configure handles

You can supply handles either via an environment variable or the config file.

**Option A: GitHub Actions variable**

Create a repository variable named `CF_HANDLES` (comma-separated list):

- GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository variable**.
- Name: `CF_HANDLES`
- Value example: `tourist,Petr`

**Option B: Local environment variable**

```bash
export CF_HANDLES="tourist,Petr"
```

**Option C: Config file**

Edit `config/users.json` and provide a `handles` array:

```json
{
  "handles": ["tourist", "Petr"]
}
```

### 2) Configure the Discord webhook

Create a Discord webhook and store the URL as a repository secret named
`DISCORD_WEBHOOK_URL`.

- GitHub repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
- Name: `DISCORD_WEBHOOK_URL`
- Value: your webhook URL.

### 3) Adjust the schedule

The workflow is defined in `.github/workflows/cf-status.yml`. Change the cron
expression under `on.schedule` to adjust frequency. Example for every 15 minutes:

```yaml
on:
  schedule:
    - cron: "*/15 * * * *"
```

# CFFStatus

A small Python script that checks Codeforces user status (online/offline, rating, last seen) and posts a formatted update to a Discord webhook.

Main entrypoint: `status.py`

---

## What it does

- Fetches users via the Codeforces API (`user.info`)
- Determines **online/offline** using the `lastOnlineTimeSeconds` timestamp
- Posts a single formatted message to a Discord webhook

Online logic:

`(now - lastOnlineTimeSeconds) <= CF_ONLINE_THRESHOLD_SECONDS`

---

## Requirements

- Python 3.10+ (recommended)
- Internet access (Codeforces + Discord)

No third-party dependencies (standard library only).

---

## Quick Start (Local)

### 1) Configure handles (pick one)

**Option A: `users.json` file (recommended)**

Edit the repo-root `users.json`:

```json
{
  "handles": ["tourist", "Petr"]
}
```

**Option B: Environment variable `CF_HANDLES`**

Comma-separated list:

- Windows (CMD):
  ```bat
  set CF_HANDLES=tourist,Petr
  ```
- Windows (PowerShell):
  ```powershell
  $env:CF_HANDLES = "tourist,Petr"
  ```
- macOS/Linux (bash/zsh):
  ```bash
  export CF_HANDLES="tourist,Petr"
  ```

### 2) Configure the Discord webhook

The script reads `DISCORD_WEBHOOK`. For convenience/compatibility, `DISCORD_WEBHOOK_URL` also works.

- Windows (CMD):
  ```bat
  set DISCORD_WEBHOOK=https://discord.com/api/webhooks/...
  ```
- Windows (PowerShell):
  ```powershell
  $env:DISCORD_WEBHOOK = "https://discord.com/api/webhooks/..."
  ```
- macOS/Linux:
  ```bash
  export DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."
  ```

### 3) Run

```bash
python status.py
```

If successful, it prints something like:

`Posted status update for: tourist, Petr`

---

## Configuration

### Handles source (priority order)

`status.py` loads handles in this order:

1. `CF_HANDLES` env var (comma-separated)
2. `users.json` (repo root) `handles` array

### Online threshold

`CF_ONLINE_THRESHOLD_SECONDS` (default: `300`)

Example: set to 10 minutes:

- Windows (PowerShell):
  ```powershell
  $env:CF_ONLINE_THRESHOLD_SECONDS = "600"
  ```
- macOS/Linux:
  ```bash
  export CF_ONLINE_THRESHOLD_SECONDS=600
  ```

---

## Discord message format

The message contains:

- Title: **Codeforces Status Update**
- One line per handle:
  - handle
  - rating (if present)
  - Online/Offline
  - last seen (minutes ago)

---

## GitHub Actions (Optional)

You can run this on a schedule with GitHub Actions. This repository currently does not include a workflow, but you can add one.

1) Create `.github/workflows/cf-status.yml`

2) Add repository secrets/variables:

- Secret: `DISCORD_WEBHOOK` (or `DISCORD_WEBHOOK_URL`)
- Variable: `CF_HANDLES` (optional, if you don't want to commit `users.json`)
- Variable: `CF_ONLINE_THRESHOLD_SECONDS` (optional)

Example workflow:

```yaml
name: Codeforces Status

on:
  schedule:
    - cron: "*/15 * * * *" # every 15 minutes
  workflow_dispatch:

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Run status bot
        env:
          DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
          CF_HANDLES: ${{ vars.CF_HANDLES }}
          CF_ONLINE_THRESHOLD_SECONDS: ${{ vars.CF_ONLINE_THRESHOLD_SECONDS }}
        run: |
          python status.py
```

Note: adjust `secrets.DISCORD_WEBHOOK` to match your secret name.

---

## Troubleshooting

- **“No handles configured. Set CF_HANDLES or create users.json.”**
  - Create `users.json` with a non-empty `handles` list, or set `CF_HANDLES`.

- **“Invalid JSON in users.json”**
  - Ensure `users.json` is valid JSON (no trailing commas).

- **“DISCORD_WEBHOOK (or DISCORD_WEBHOOK_URL) is not set.”**
  - Set the webhook env var in your shell/session.

- **“Failed to reach Codeforces API …”**
  - Check internet access, firewall/proxy, or temporary API issues.

- **“Codeforces API error: …”**
  - Usually means invalid handles or an API-side error.

- **Discord message not posting**
  - Verify the webhook URL is correct and still active.
  - Confirm the webhook has permission to post in the channel.

---

## Security notes

- Treat the Discord webhook URL as a secret.
- Never commit webhook URLs into a public repository.
- In GitHub Actions, store it as a **Secret**, not a variable.

---

## License

No license file is included yet.
