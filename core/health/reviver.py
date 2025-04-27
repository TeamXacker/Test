# File: core/health/reviver.py
import asyncio
from pyrogram import Client
from pyrogram.errors import (
    SessionRevoked,
    AuthKeyInvalid,
    PhoneCodeInvalid,
    SessionPasswordNeeded
)

class SessionReviver:
    @staticmethod
    async def revive_session(session_name: str) -> bool:
        """Attempt to revive a dead session"""
        try:
            async with Client(
                session_name,
                workdir=str(settings.SESSION_DIR),
                api_id=settings.API_ID,
                api_hash=settings.API_HASH
            ) as app:
                try:
                    await app.connect()
                    user = await app.get_me()
                    return True
                except (SessionRevoked, AuthKeyInvalid):
                    phone = f"+{session_name}"
                    sent_code = await app.send_code(phone)
                    code = input(f"Enter code for {phone}: ")
                    await app.sign_in(phone, sent_code.phone_code_hash, code)
                    return True
                except SessionPasswordNeeded:
                    password = input("Enter 2FA password: ")
                    await app.check_password(password)
                    return True
        except Exception as e:
            print(f"Revival failed: {str(e)}")
            return False