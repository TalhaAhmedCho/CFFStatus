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

### Optional configuration

- `CF_ONLINE_THRESHOLD_SECONDS` (default: 300) controls how recent a handle must
  be to be considered online. You can set this as a repository variable in
  GitHub Actions.

## Local run

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
python3 scripts/cf_status.py
```
