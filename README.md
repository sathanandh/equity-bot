\# 🚀 Equity Bot — Multi-Provider LLM Analysis



> Automated equity research analysis using free-tier LLM providers, scheduled via GitHub Actions.



\[!\[GitHub Actions](https://img.shields.io/badge/GitHub\_Actions-Enabled-2088FF?logo=githubactions)](https://github.com/features/actions)

\[!\[Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org)

\[!\[License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)



---



\## 📋 Table of Contents



\- \[✨ Features](#-features)

\- \[🏗️ Architecture](#️-architecture)

\- \[📁 Repository Structure](#-repository-structure)

\- \[⚙️ Quick Setup](#️-quick-setup)

\- \[🔐 Secrets Configuration](#-secrets-configuration)

\- \[🧪 Testing](#-testing)

\- \[🕐 Cron Scheduling](#-cron-scheduling)

\- \[⚙️ Configuration Options](#️-configuration-options)

\- \[🛠️ Troubleshooting](#️-troubleshooting)

\- \[⚠️ Security Notice](#️-security-notice)

\- \[🤝 Contributing](#-contributing)

\- \[📄 License](#-license)

\- \[🔗 Resources](#-resources)



---



\## ✨ Features



\### 🤖 Core Capabilities

| Feature | Description |

|---------|-------------|

| \*\*Multi-Provider LLM Routing\*\* | Automatically routes requests across OpenRouter, NVIDIA NIM, Groq, and GitHub Models |

| \*\*Smart Fallback Logic\*\* | Skips broken/deprecated models, falls back to available providers on 404/429 errors |

| \*\*Free-Tier Optimized\*\* | Conservative defaults to respect rate limits and daily caps |

| \*\*Cumulative Knowledge Cache\*\* | Stores insights across runs for context-aware analysis |



\### 📥 Data Ingestion

| Feature | Description |

|---------|-------------|

| \*\*Telegram Channel Fetching\*\* | Monitors multiple channels for PDF/DOCX/XLSX/TXT reports |

| \*\*Smart File Prioritization\*\* | Scores files by keywords (`initiating`, `coverage`, `earnings`) + recency |

| \*\*PDF Text Extraction\*\* | Clean extraction with noise removal (page numbers, URLs, whitespace) |

| \*\*Chunked Processing\*\* | Splits large documents to fit model context windows |



\### 🧠 Analysis Engine

| Feature | Description |

|---------|-------------|

| \*\*God-Mode Prompt Framework\*\* | Structured output: thesis, facts, context, first-principles, risks, actionable insights |

| \*\*Insight Tagging\*\* | Labels claims as `\[DATA]`, `\[LOGIC]`, `\[OPINION]`, or `\[EXTRAPOLATION]` |

| \*\*Confidence Scoring\*\* | Model outputs conviction levels (H/M/L) + falsification tests |

| \*\*Chunk Synthesis\*\* | Combines multi-part analyses into coherent final reports |



\### 📤 Output \& Delivery

| Feature | Description |

|---------|-------------|

| \*\*Telegram Formatting\*\* | Markdown-optimized output with emoji headers, part splitting for long messages |

| \*\*Google Drive Backup\*\* | Saves full analysis reports to specified Drive folder |

| \*\*Provider Attribution\*\* | Tags output with which model/provider generated the analysis |

| \*\*Usage Tracking\*\* | Logs request counts and errors per provider for monitoring |



\### ⚙️ Operational

| Feature | Description |

|---------|-------------|

| \*\*GitHub Actions Cron\*\* | Scheduled runs at configurable intervals (default: 9 AM \& 6 PM UTC) |

| \*\*Manual Trigger Support\*\* | Test runs via `workflow\_dispatch` with debug mode option |

| \*\*Environment-Aware\*\* | Auto-adjusts settings for GitHub Actions vs local testing |

| \*\*Graceful Error Handling\*\* | Continues processing on partial failures, logs artifacts for debugging |



---



\## 🏗️ Architecture



```

┌─────────────────────────────────────────────────────┐

│                 GitHub Actions Runner                │

│  (ubuntu-latest, Python 3.11, 2-core, 7GB RAM)      │

└─────────────────┬───────────────────────────────────┘

&nbsp;                 │

&nbsp;   ┌─────────────▼─────────────┐

&nbsp;   │   Workflow: equity-bot.yml │

&nbsp;   │  • Cron trigger / Manual   │

&nbsp;   │  • Install deps            │

&nbsp;   │  • Inject secrets → env    │

&nbsp;   │  • Execute: python src/   │

&nbsp;   └─────────────┬─────────────┘

&nbsp;                 │

&nbsp;   ┌─────────────▼─────────────┐

&nbsp;   │      Python Bot:          │

&nbsp;   │    src/equity\_bot.py      │

&nbsp;   ├───────────────────────────┤

&nbsp;   │ • config.py               │

&nbsp;   │   - Channel IDs           │

&nbsp;   │   - Analysis settings     │

&nbsp;   │ • utils/                  │

&nbsp;   │   - pdf\_extractor.py      │

&nbsp;   │   - telegram\_client.py    │

&nbsp;   │ • Router + Analyzer       │

&nbsp;   │   - Multi-provider logic  │

&nbsp;   │   - Rate limit handling   │

&nbsp;   └─────────────┬─────────────┘

&nbsp;                 │

&nbsp;   ┌─────────────▼─────────────┐

&nbsp;   │        External APIs      │

&nbsp;   ├───────────────────────────┤

&nbsp;   │ • Telegram API (fetch)    │

&nbsp;   │ • OpenRouter / NVIDIA /   │

&nbsp;   │   Groq / GitHub (LLM)     │

&nbsp;   │ • Google Drive API (save) │

&nbsp;   └───────────────────────────┘

```



---



\## 📁 Repository Structure



```

equity-bot/

├── .github/

│   └── workflows/

│       └── equity-bot.yml          # 🕐 Cron scheduler + runner config

├── src/

│   ├── equity\_bot.py               # 🤖 Main bot entry point

│   ├── config.py                   # ⚙️ Channel IDs + analysis settings

│   ├── requirements.txt            # 📦 Python dependencies

│   └── utils/

│       ├── pdf\_extractor.py        # 📄 PDF text extraction + chunking

│       └── telegram\_client.py      # 📱 Telegram fetch/send client

├── .gitignore                      # 🔐 Exclude secrets, caches, artifacts

├── secrets\_example.env             # 📝 Local testing template (DO NOT COMMIT)

├── README.md                       # 📖 This file

└── LICENSE                         # 📄 MIT License

```



---



\## ⚙️ Quick Setup



\### 1️⃣ Fork/Clone Repository

```bash

git clone https://github.com/YOUR\_USERNAME/equity-bot.git

cd equity-bot

```



\### 2️⃣ Add GitHub Secrets (MANDATORY)



Go to your repo → \*\*Settings\*\* → \*\*Secrets and variables\*\* → \*\*Actions\*\* → \*\*New repository secret\*\*



| Secret Name | Description | Example Format |

|------------|-------------|---------------|

| `OPENROUTER\_API\_KEY` | OpenRouter API key | `sk-or-v1-abc123...` |

| `NVIDIA\_API\_KEY` | NVIDIA NIM API key | `nvapi-abc123...` |

| `GROQ\_KEY` | Groq API key | `gsk\_abc123...` |

| `TELEGRAM\_STRING\_SESSION` | Telethon session string | `1BVtsOH4...` |

| `TELEGRAM\_API\_ID` | Telegram API ID | `12345678` |

| `TELEGRAM\_API\_HASH` | Telegram API hash | `abc123def456...` |

| `GOOGLE\_SERVICE\_ACCOUNT\_JSON` | Google Drive service account (entire JSON) | `{"type":"service\_account",...}` |

| `DRIVE\_FOLDER\_ID` | Target Google Drive folder ID | `1AbCdEfGhIjKlMnOpQrStUvWxYz` |



> 💡 \*\*Getting Google Service Account JSON\*\*:

> 1. Go to \[Google Cloud Console](https://console.cloud.google.com)

> 2. Create project → Enable \*\*Google Drive API\*\*

> 3. IAM \& Admin → Service Accounts → Create Service Account

> 4. Generate JSON key → Copy \*\*entire content\*\* (including `{}`)

> 5. Share your Drive folder with the service account email (`xxx@xxx.iam.gserviceaccount.com`)



\### 3️⃣ Configure Channels (Optional)



Edit `src/config.py` to add/remove source channels:



```python

SOURCE\_CHANNELS = \[

&nbsp;   {"id": -1001588470529, "name": "Channel Alpha"},

&nbsp;   {"id": -1003025504126, "name": "Equity Research Reports"},

&nbsp;   # Add more: {"id": -100xxxxxxxxx, "name": "Another Channel"},

]

OUTPUT\_GROUP\_ID = -5205208069  # Where to send analysis

```



\### 4️⃣ Commit \& Push

```bash

git add .

git commit -m "🚀 Initial setup: config + secrets"

git push origin main

```



---



\## 🔐 Secrets Configuration



\### GitHub Secrets (Production)

✅ Stored securely in GitHub, injected as environment variables at runtime  

✅ Never committed to repository  

✅ Accessible only to workflow runs  



\### Local Testing (Optional)

```bash

\# 1. Copy template

cp secrets\_example.env .env



\# 2. Edit .env with your NEW (non-compromised) keys

nano .env  # or use your preferred editor



\# 3. Add .env to .gitignore (already included)

\# 4. Test locally:

cd src

python equity\_bot.py

```



> ⚠️ \*\*Never commit `.env` or `secrets\_example.env` with real values\*\*



---



\## 🧪 Testing



\### Manual Trigger (Recommended First Step)

1\. Go to your repo → \*\*Actions\*\* tab

2\. Select \*\*"🚀 Equity Bot - Scheduled Analysis"\*\*

3\. Click \*\*"Run workflow"\*\* → \*\*"Run workflow"\*\* (green button)

4\. Optional: Enable `debug\_mode: true` for verbose logging

5\. Monitor live logs for progress/errors



\### Expected Output (Success)

```

🚀 Starting Equity Bot at 2026-03-08T09:00:00Z

🔄 Router initialized: \['openrouter', 'nvidia', 'groq']

📥 STEP 1: Fetching files (last 50 hours)...

📺 Equity Research Reports (ID: -1003025504126)

✅ Connected: Equity Research Reports

📎 \[14:09] Report\_TSLA\_Q4.pdf (2.4 MB)

✅ Equity Research Reports: 4 files

📊 Found 4 files

📊 STEP 2: Selecting top 2 files...

&nbsp;  1. \[Equity Research Reports] Report\_TSLA\_Q4.pdf (2.4 MB)

&nbsp;  2. \[Equity Research Reports] Update\_IT\_Sector.pdf (1.1 MB)

📄 STEP 3: Extracting text...

&nbsp;  ✅ Report\_TSLA\_Q4.pdf: 21,238 chars

&nbsp;  ✅ Update\_IT\_Sector.pdf: 18,710 chars

🧠 STEP 4: Analyzing documents...

🎯 openrouter → google/gemma-2-9b-it:free

✅ Success (2,841 chars)

📤 SENDING OUTPUT

📤 Sending to Telegram group -5205208069...

📤 Part 1/1

💾 Uploaded: https://drive.google.com/file/d/xxx/view

✅ PIPELINE COMPLETE

📊 Results: 2/2 files analyzed

🔄 Provider usage: {'openrouter': {'requests': 2, 'errors': 0}}

⏱️ Runtime: 127.3 seconds

```



\### Verify Outputs

| Destination | How to Check |

|------------|-------------|

| \*\*Telegram Group\*\* | Open group → Look for formatted analysis message |

| \*\*Google Drive\*\* | Open folder → Check for `Analysis\_\*.md` files |

| \*\*GitHub Actions Logs\*\* | Actions tab → Click run → View "Execute Equity Bot" step |

| \*\*Failed Run Artifacts\*\* | Actions tab → Failed run → "equity-bot-logs-XXX" artifact |



---



\## 🕐 Cron Scheduling



\### Default Schedule (UTC)

```yaml

schedule:

&nbsp; - cron: '0 9,18 \* \* \*'  # 9 AM and 6 PM UTC daily

```



\### Cron Syntax Reference

```

┌───────────── minute (0-59)

│ ┌───────────── hour (0-23)

│ │ ┌───────────── day of month (1-31)

│ │ │ ┌───────────── month (1-12)

│ │ │ │ ┌───────────── day of week (0-6, Sun=0)

│ │ │ │ │

\* \* \* \* \*

```



\### Common Schedules (UTC)

| Schedule | Cron Expression | Use Case |

|----------|----------------|----------|

| Every hour | `0 \* \* \* \*` | High-frequency monitoring (⚠️ may hit rate limits) |

| Every 6 hours | `0 \*/6 \* \* \*` | Balanced coverage |

| Twice daily | `0 9,18 \* \* \*` | ✅ Recommended default |

| Weekdays only | `0 9 \* \* 1-5` | Market-days analysis |

| Market hours (US) | `30 13 \* \* 1-5` | Post-market close (1:30 PM UTC = 9:30 AM ET) |



\### 🌍 Convert to Your Timezone

```bash

\# Example: Run at 9 AM IST (UTC+5:30) = 3:30 AM UTC

\# Cron: 30 3 \* \* \*



\# Example: Run at 6 PM EST (UTC-5) = 11 PM UTC  

\# Cron: 0 23 \* \* \*

```



> 💡 Use \[crontab.guru](https://crontab.guru) to validate \& convert schedules.



\### Disable Cron (Testing Only)

Comment out the `schedule` block:

```yaml

\# schedule:

\#   - cron: '0 9,18 \* \* \*'

```

Bot will only run via manual `workflow\_dispatch` trigger.



---



\## ⚙️ Configuration Options



Edit `src/config.py` to customize behavior:



\### 📺 Channel Settings

```python

SOURCE\_CHANNELS = \[  # Where to FETCH reports FROM

&nbsp;   {"id": -1001588470529, "name": "Channel Alpha"},

&nbsp;   {"id": -1003025504126, "name": "Equity Research Reports"},

]

OUTPUT\_GROUP\_ID = -5205208069  # Where to SEND analysis TO

```



\### ⏰ Fetch Settings

```python

HOURS\_AGO = 50                    # Lookback window for messages

MAX\_MESSAGES\_PER\_CHANNEL = 150    # Max messages to scan per channel

DOWNLOAD\_FILES = True             # Download attachments (set False for metadata-only)

VALID\_EXTENSIONS = \['.pdf', '.docx', '.xlsx', '.txt']  # File types to process

```



\### 🧠 Analysis Settings (Free-Tier Optimized)

```python

FILES\_TO\_ANALYZE = 2              # Max files to analyze per run (conservative)

MAX\_PAGES\_PER\_FILE = 5            # Max PDF pages to extract (reduces token usage)

CHUNK\_SIZE\_CHARS = 4000           # Text chunk size for large documents

ENABLE\_REASONING = False          # Skip heavy reasoning mode on scheduled runs

MAX\_RETRIES = 3                   # API call retry attempts

RATE\_LIMIT\_BACKOFF = 10           # Seconds to wait when rate limited

```



\### 💾 Storage Settings

```python

SAVE\_TO\_DRIVE = True              # Save outputs to Google Drive

DRIVE\_FOLDER\_ID = "1AbCd..."      # Target Drive folder ID

MAX\_KNOWLEDGE\_ENTRIES = 25        # Max cached insights to retain

```



\### 🔄 Auto-Adjust for GitHub Actions

```python

\# When RUNNING\_IN\_GITHUB = True, bot auto-applies:

FILES\_TO\_ANALYZE = min(FILES\_TO\_ANALYZE, 2)   # Cap at 2 for cron

MAX\_PAGES\_PER\_FILE = min(MAX\_PAGES\_PER\_FILE, 5)

ENABLE\_REASONING = False                       # Disable heavy reasoning

```



\### Override via Environment Variables (Optional)

Set these in GitHub Secrets or local `.env`:

```bash

HOURS\_AGO=24

FILES\_TO\_ANALYZE=1

MAX\_PAGES\_PER\_FILE=3

ENABLE\_REASONING=true

RATE\_LIMIT\_BACKOFF=15

```



---



\## 🛠️ Troubleshooting



\### 🔍 Common Errors \& Fixes



| Error | Likely Cause | Solution |

|-------|-------------|----------|

| `ModuleNotFoundError: No module named 'telethon'` | Missing dependency | Ensure `requirements.txt` is correct; check `pip install` step in logs |

| `Authentication failed for Telegram` | Invalid session/API credentials | Regenerate Telegram credentials; verify `TELEGRAM\_STRING\_SESSION` format |

| `google.auth.exceptions.DefaultCredentialsError` | Invalid service account JSON | Re-generate Google JSON key; ensure entire content (including `{}`) is in secret |

| `Drive permission denied` | Folder not shared with service account | Share Drive folder with service account email (`xxx@xxx.iam.gserviceaccount.com`) |

| `404 Model not found` | Deprecated model name | Update `build\_providers\_config()` in `equity\_bot.py` with current free models |

| `Rate limit exceeded (429)` | Too frequent requests | Increase cron interval; reduce `FILES\_TO\_ANALYZE`; check provider dashboards for caps |

| `Workflow timeout (180 min)` | Job exceeded time limit | Reduce `MAX\_PAGES\_PER\_FILE`; add early exits; optimize chunk size |

| `No files found` | Channels empty or ID mismatch | Verify channel IDs include `-100` prefix; check bot has access to channels |

| `Telegram message too long` | Output exceeds 4096 chars | Bot auto-splits messages; check `\_format\_output()` truncation logic |



\### 🧪 Debug Mode

Enable verbose logging via manual trigger:

1\. Actions → "🚀 Equity Bot" → \*\*Run workflow\*\*

2\. Check ✅ \*\*debug\_mode: true\*\*

3\. Run → View expanded logs for step-by-step output



\### 📤 View Logs \& Artifacts

\- \*\*Success logs\*\*: Actions tab → Select run → Expand "Execute Equity Bot" step

\- \*\*Failed runs\*\*: Actions tab → Failed run → Download "equity-bot-logs-XXX" artifact

\- \*\*Local logs\*\*: Check `/tmp/equity-bot/` on runner (uploaded as artifact on failure)



\### 🔄 Reset State (If Stuck)

```bash

\# 1. Clear cache (optional)

\#    Delete knowledge\_cache.json from your Drive folder or local /tmp/



\# 2. Revoke \& regenerate API keys (if auth issues persist)

\#    OpenRouter: https://openrouter.ai/keys

\#    NVIDIA: https://build.nvidia.com/profile

\#    Groq: https://console.groq.com/keys

\#    Telegram: https://my.telegram.org/auth



\# 3. Update GitHub Secrets with new keys



\# 4. Trigger manual test run

```



---



\## ⚠️ Security Notice



\### 🔐 Critical: Keys Shared in This Repository's History Are Compromised



If you previously hardcoded API keys in any committed file or chat:

1\. \*\*Revoke immediately\*\* at provider dashboards:

&nbsp;  - \[OpenRouter Keys](https://openrouter.ai/keys)

&nbsp;  - \[NVIDIA Profile](https://build.nvidia.com/profile)

&nbsp;  - \[Groq Keys](https://console.groq.com/keys)

&nbsp;  - \[Telegram Auth](https://my.telegram.org/auth)

2\. \*\*Generate new keys\*\* and add to GitHub Secrets (NOT code)

3\. \*\*Never commit\*\* `.env`, `secrets\*.env`, or hardcoded credentials



\### ✅ Security Best Practices

\- \[x] All credentials stored in GitHub Secrets (not code)

\- \[x] `.gitignore` excludes sensitive files (`.env`, `\*.log`, `cache/`)

\- \[x] Google Service Account has minimal `drive.file` scope

\- \[x] Telegram bot uses read-only channel access + targeted group send

\- \[ ] Rotate API keys quarterly (add calendar reminder)

\- \[ ] Monitor provider dashboards for unusual usage



\### 🚫 What NOT to Do

```bash

\# ❌ NEVER commit real credentials:

git add .env  # ← Don't do this

git commit -m "Add keys"  # ← Never



\# ❌ NEVER paste keys in issues, PRs, or public chats

\# ❌ NEVER use same keys for testing + production

```



---



\## 🤝 Contributing



Contributions welcome! Please follow these steps:



1\. \*\*Fork\*\* the repository

2\. \*\*Create a feature branch\*\*: `git checkout -b feat/your-feature`

3\. \*\*Make changes\*\* + add tests if applicable

4\. \*\*Run linting\*\* (optional but appreciated):

&nbsp;  ```bash

&nbsp;  pip install black flake8

&nbsp;  black src/

&nbsp;  flake8 src/

&nbsp;  ```

5\. \*\*Commit\*\* with clear message: `git commit -m "feat: add XYZ"`

6\. \*\*Push\*\* to your fork: `git push origin feat/your-feature`

7\. \*\*Open a Pull Request\*\* with description of changes



\### 🧪 Testing Contributions

\- Test locally with `.env` before submitting PR

\- Ensure workflow passes with manual trigger

\- Update `README.md` if adding new config options



\### 📝 Code Style

\- Follow \[PEP 8](https://peps.python.org/pep-0008/)

\- Use type hints for function signatures

\- Add docstrings for public functions/classes

\- Keep functions focused (<50 lines ideal)



---



\## 📄 License



Distributed under the \*\*MIT License\*\*. See `LICENSE` for details.



```

MIT License



Copyright (c) 2026 Equity Bot Contributors



Permission is hereby granted, free of charge, to any person obtaining a copy

of this software and associated documentation files (the "Software"), to deal

in the Software without restriction, including without limitation the rights

to use, copy, modify, merge, publish, distribute, sublicense, and/or sell

copies of the Software, and to permit persons to whom the Software is

furnished to do so, subject to the following conditions:



The above copyright notice and this permission notice shall be included in all

copies or substantial portions of the Software.



THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR

IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,

FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE

AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER

LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,

OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE

SOFTWARE.

```



---



\## 🔗 Resources



\### 📚 Documentation

| Resource | Link |

|----------|------|

| GitHub Actions Cron Syntax | https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule |

| GitHub Secrets Guide | https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions |

| Telethon Documentation | https://docs.telethon.dev |

| Google Drive API Quickstart | https://developers.google.com/drive/api/quickstart/python |

| OpenRouter Free Models | https://openrouter.ai/models?max\_price=0 |

| NVIDIA NIM Models | https://build.nvidia.com/explore/discover |

| Groq Models | https://console.groq.com/docs/models |



\### 🛠️ Tools

| Tool | Purpose | Link |

|------|---------|------|

| crontab.guru | Cron schedule tester \& converter | https://crontab.guru |

| Telegram @userbotix\_bot | Generate Telethon session string | https://t.me/userbotix\_bot |

| Google Cloud Console | Manage service accounts \& APIs | https://console.cloud.google.com |

| JSON Formatter | Validate service account JSON | https://jsonformatter.org |



\### 🆘 Support

\- 🐛 \*\*Bug Reports\*\*: Open an \[Issue](https://github.com/YOUR\_USERNAME/equity-bot/issues)

\- 💡 \*\*Feature Requests\*\*: Use \[Discussions](https://github.com/YOUR\_USERNAME/equity-bot/discussions)

\- ❓ \*\*Questions\*\*: Tag with `question` in Issues or start a Discussion



---



> ⚠️ \*\*Disclaimer\*\*: This bot uses free-tier API limits. Usage is subject to each provider's Terms of Service. The authors are not responsible for account suspensions, rate limit penalties, or data loss. Use at your own risk.



---



\*\*🚀 Ready to deploy?\*\*  

1\. Add your secrets to GitHub  

2\. Commit \& push  

3\. Trigger a manual test run  

4\. Enable cron after verification  



\*Happy analyzing!\* 📈🤖

