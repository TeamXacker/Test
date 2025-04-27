# File: config/settings.py
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Settings:
    # Telegram API
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    SESSION_DIR = Path("storage/sessions")
    BACKUP_DIR = Path("storage/backups")
    
    # Security
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "32_character_secure_key_here!!")
    MAX_LOGIN_ATTEMPTS = 3
    
    # Health Check
    HEALTH_CHECK_INTERVAL = 3600  # 1 hour
    
    # Logging Settings
    LOG_DIR = Path("storage/logs")
    MAX_LOG_SIZE = 10  # MB
    LOG_BACKUP_COUNT = 5
    DEFAULT_LOG_LEVEL = "INFO"  # DEBUG/INFO/WARNING/ERROR/CRITICAL
    
    @classmethod
    def validate(cls):
        cls.SESSION_DIR.mkdir(exist_ok=True, parents=True)
        cls.BACKUP_DIR.mkdir(exist_ok=True, parents=True)
        cls.LOG_DIR.mkdir(exist_ok=True, parents=True)

Settings.validate()