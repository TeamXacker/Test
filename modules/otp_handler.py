# File: core/modules/otp_handler.py

import re
import asyncio
from pyrogram import Client, filters
from config.settings import Settings
from core.utils.logger import log

class OTPFetcher:
    OTP_PATTERNS = [
        r"Login code: (\d{5})",
        r"(\d{5}) is your Telegram code",
        r"code: (\d{5})"
    ]

    @classmethod
    async def wait_for_otp(cls, session_name: str, timeout: int = 120) -> str:
        """
        Waits ONLY for a NEW OTP message from Telegram (777000).
        Args:
            session_name: Session name (without .session)
            timeout: Max seconds to wait
        Returns:
            OTP code (str) or empty string if not found
        """
        session_path = f"{Settings.SESSION_DIR}/{session_name}"
        otp_code = ""

        app = Client(session_path, api_id=Settings.API_ID, api_hash=Settings.API_HASH)
        event = asyncio.Event()

        @app.on_message(filters.chat(777000))
        async def otp_handler(_, message):
            nonlocal otp_code
            if not message.text:
                return
            for pattern in cls.OTP_PATTERNS:
                match = re.search(pattern, message.text)
                if match:
                    otp_code = match.group(1)
                    log(f"NEW OTP received for {session_name}: {otp_code}")
                    event.set()
                    break

        await app.start()
        try:
            try:
                await asyncio.wait_for(event.wait(), timeout)
            except asyncio.TimeoutError:
                log(f"Timeout waiting for NEW OTP for {session_name}")

        finally:
            await app.stop()

        return otp_code