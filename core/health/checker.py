# File: core/health/checker.py
import asyncio
from pyrogram import Client
from pyrogram.errors import SessionExpired, AuthKeyInvalid
from pathlib import Path
from config import Settings, constants

class SessionHealth:
    @staticmethod
    async def check_session(session_name: str) -> dict:
        """Check session health status"""
        session_file = Settings.SESSION_DIR / f"{session_name}.session"
        
        if not session_file.exists():
            return {"status": False, "reason": "Session file not found"}
        
        try:
            async with Client(
                session_name,
                workdir=str(Settings.SESSION_DIR),
                api_id=Settings.API_ID,
                api_hash=Settings.API_HASH
            ) as app:
                user = await app.get_me()
                return {
                    "status": True,
                    "user": {
                        "id": user.id,
                        "phone": user.phone_number,
                        "username": user.username
                    }
                }
        except (SessionExpired, AuthKeyInvalid) as e:
            return {"status": False, "reason": str(e)}
        except Exception as e:
            return {"status": False, "reason": str(e)}

    @staticmethod
    async def check_all_sessions():
        """Check all registered sessions"""
        sessions = [f.stem for f in Settings.SESSION_DIR.glob("*.session")]
        results = {}
        
        for session in sessions:
            results[session] = await SessionHealth.check_session(session)
            
        return results