# src/utils/telegram_client.py
"""Modular Telegram client for fetching and sending messages"""

import asyncio
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from telethon import TelegramClient
from telethon.sessions import StringSession


class TelegramBot:
    """Telegram client wrapper for equity bot"""
    
    def __init__(
        self,
        session: str,
        api_id: str,
        api_hash: str,
        download_dir: Optional[Path] = None
    ):
        self.session = session
        self.api_id = int(api_id)
        self.api_hash = api_hash
        self.download_dir = download_dir or Path("/tmp/equity-bot/downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self._client: Optional[TelegramClient] = None
    
    async def __aenter__(self):
        self._client = TelegramClient(
            StringSession(self.session),
            self.api_id,
            self.api_hash
        )
        await self._client.start()
        return self
    
    async def __aexit__(self, *args):
        if self._client:
            await self._client.disconnect()
    
    async def fetch_files(
        self,
        channels: list[dict],
        hours_ago: int = 50,
        max_messages: int = 150,
        extensions: list[str] = None
    ) -> list[dict]:
        """Fetch files from Telegram channels."""
        extensions = extensions or ['.pdf', '.docx', '.xlsx', '.txt']
        all_files = []
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        
        for ch in channels:
            cid = ch['id']
            cname = ch.get('name', f"Channel_{cid}")
            print(f"📺 Fetching: {cname}")
            
            try:
                channel = await self._client.get_entity(cid)
                files_found = 0
                
                async for msg in self._client.iter_messages(channel, limit=max_messages):
                    if not msg.date:
                        continue
                    msg_utc = msg.date if msg.date.tzinfo else msg.date.replace(tzinfo=timezone.utc)
                    if msg_utc < cutoff:
                        continue
                    if msg.file and msg.file.name:
                        fname = msg.file.name.lower()
                        if any(fname.endswith(ext) for ext in extensions):
                            file_info = {
                                'name': msg.file.name,
                                'size_mb': round(msg.file.size / (1024*1024), 2),
                                'date': msg.date,
                                'date_utc': msg_utc,
                                'path': None,
                                'channel_name': cname,
                                'channel_id': cid
                            }
                            all_files.append(file_info)
                            files_found += 1
                            print(f"  📎 {file_info['name']} ({file_info['size_mb']} MB)")
                            if self.download_dir:
                                try:
                                    file_info['path'] = await msg.download_media(
                                        file=self.download_dir / msg.file.name
                                    )
                                except Exception as e:
                                    print(f"    ❌ Download error: {e}")
                
                print(f"✅ {cname}: {files_found} files")
            except Exception as e:
                print(f"❌ Error fetching {cname}: {e}")
                continue
        
        return sorted(all_files, key=lambda x: x['date_utc'], reverse=True)
    
   async def send_message(self, group_id: int, text: str, parse_mode: str = 'md') -> bool:
    """Send formatted message to Telegram group."""
    try:
        print(f"\n📤 Sending to group {group_id}...")
        print(f"🔍 Group ID type: {type(group_id)}")
        
        # Get bot info
        me = await self._client.get_me()
        print(f"🤖 Logged in as: {me.first_name} (@{me.username or 'no_username'})")
        print(f"🤖 Is bot: {me.bot}")
        
        # Try multiple ID formats
        entity = None
        test_ids = [group_id, int(f"-100{abs(group_id)}"), str(group_id)]
        
        for test_id in test_ids:
            try:
                print(f"🔍 Trying ID: {test_id}")
                entity = await self._client.get_entity(test_id)
                print(f"✅ Resolved: {entity.title} (type: {type(entity).__name__})")
                break
            except Exception as e:
                print(f"⚠️ Failed {test_id}: {type(e).__name__}")
                continue
        
        if not entity:
            print(f"❌ Could not resolve group {group_id}")
            return False
        
        # Check permissions
        try:
            await self._client.get_permissions(entity)
            print(f"✅ Have permissions in group")
        except Exception as e:
            print(f"⚠️ Permission check failed: {e}")
        
        # Split and send
        max_len = 3800
        parts = [text[i:i+max_len] for i in range(0, len(text), max_len)]
        print(f"📄 Message split into {len(parts)} part(s)")
        
        for i, part in enumerate(parts, 1):
            prefix = f"📊 Part {i}/{len(parts)}\n\n" if len(parts) > 1 else ""
            await self._client.send_message(
                entity,
                prefix + part,
                parse_mode=parse_mode,
                link_preview=False
            )
            print(f"📤 Sent part {i}/{len(parts)}")
            await asyncio.sleep(1.5)
        
        return True
    except Exception as e:
        print(f"⚠️ Send failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
