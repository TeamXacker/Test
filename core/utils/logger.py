# File: core/utils/logger.py
import logging
import os
from datetime import datetime
from pathlib import Path
from config import Settings
from typing import Optional, Union

class ColorFormatter(logging.Formatter):
    """Custom log formatter with colors"""
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[31;1m' # Bold Red
    }
    RESET = '\033[0m'

    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        message = super().format(record)
        return f"{color}{message}{self.RESET}" if color else message

class BotLogger:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.loggers = {}
        self._setup_global_logging()
    
    def _setup_global_logging(self):
        """Configure root logger settings"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[]
        )
    
    def get_logger(
        self,
        name: str = "system",
        session_name: Optional[str] = None,
        level: Union[str, int] = logging.INFO
    ) -> logging.Logger:
        """Get or create a logger with specified configuration"""
        logger_name = f"{name}.{session_name}" if session_name else name
        
        if logger_name in self.loggers:
            return self.loggers[logger_name]
        
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        
        # Create log directory if not exists
        log_dir = Settings.LOG_DIR
        log_dir.mkdir(exist_ok=True, parents=True)
        
        # File handler (logs to file)
        log_file = log_dir / f"{logger_name}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler (colored output)
        console_handler = logging.StreamHandler()
        console_formatter = ColorFormatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        logger.propagate = False
        self.loggers[logger_name] = logger
        
        return logger
    
    def log(
        self,
        message: str,
        level: str = "info",
        session_name: Optional[str] = None,
        module: Optional[str] = None
    ):
        """Convenience method for quick logging"""
        logger_name = module or "system"
        logger = self.get_logger(logger_name, session_name)
        
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, message)
    
    def rotate_logs(self, max_size_mb: int = 10, backup_count: int = 5):
        """Rotate log files when they reach max size"""
        for handler in logging.root.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                log_path = Path(handler.baseFilename)
                if log_path.exists() and log_path.stat().st_size > max_size_mb * 1024 * 1024:
                    self._perform_rotation(log_path, backup_count)
    
    def _perform_rotation(self, log_path: Path, backup_count: int):
        """Handle actual log rotation"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create backup
        backup_path = log_path.parent / f"{log_path.stem}.backup.{timestamp}{log_path.suffix}"
        log_path.rename(backup_path)
        
        # Remove old backups if exceeding count
        backups = sorted(log_path.parent.glob(f"{log_path.stem}.backup.*{log_path.suffix}"))
        while len(backups) > backup_count:
            backups[0].unlink()
            backups = backups[1:]

def log(
    message: str,
    level: str = "info",
    session_name: Optional[str] = None,
    module: Optional[str] = None
):
    """Global logging shortcut function"""
    BotLogger().log(message, level, session_name, module)