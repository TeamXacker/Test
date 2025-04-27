# File: core/session/creator.py
import asyncio
from pyrogram import Client
from pyrogram.errors import FloodWait, SessionPasswordNeeded
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm
from config import Settings, constants
from core.utils.encryption import encrypt_session, decrypt_session
from core.utils.logger import log

class SessionCreator:

    @staticmethod
    async def create_session():
        """Enhanced session creation with all requested features"""
        
        phone_number = input(" Enter phone number (e.g: +1234567890): ").strip()
        if not phone_number:
            return
            
        if not phone_number.startswith("+") or not phone_number[1:].isdigit():
            print(f" {constants.RED}Invalid phone number format!{constants.RESET}")
            return
        
        session_name = phone_number.replace("+", "")
        session_file = Settings.SESSION_DIR / f"{session_name}.session"
        encrypted_file = Settings.SESSION_DIR / f"{session_name}.enc"
        
        if session_file.exists() or encrypted_file.exists():
            print(f" {constants.RED}Session already exists for this number!{constants.RESET}")
            return
        
        app = Client(str(session_file.with_suffix('')), api_id=Settings.API_ID, api_hash=Settings.API_HASH)

        try:
            await app.connect()

            # Send login code
            try:
                sent_code = await app.send_code(phone_number)
            except FloodWait as e:
                print(f" {constants.YELLOW}Flood wait: {e.value} seconds. Waiting...{constants.RESET}")
                await asyncio.sleep(e.value)
                sent_code = await app.send_code(phone_number)
            
            # Enter verification code
            code = input(" Enter the verification code: ").strip()
            
            try:
                await app.sign_in(phone_number, sent_code.phone_code_hash, code)
            except SessionPasswordNeeded:
                for attempt in range(3):
                    password = input(" Enter 2FA password: ")
                    try:
                        await app.check_password(password)
                        break  # Exit loop if password is correct
                    except PasswordHashInvalid:
                        print(f" {constants.RED}Incorrect 2FA password. Attempts left: {2 - attempt}{constants.RESET}")
                else:
                    print(f" {constants.RED}Too many incorrect 2FA attempts. Aborting.{constants.RESET}")
                    return
            except (PhoneCodeInvalid, PhoneCodeExpired) as e:
                print(f" {constants.RED}Verification failed: {type(e).__name__}{constants.RESET}")
                return
            
            # Export and encrypt the session
            session_string = await app.export_session_string()
            encrypted = encrypt_session(session_string, Settings.ENCRYPTION_KEY)

            # Save encrypted session
            with open(encrypted_file, "w") as f:
                f.write(encrypted)

            log(f"Session created for {phone_number}")
            print(f" {constants.GREEN}Session created and encrypted successfully!{constants.RESET}")
            
        except Exception as e:
            log(f"Session creation failed: {str(e)}", level="error")
            print(f" {constants.RED}Unexpected error: {str(e)}{constants.RESET}")
            if session_file.exists():
                session_file.unlink()
            if encrypted_file.exists():
                encrypted_file.unlink()

        finally:
            await app.disconnect()
    
    

    @staticmethod
    async def view_sessions():
        """View all sessions without progress bar, live printing"""
        session_files = list(Settings.SESSION_DIR.glob("*.session"))
        total_sessions = len(session_files)
    
        if total_sessions == 0:
            print(f" {constants.YELLOW}No sessions found!{constants.RESET}")
            return
    
        print(f"\n {constants.CYAN}Active Sessions ({total_sessions}):{constants.RESET}\n")
    
        for i, file in enumerate(session_files, 1):
            session_name = file.stem
            enc_file = Settings.SESSION_DIR / f"{session_name}.enc"
    
            if not enc_file.exists():
                print(f" {i}. {constants.RED}Encrypted session file not found for {session_name}{constants.RESET}")
                continue
    
            try:
                with open(enc_file) as f:
                    session_str = decrypt_session(f.read(), Settings.ENCRYPTION_KEY)
    
                async with Client(
                    f"{Settings.SESSION_DIR}/{session_name}",
                    session_string=session_str,
                    api_id=Settings.API_ID,
                    api_hash=Settings.API_HASH
                ) as app:
                    user = await app.get_me()
                    status = f"{constants.GREEN}✓{constants.RESET}"
                    print(f" {i}. {status} +{session_name}")
                    print(f"    Username: @{user.username} ({user.id})")
            
            except Exception as e:
                status = f"{constants.RED}✗{constants.RESET}"
                print(f" {i}. {status} +{session_name}")
                print(f"    {constants.RED}Error: {str(e)}{constants.RESET}")
    
        print()