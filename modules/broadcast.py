# File: core/modules/broadcast.py
import asyncio
from typing import List, Dict
from pyrogram import Client
from pathlib import Path
from config import Settings, constants
from core.anti_ban import AntiBan
from core.utils.logger import log

class BroadcastManager:

    @classmethod
    async def mass_broadcast(cls, sessions, target, message):
        results = {
            'success': 0,
            'failed': 0,
            'details': {}
        }

        total = len(sessions)

        # Launch all sending tasks
        tasks = [
            cls._send_and_log(index, total, session_name, target, message, results)
            for index, session_name in enumerate(sessions, 1)
        ]

        await asyncio.gather(*tasks)

        return results

    @classmethod
    async def _send_and_log(cls, index, total, session_name, target, message, results):
        app = Client(f"{Settings.SESSION_DIR}/{session_name}", api_id=Settings.API_ID, api_hash=Settings.API_HASH)
        await app.start()
        try:
            await app.send_message(target, message)
            log(f"[{session_name}] Message sent to {target}")
            print(f"[{index}/{total}] {session_name} -> Success")
            results['success'] += 1
            results['details'][session_name] = "Success"
        except Exception as e:
            log(f"[{session_name}] Failed to send message: {e}")
            print(f"[{index}/{total}] {session_name} -> Failed: {str(e)}")
            results['failed'] += 1
            results['details'][session_name] = f"Failed: {str(e)}"
        finally:
            await app.stop()