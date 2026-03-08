# src/config.py
# ════════════════════════════════════════════════════════════════════════════
# ⚙️ Bot Configuration - Channel IDs, Limits, Settings
# ════════════════════════════════════════════════════════════════════════════

import os
from pathlib import Path

# ════════════════════════════════════════════════════════════════════════════
# 📺 Telegram Channel Configuration
# ════════════════════════════════════════════════════════════════════════════

SOURCE_CHANNELS = [
    {"id": -1001588470529, "name": "Channel Alpha"},
    {"id": -1003025504126, "name": "Equity Research Reports"},
]

OUTPUT_GROUP_ID = -1003723569586

# ════════════════════════════════════════════════════════════════════════════
# ⏰ Fetch Settings
# ════════════════════════════════════════════════════════════════════════════

HOURS_AGO = int(os.getenv("HOURS_AGO", "100"))
MAX_MESSAGES_PER_CHANNEL = int(os.getenv("MAX_MESSAGES_PER_CHANNEL", "150"))
DOWNLOAD_FILES = os.getenv("DOWNLOAD_FILES", "true").lower() == "true"
VALID_EXTENSIONS = [".pdf", ".docx", ".xlsx", ".txt"]

# ════════════════════════════════════════════════════════════════════════════
# 🧠 Analysis Settings
# ════════════════════════════════════════════════════════════════════════════

FILES_TO_ANALYZE = int(os.getenv("FILES_TO_ANALYZE", "2"))
MAX_PAGES_PER_FILE = int(os.getenv("MAX_PAGES_PER_FILE", "5"))
CHUNK_SIZE_CHARS = int(os.getenv("CHUNK_SIZE_CHARS", "4000"))
ENABLE_REASONING = os.getenv("ENABLE_REASONING", "false").lower() == "true"
MAX_RETRIES = 3
RATE_LIMIT_BACKOFF = int(os.getenv("RATE_LIMIT_BACKOFF", "10"))

# ════════════════════════════════════════════════════════════════════════════
# 💾 Storage Settings
# ════════════════════════════════════════════════════════════════════════════

SAVE_TO_DRIVE = os.getenv("SAVE_TO_DRIVE", "true").lower() == "true"
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "")
CACHE_DIR = Path(os.getenv("CACHE_DIR", "/tmp/equity-bot/cache"))
KNOWLEDGE_CACHE_FILE = CACHE_DIR / "knowledge_cache.json"
MAX_KNOWLEDGE_ENTRIES = int(os.getenv("MAX_KNOWLEDGE_ENTRIES", "25"))
DOWNLOAD_DIR = Path(os.getenv("DOWNLOAD_DIR", "/tmp/equity-bot/downloads"))

# ════════════════════════════════════════════════════════════════════════════
# 🔄 Runtime Mode Detection
# ════════════════════════════════════════════════════════════════════════════

RUNNING_IN_GITHUB = os.getenv("GITHUB_ACTIONS", "false").lower() == "true"

if RUNNING_IN_GITHUB:
    FILES_TO_ANALYZE = min(FILES_TO_ANALYZE, 2)
    MAX_PAGES_PER_FILE = min(MAX_PAGES_PER_FILE, 5)
    ENABLE_REASONING = False
    print(f"🔧 GitHub Actions mode: conservative settings applied")


def validate_config():
    """Check required config values at startup"""
    errors = []
    
    if not SOURCE_CHANNELS:
        errors.append("SOURCE_CHANNELS is empty")
    
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
