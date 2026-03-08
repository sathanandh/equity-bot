# src/config.py
# ════════════════════════════════════════════════════════════════════════════
# ⚙️ Bot Configuration - Channel IDs, Limits, Settings
# ════════════════════════════════════════════════════════════════════════════

import os
from pathlib import Path
from datetime import timedelta

# ════════════════════════════════════════════════════════════════════════════
# 📺 Telegram Channel Configuration (YOUR IDs)
# ════════════════════════════════════════════════════════════════════════════

# 📥 Source Channels: Where to FETCH reports FROM
SOURCE_CHANNELS = [
    {
        "id": -1001588470529,      # ← Your Channel Alpha ID
        "name": "Channel Alpha",    # ← Friendly name for logging
    },
    {
        "id": -1003025504126,      # ← Your Equity Research Reports ID
        "name": "Equity Research Reports",
    },
    # ➕ Add more channels here as needed:
    # {"id": -100xxxxxxxxx, "name": "Another Channel"},
]

# 📤 Output Group: Where to SEND analysis TO
OUTPUT_GROUP_ID = -5205208069  # ← Your target group ID


# ════════════════════════════════════════════════════════════════════════════
# ⏰ Fetch Settings
# ════════════════════════════════════════════════════════════════════════════

# Lookback window: Fetch messages from last N hours
HOURS_AGO = int(os.getenv("HOURS_AGO", "50"))

# Max messages to scan per channel (prevents runaway API calls)
MAX_MESSAGES_PER_CHANNEL = int(os.getenv("MAX_MESSAGES_PER_CHANNEL", "150"))

# Enable file downloads (set False to only fetch metadata)
DOWNLOAD_FILES = os.getenv("DOWNLOAD_FILES", "true").lower() == "true"

# Valid file extensions to process
VALID_EXTENSIONS = [".pdf", ".docx", ".xlsx", ".txt"]


# ════════════════════════════════════════════════════════════════════════════
# 🧠 Analysis Settings (Free-Tier Optimized)
# ════════════════════════════════════════════════════════════════════════════

# Max files to analyze per run (conservative for free tiers)
FILES_TO_ANALYZE = int(os.getenv("FILES_TO_ANALYZE", "2"))

# Max pages to extract per PDF (reduces token usage)
MAX_PAGES_PER_FILE = int(os.getenv("MAX_PAGES_PER_FILE", "5"))

# Text chunk size for large documents (chars)
CHUNK_SIZE_CHARS = int(os.getenv("CHUNK_SIZE_CHARS", "4000"))

# Enable reasoning mode (uses more tokens, slower)
ENABLE_REASONING = os.getenv("ENABLE_REASONING", "false").lower() == "true"

# Max retry attempts per API call
MAX_RETRIES = 3

# Backoff seconds when rate limited
RATE_LIMIT_BACKOFF = int(os.getenv("RATE_LIMIT_BACKOFF", "10"))


# ════════════════════════════════════════════════════════════════════════════
# 💾 Storage & Cache Settings
# ════════════════════════════════════════════════════════════════════════════

# Save analysis outputs to Google Drive
SAVE_TO_DRIVE = os.getenv("SAVE_TO_DRIVE", "true").lower() == "true"

# Target Drive folder ID (from URL: drive.google.com/drive/folders/XXX)
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "")

# Local cache file path (for knowledge accumulation)
CACHE_DIR = Path(os.getenv("CACHE_DIR", "/tmp/equity-bot/cache"))
KNOWLEDGE_CACHE_FILE = CACHE_DIR / "knowledge_cache.json"
MAX_KNOWLEDGE_ENTRIES = int(os.getenv("MAX_KNOWLEDGE_ENTRIES", "25"))

# Local download directory for fetched files
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "/tmp/equity-bot/downloads"))


# ════════════════════════════════════════════════════════════════════════════
# 🔄 Runtime Mode Detection
# ════════════════════════════════════════════════════════════════════════════

# Detect if running in GitHub Actions vs local
RUNNING_IN_GITHUB = os.getenv("GITHUB_ACTIONS", "false").lower() == "true"

# Auto-adjust settings for GitHub Actions (conservative)
if RUNNING_IN_GITHUB:
    FILES_TO_ANALYZE = min(FILES_TO_ANALYZE, 2)  # Cap at 2 for cron runs
    MAX_PAGES_PER_FILE = min(MAX_PAGES_PER_FILE, 5)
    ENABLE_REASONING = False  # Disable heavy reasoning on scheduled runs
    print(f"🔧 GitHub Actions mode: conservative settings applied")


# ════════════════════════════════════════════════════════════════════════════
# 📋 Validation Helper
# ════════════════════════════════════════════════════════════════════════════

def validate_config():
    """Check required config values at startup"""
    errors = []
    
    if not SOURCE_CHANNELS:
        errors.append("SOURCE_CHANNELS is empty — add at least one channel ID")
    
    for ch in SOURCE_CHANNELS:
        if not isinstance(ch.get("id"), int):
            errors.append(f"Channel ID must be integer: {ch}")
    
    if not isinstance(OUTPUT_GROUP_ID, int):
        errors.append(f"OUTPUT_GROUP_ID must be integer: {OUTPUT_GROUP_ID}")
    
    if SAVE_TO_DRIVE and not DRIVE_FOLDER_ID:
        errors.append("SAVE_TO_DRIVE=True but DRIVE_FOLDER_ID is empty")
    
    if errors:
        print("❌ Configuration errors:")
        for e in errors:
            print(f"  • {e}")
        return False
    
    print(f"✅ Config validated: {len(SOURCE_CHANNELS)} source channels, output: {OUTPUT_GROUP_ID}")
    return True


# test_channels.py (optional debug script)
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from config import SOURCE_CHANNELS, OUTPUT_GROUP_ID, TELEGRAM_CREDS

async def test():
    client = TelegramClient(
        StringSession(TELEGRAM_CREDS["session"]),
        TELEGRAM_CREDS["api_id"],
        TELEGRAM_CREDS["api_hash"]
    )
    await client.start()
    
    print("🔍 Testing channel access...")
    for ch in SOURCE_CHANNELS:
        try:
            entity = await client.get_entity(ch["id"])
            print(f"✅ {ch['name']}: {entity.title} (ID: {ch['id']})")
        except Exception as e:
            print(f"❌ {ch['name']}: {e}")
    
    try:
        entity = await client.get_entity(OUTPUT_GROUP_ID)
        print(f"✅ Output group: {entity.title} (ID: {OUTPUT_GROUP_ID})")
    except Exception as e:
        print(f"❌ Output group: {e}")
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test())