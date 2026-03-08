#!/usr/bin/env python3
# ════════════════════════════════════════════════════════════════════════════
# 🤖 Equity Bot - Main Entry Point
# 📁 Location: src/equity_bot.py
# ════════════════════════════════════════════════════════════════════════════
# ────────────────────────────────────────────────────────────────────────────
# 🔧 PATH FIX: Enable imports from src/ directory when running from repo root
# ────────────────────────────────────────────────────────────────────────────
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
# ────────────────────────────────────────────────────────────────────────────

# ════════════════════════════════════════════════════════════════════════════
# 📦 STANDARD IMPORTS
# ════════════════════════════════════════════════════════════════════════════

import os
import json
import re
import time
import random
import asyncio
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ════════════════════════════════════════════════════════════════════════════
# 🔐 CREDENTIAL LOADER
# ════════════════════════════════════════════════════════════════════════════

def load_credentials():
    """Load credentials from environment variables (GitHub Secrets)"""
    creds = {
        "openrouter": os.getenv("OPENROUTER_API_KEY"),
        "nvidia": os.getenv("NVIDIA_API_KEY"),
        "groq": os.getenv("GROQ_KEY"),
        "github": os.getenv("GITHUB_TOKEN"),
        "telegram": {
            "session": os.getenv("TELEGRAM_STRING_SESSION"),
            "api_id": os.getenv("TELEGRAM_API_ID"),
            "api_hash": os.getenv("TELEGRAM_API_HASH"),
        },
        "drive": {
            "service_account": os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"),
            "folder_id": os.getenv("DRIVE_FOLDER_ID"),
        }
    }
    
    required = [
        ("telegram.session", creds["telegram"]["session"]),
        ("telegram.api_id", creds["telegram"]["api_id"]),
        ("telegram.api_hash", creds["telegram"]["api_hash"]),
    ]
    
    llm_providers = [
        ("openrouter", creds["openrouter"]),
        ("nvidia", creds["nvidia"]),
        ("groq", creds["groq"]),
    ]
    
    missing = [name for name, val in required if not val]
    if missing:
        print(f"❌ Missing required credentials: {', '.join(missing)}")
        return None
    
    if not any(val for _, val in llm_providers):
        print("❌ At least one LLM API key must be provided")
        return None
    
    return creds


# ════════════════════════════════════════════════════════════════════════════
# 📦 IMPORTS - Local modules
# ════════════════════════════════════════════════════════════════════════════

from config import (
    SOURCE_CHANNELS,
    OUTPUT_GROUP_ID,
    HOURS_AGO,
    MAX_MESSAGES_PER_CHANNEL,
    DOWNLOAD_FILES,
    VALID_EXTENSIONS,
    FILES_TO_ANALYZE,
    MAX_PAGES_PER_FILE,
    CHUNK_SIZE_CHARS,
    ENABLE_REASONING,
    MAX_RETRIES,
    RATE_LIMIT_BACKOFF,
    SAVE_TO_DRIVE,
    DRIVE_FOLDER_ID,
    DOWNLOAD_DIR,
    CACHE_DIR,
    KNOWLEDGE_CACHE_FILE,
    MAX_KNOWLEDGE_ENTRIES,
    RUNNING_IN_GITHUB,
    validate_config,
)

from utils.pdf_extractor import extract_text_from_pdf, chunk_text_smart
from utils.telegram_client import TelegramBot

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io


# ════════════════════════════════════════════════════════════════════════════
# 🧠 GOOGLE DRIVE SERVICE
# ════════════════════════════════════════════════════════════════════════════

class DriveService:
    def __init__(self, service_account_json: str, folder_id: str):
        self.folder_id = folder_id
        self.service = self._init_service(service_account_json)
    
    def _init_service(self, sa_json: str):
        try:
            creds = service_account.Credentials.from_service_account_info(
                json.loads(sa_json),
                scopes=["https://www.googleapis.com/auth/drive.file"]
            )
            return build("drive", "v3", credentials=creds)
        except Exception as e:
            print(f"⚠️ Drive init failed: {e}")
            return None
    
    def upload_text(self, content: str, filename: str) -> str | None:
        if not self.service:
            return None
        try:
            file_metadata = {
                "name": filename,
                "parents": [self.folder_id] if self.folder_id else None,
            }
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode("utf-8")),
                mimetype="text/markdown",
                resumable=True
            )
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id,webViewLink"
            ).execute()
            print(f"💾 Uploaded: {file.get('webViewLink')}")
            return file.get("id")
        except Exception as e:
            print(f"⚠️ Drive upload failed: {e}")
            return None


# ════════════════════════════════════════════════════════════════════════════
# 🧠 KNOWLEDGE CACHE
# ════════════════════════════════════════════════════════════════════════════

class KnowledgeCache:
    def __init__(self, cache_path: Path, max_entries: int = 25):
        self.cache_path = cache_path
        self.max_entries = max_entries
        self.data = self._load()
    
    def _load(self) -> dict:
        try:
            if self.cache_path.exists():
                with open(self.cache_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Cache load failed: {e}")
        return {'entries': [], 'last_updated': None}
    
    def _save(self):
        try:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.data['last_updated'] = datetime.now().isoformat()
            with open(self.cache_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Cache save failed: {e}")
    
    def add_insight(self, filename: str, insights: list, channel: str = ""):
        entry = {
            'filename': filename,
            'channel': channel,
            'timestamp': datetime.now().isoformat(),
            'insights': insights[:5]
        }
        self.data['entries'].append(entry)
        if len(self.data['entries']) > self.max_entries:
            self.data['entries'] = self.data['entries'][-self.max_entries:]
        self._save()
        print(f"💾 Cached {len(insights[:5])} insights from {filename}")
    
    def get_context(self, keywords: list = None, max_entries: int = 5, 
                   channel_filter: str = None) -> str:
        if not self.data['entries']:
            return ""
        entries = self.data['entries']
        if channel_filter:
            entries = [e for e in entries if e.get('channel') == channel_filter]
        if keywords:
            kw_lower = [k.lower() for k in keywords]
            entries = [
                e for e in entries
                if any(
                    kw in e['filename'].lower() or 
                    any(kw in ins.lower() for ins in e['insights'])
                    for kw in kw_lower
                )
            ]
        selected = entries[-max_entries:] if entries else self.data['entries'][-max_entries:]
        parts = []
        for entry in selected:
            tag = f"[{entry.get('channel', '?')}]" if entry.get('channel') else ""
            parts.append(f"### {tag} {entry['filename']} ({entry['timestamp'][:10]})")
            parts.extend([f"• {ins}" for ins in entry['insights']])
            parts.append("")
        return "\n".join(parts).strip()


# ════════════════════════════════════════════════════════════════════════════
# 🧠 MULTI-PROVIDER CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

def build_providers_config(creds: dict) -> dict:
    providers = {}
    
    if creds.get("openrouter"):
        providers["openrouter"] = {
            "enabled": True,
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": creds["openrouter"],
            "models": [
                {"name": "google/gemma-2-9b-it:free", "rpm": 20, "priority": 1, "ctx": 8192},
                {"name": "meta-llama/llama-3.2-3b-instruct:free", "rpm": 20, "priority": 2, "ctx": 8192},
                {"name": "arcee-ai/trinity-large-preview:free", "rpm": 20, "priority": 3, "ctx": 16384, "reasoning": True},
                {"name": "qwen/qwen-2.5-7b-instruct:free", "rpm": 20, "priority": 4, "ctx": 32768},
                {"name": "microsoft/phi-3.5-mini-instruct:free", "rpm": 20, "priority": 5, "ctx": 128000},
            ],
            "headers": lambda key: {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/equity-bot",
                "X-Title": "Equity Analysis Bot",
            }
        }
    
    if creds.get("nvidia"):
        providers["nvidia"] = {
            "enabled": True,
            "base_url": "https://integrate.api.nvidia.com/v1",
            "api_key": creds["nvidia"],
            "models": [
                {"name": "meta/llama-3.1-8b-instruct", "rpm": 30, "priority": 1, "ctx": 8192},
                {"name": "google/gemma-2-9b-it", "rpm": 25, "priority": 2, "ctx": 8192},
                {"name": "mistralai/mistral-7b-instruct-v0.2", "rpm": 20, "priority": 3, "ctx": 32768},
            ],
            "headers": lambda key: {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        }
    
    if creds.get("groq"):
        providers["groq"] = {
            "enabled": True,
            "base_url": "https://api.groq.com/openai/v1",
            "api_key": creds["groq"],
            "models": [
                {"name": "llama3-8b-8192", "rpm": 30, "priority": 1, "ctx": 8192},
                {"name": "llama-3.1-8b-instant", "rpm": 30, "priority": 2, "ctx": 8192},
                {"name": "gemma2-9b-it", "rpm": 25, "priority": 3, "ctx": 8192},
                {"name": "mixtral-8x7b-32768", "rpm": 20, "priority": 4, "ctx": 32768},
            ],
            "headers": lambda key: {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        }
    
    if creds.get("github"):
        providers["github"] = {
            "enabled": True,
            "base_url": "https://models.inference.ai.azure.com",
            "api_key": creds["github"],
            "models": [
                {"name": "Phi-3.5-mini-instruct", "rpm": 10, "priority": 1, "ctx": 128000},
                {"name": "Mistral-Nemo-12B-Instruct", "rpm": 8, "priority": 2, "ctx": 128000},
            ],
            "headers": lambda key: {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
        }
    
    return providers


# ════════════════════════════════════════════════════════════════════════════
# 🧠 GOD-MODE PROMPT
# ════════════════════════════════════════════════════════════════════════════

GOD_PROMPT = """🔮 ROLE: Autonomous Equity Oracle. MAX SIGNAL, ZERO NOISE.

🎯 FRAMEWORK:
1. SURFACE: Claims/numbers with [DATA]/[LOGIC]/[OPINION] tags
2. CONTEXT: Consensus vs this view + confidence
3. FIRST-PRINCIPLES: Truth + assumptions + falsification
4. GOD-INSIGHTS: Non-obvious connections + second-order effects

⚙️ RULES:
• Cite page/section • Tag every insight • Remove fluff • Prioritize novelty • <1800 words

📤 OUTPUT FORMAT:
## 🎯 Core Thesis
• [CONVICTION: H/M/L] One-sentence thesis • Biggest mispricing • Top catalyst

## 📊 Layered Analysis
### Facts • [Claims with refs]
### Context • Consensus vs This • Attribution
### First-Principles • Truth • Assumptions • Falsify
### God-Insights [EXTRAPOLATION] • Non-obvious • Second-order • Asymmetric

## ⚠️ Risks | Risk | Prob | Impact | Attribution |
## 🚀 Actionable • View: [Long/Short/Neutral] + [Conviction%] • Triggers • Monitor: [3 metrics]
## 🔄 Self-Correction • Assumptions • Uncertainty

🔮 End: "Confidence: X%"
"""

# ════════════════════════════════════════════════════════════════════════════
# 🧠 MODEL ROUTER
# ════════════════════════════════════════════════════════════════════════════

class Router:
    def __init__(self, providers: dict):
        self.providers = {k: v for k, v in providers.items() if v.get('enabled')}
        self.usage = {pid: {"req": 0, "err": 0, "last429": None} for pid in self.providers}
        self.perf = {}
        self.broken_models = set()
        print(f"🔄 Router initialized: {list(self.providers.keys())}")
    
    def pick(self, task: str = "analysis", reasoning: bool = False) -> dict | None:
        candidates = []
        for pid, cfg in self.providers.items():
            if self.usage[pid]["err"] > 5:
                continue
            if self.usage[pid]["last429"] and time.time() - self.usage[pid]["last429"] < RATE_LIMIT_BACKOFF:
                continue
            for model in cfg["models"]:
                if reasoning and not model.get("reasoning"):
                    continue
                model_key = f"{pid}:{model['name']}"
                if model_key in self.broken_models:
                    continue
                score = model.get("priority", 99)
                if model_key in self.perf and self.perf[model_key].get("success_rate", 1) > 0.9:
                    score -= 1
                candidates.append({
                    "provider": pid,
                    "model": model["name"],
                    "cfg": cfg,
                    "model_cfg": model,
                    "score": score,
                    "ctx": model.get("ctx", 8192),
                    "key": model_key
                })
        if not candidates:
            print("⚠️ No available models")
            return None
        candidates.sort(key=lambda x: (x["score"], random.random()))
        selected = candidates[0]
        self.usage[selected["provider"]]["req"] += 1
        print(f"🎯 {selected['provider']} → {selected['model']}")
        return selected
    
    def record(self, pid: str, model: str, success: bool, latency_ms: float = None, error_code: str = None):
        key = f"{pid}:{model}"
        if key not in self.perf:
            self.perf[key] = {"total": 0, "success": 0, "latencies": []}
        stats = self.perf[key]
        stats["total"] += 1
        if success:
            stats["success"] += 1
            if latency_ms:
                stats["latencies"].append(latency_ms)
                stats["latencies"] = stats["latencies"][-20:]
        else:
            self.usage[pid]["err"] += 1
            self.usage[pid]["last429"] = time.time()
            if error_code == 404:
                self.broken_models.add(key)
                print(f"🚫 Marked broken (404): {key}")
    
    def stats(self) -> dict:
        return {pid: {"requests": u["req"], "errors": u["err"]} for pid, u in self.usage.items()}


# ════════════════════════════════════════════════════════════════════════════
# 🧠 ANALYZER
# ════════════════════════════════════════════════════════════════════════════

class Analyzer:
    def __init__(self, router: Router, cache: KnowledgeCache = None, drive: DriveService = None):
        self.router = router
        self.cache = cache
        self.drive = drive
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "EquityBot/2.0"})
    
    def _make_request(self, model_cfg: dict, messages: list, temperature: float = 0.1, 
                     max_tokens: int = 2800, reasoning: bool = False) -> dict | None:
        pid = model_cfg["provider"]
        model = model_cfg["model"]
        cfg = model_cfg["cfg"]
        url = f"{cfg['base_url']}/chat/completions"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if pid == "openrouter" and reasoning and model_cfg["model_cfg"].get("reasoning"):
            payload["reasoning"] = {"enabled": True}
        headers = cfg["headers"](cfg["api_key"])
        start_time = time.time()
        try:
            response = self.session.post(url, headers=headers, json=payload, timeout=120)
            latency_ms = (time.time() - start_time) * 1000
            if response.status_code == 404:
                print(f"❌ Model not found (404): {pid}:{model}")
                self.router.record(pid, model, False, latency_ms, error_code=404)
                return None
            if response.status_code == 429:
                print(f"⚠️ Rate limited (429): {pid}:{model}")
                self.router.record(pid, model, False, latency_ms, error_code=429)
                return None
            if response.status_code >= 400:
                print(f"❌ HTTP {response.status_code}: {response.text[:150]}")
                self.router.record(pid, model, False, latency_ms, error_code=str(response.status_code))
                return None
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            reasoning_out = None
            if pid == "openrouter":
                msg = data["choices"][0]["message"]
                reasoning_out = msg.get("reasoning_details") or msg.get("reasoning")
            self.router.record(pid, model, True, latency_ms)
            return {
                "content": content,
                "reasoning": reasoning_out,
                "provider": pid,
                "model": model
            }
        except requests.Timeout:
            print(f"⏰ Timeout: {pid}:{model}")
            self.router.record(pid, model, False, error_code="timeout")
            return None
        except Exception as e:
            print(f"❌ Request error {pid}:{model}: {e}")
            self.router.record(pid, model, False, error_code="exception")
            return None
    
    def analyze_document(self, text: str, filename: str, context: str = "", 
                        channel: str = "", task_type: str = "analysis") -> dict | None:
        for attempt in range(MAX_RETRIES):
            prefer_reasoning = ENABLE_REASONING and task_type == "deep_analysis"
            model_cfg = self.router.pick(task_type, reasoning=prefer_reasoning)
            if not model_cfg:
                return None
            max_chars = int(model_cfg["ctx"] * 3.5)
            safe_text = text[:max_chars] + ("..." if len(text) > max_chars else "")
            context_block = f"\n\n🧠 PAST INSIGHTS:\n{context}" if context else ""
            channel_tag = f"[{channel}]" if channel else ""
            user_prompt = f"""DOCUMENT: {filename} {channel_tag}
CONTENT:
{safe_text}
{context_block}

TASK: Apply the god-mode framework. Output ONLY the structured format. No preamble."""
            messages = [
                {"role": "system", "content": GOD_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
            print(f"🧠 Attempt {attempt+1}: {model_cfg['provider']} → {model_cfg['model']}")
            result = self._make_request(
                model_cfg,
                messages,
                temperature=0.1,
                max_tokens=2800,
                reasoning=(ENABLE_REASONING and model_cfg["model_cfg"].get("reasoning", False))
            )
            if result and result["content"]:
                print(f"✅ Success ({len(result['content']):,} chars)")
                return {
                    "content": self._format_output(result["content"]),
                    "reasoning": result.get("reasoning"),
                    "provider": model_cfg["provider"],
                    "model": model_cfg["model"]
                }
            if attempt < MAX_RETRIES - 1:
                wait_time = 2 ** attempt
                print(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        print("❌ All attempts failed")
        return None
    
    def _format_output(self, text: str) -> str:
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.replace('###', '**').replace('##', '🔹')
        if not text.startswith("🔹"):
            text = "🔹 " + text
        if len(text) > 3800:
            text = text[:3700] + "\n\n*...continued in attached file*"
        return text.strip()
    
    def analyze_multiple_files(self, files_data: list) -> list:
        print(f"\n🚀 ANALYZING {len(files_data)} files")
        results = []
        for i, file_data in enumerate(files_data, 1):
            print(f"\n{'='*70}")
            print(f"📄 {i}/{len(files_data)}: {file_data['filename']}")
            print(f"{'='*70}")
            keywords = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', file_data['filename'])[:5]
            channel_name = file_data.get('channel_name')
            past_context = self.cache.get_context(
                keywords, 
                max_entries=3, 
                channel_filter=channel_name
            ) if self.cache else ""
            if len(file_data['text']) > CHUNK_SIZE_CHARS:
                print(f"⚠️ Chunking ({len(file_data['text']):,} chars)...")
                chunks = chunk_text_smart(file_data['text'], CHUNK_SIZE_CHARS)
                print(f"✅ Split into {len(chunks)} chunks")
                chunk_analyses = []
                for j, chunk in enumerate(chunks[:2], 1):
                    print(f"  🔹 Chunk {j}")
                    chunk_result = self.analyze_document(
                        chunk,
                        f"{file_data['filename']} [Part {j}]",
                        past_context if j == 1 else "",
                        channel_name,
                        task_type="chunk_analysis"
                    )
                    if chunk_result:
                        chunk_analyses.append(chunk_result)
                if chunk_analyses:
                    synthesis = self._synthesize_chunks(chunk_analyses, file_data['filename'])
                    if synthesis:
                        results.append({
                            'filename': file_data['filename'],
                            'analysis': synthesis['content'],
                            'channel': channel_name,
                            'provider': synthesis['provider'],
                            'model': synthesis['model']
                        })
            else:
                result = self.analyze_document(
                    file_data['text'],
                    file_data['filename'],
                    past_context,
                    channel_name,
                    task_type="deep_analysis"
                )
                if result:
                    results.append({
                        'filename': file_data['filename'],
                        'analysis': result['content'],
                        'channel': channel_name,
                        'provider': result['provider'],
                        'model': result['model']
                    })
            if results and self.cache:
                latest = results[-1]['analysis']
                insights = [
                    line.strip() for line in latest.split('\n')
                    if any(tag in line for tag in ['[EXTRAPOLATION]', '[DATA]', '🔹'])
                ][:5]
                if insights:
                    self.cache.add_insight(file_data['filename'], insights, channel_name)
            if i < len(files_data):
                print(f"\n⏳ Cooldown {RATE_LIMIT_BACKOFF}s...")
                time.sleep(RATE_LIMIT_BACKOFF)
        return results
    
    def _synthesize_chunks(self, chunk_analyses: list, filename: str) -> dict | None:
        if len(chunk_analyses) == 1:
            return chunk_analyses[0]
        combined = "\n\n".join(c['content'] for c in chunk_analyses)[:9000]
        synthesis_prompt = f"""Synthesize these equity analysis fragments into one coherent report. 
Remove duplicates. Highlight the 3 most important insights.

{combined}"""
        model_cfg = self.router.pick("synthesis", reasoning=False)
        if not model_cfg:
            print("⚠️ No model available for synthesis, returning first chunk")
            return chunk_analyses[0]
        messages = [
            {"role": "system", "content": "Senior equity analyst. Synthesize concisely."},
            {"role": "user", "content": synthesis_prompt}
        ]
        result = self._make_request(model_cfg, messages, temperature=0.1, max_tokens=2500)
        if result and result["content"]:
            return {
                "content": self._format_output(result["content"]),
                "provider": model_cfg["provider"],
                "model": model_cfg["model"]
            }
        print("⚠️ Synthesis failed, using first chunk")
        return chunk_analyses[0]


# ════════════════════════════════════════════════════════════════════════════
# 🚀 MAIN PIPELINE
# ════════════════════════════════════════════════════════════════════════════

async def run_pipeline():
    start_time = datetime.now()
    print(f"\n{'='*80}")
    print(f"🚀 EQUITY BOT STARTED: {start_time.isoformat()}")
    print(f"{'='*80}")
    
    creds = load_credentials()
    if not creds:
        print("❌ Failed to load credentials — exiting")
        return False
    
    if not validate_config():
        return False
    
    print(f"\n💾 Initializing cache: {KNOWLEDGE_CACHE_FILE}")
    cache = KnowledgeCache(KNOWLEDGE_CACHE_FILE, MAX_KNOWLEDGE_ENTRIES)
    print(f"   Loaded {len(cache.data['entries'])} cached entries")
    
    providers = build_providers_config(creds)
    print(f"🧠 Active providers: {list(providers.keys())}")
    
    router = Router(providers)
    
    drive = None
    if SAVE_TO_DRIVE and creds["drive"]["service_account"] and creds["drive"]["folder_id"]:
        drive = DriveService(creds["drive"]["service_account"], creds["drive"]["folder_id"])
        print(f"💾 Drive service initialized")
    
    analyzer = Analyzer(router, cache, drive)
    
    tg_creds = creds["telegram"]
    async with TelegramBot(
        session=tg_creds["session"],
        api_id=tg_creds["api_id"],
        api_hash=tg_creds["api_hash"],
        download_dir=DOWNLOAD_DIR if DOWNLOAD_FILES else None
    ) as telegram:
        
        print(f"\n📥 STEP 1: Fetching files (last {HOURS_AGO} hours)...")
        files = await telegram.fetch_files(
            channels=SOURCE_CHANNELS,
            hours_ago=HOURS_AGO,
            max_messages=MAX_MESSAGES_PER_CHANNEL,
            extensions=VALID_EXTENSIONS
        )
        
        if not files:
            print("\n❌ No files found — pipeline complete")
            return True
        
        print(f"📊 Found {len(files)} files")
        
        print(f"\n📊 STEP 2: Selecting top {FILES_TO_ANALYZE} files...")
        
        def priority_score(f):
            score = 0
            name_lower = f['name'].lower()
            priority_keywords = ['initiating', 'coverage', 'upgrade', 'downgrade', 'target', 'earnings']
            score += sum(10 for kw in priority_keywords if kw in name_lower)
            score += min(f['size_mb'], 10)
            hours_old = (datetime.now(timezone.utc) - f['date_utc']).total_seconds() / 3600
            if hours_old < 12:
                score += 5
            return score
        
        sorted_files = sorted(files, key=priority_score, reverse=True)
        selected = sorted_files[:FILES_TO_ANALYZE]
        
        for i, f in enumerate(selected, 1):
            print(f"   {i}. [{f['channel_name']}] {f['name']} ({f['size_mb']} MB)")
        
        print(f"\n📄 STEP 3: Extracting text...")
        files_data = []
        for f in selected:
            if f.get('path') and Path(f['path']).exists():
                text = extract_text_from_pdf(f['path'], max_pages=MAX_PAGES_PER_FILE)
                if text and len(text) > 500:
                    files_data.append({
                        'text': text,
                        'filename': f['name'],
                        'path': f['path'],
                        'channel_name': f['channel_name']
                    })
                    print(f"   ✅ {f['name']}: {len(text):,} chars")
        
        if not files_data:
            print("\n❌ No extractable text — pipeline complete")
            return True
        
        print(f"\n🧠 STEP 4: Analyzing documents...")
        results = analyzer.analyze_multiple_files(files_data)
        
        print(f"\n{'='*80}")
        print(f"📤 SENDING OUTPUT")
        print(f"{'='*80}")
        
        for result in results:
            if not result.get('analysis'):
                continue
            channel_tag = f"[{result.get('channel', '?')}] " if result.get('channel') else ""
            provider_tag = f"[{result['provider']}:{result['model']}] "
            full_output = f"{channel_tag}{provider_tag}{result['analysis']}"
            print(f"\n📤 Sending to Telegram group {OUTPUT_GROUP_ID}...")
            tg_success = await telegram.send_message(OUTPUT_GROUP_ID, full_output)
            if SAVE_TO_DRIVE and drive and tg_success:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_name = re.sub(r'[^\w\s-]', '', result['filename'])[:35]
                filename = f"Analysis_{result['provider']}_{safe_name}_{timestamp}.md"
                print(f"💾 Uploading to Drive: {filename}")
                drive.upload_text(result['analysis'], filename)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"\n{'='*80}")
        print(f"✅ PIPELINE COMPLETE")
        print(f"{'='*80}")
        print(f"📊 Results: {len(results)}/{len(files_data)} files analyzed")
        print(f"🔄 Provider usage: {router.stats()}")
        print(f"💾 Cache entries: {len(cache.data['entries'])}")
        print(f"⏱️ Runtime: {elapsed:.1f} seconds")
        print(f"\n🎯 Next: Check Telegram group | Review Drive folder")
        print(f"{'='*80}")
        
        return True


# ════════════════════════════════════════════════════════════════════════════
# 🏁 ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        success = asyncio.run(run_pipeline())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
