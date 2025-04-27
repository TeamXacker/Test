# File: core/anti_ban/actions.py
import random
import time
import asyncio
from typing import AsyncGenerator
from config import settings

class AntiBan:
    """Advanced anti-detection system for Telegram automation"""
    
    # Class variables for global settings
    enabled = True
    random_delay_enabled = True
    human_typing_enabled = False
    max_actions_per_hour = 50
    
    @staticmethod
    async def random_delay(min_sec: float = 1, max_sec: float = 5) -> None:
        """Random delay between actions to mimic human behavior"""
        if AntiBan.random_delay_enabled and AntiBan.enabled:
            delay = random.uniform(min_sec, max_sec)
            await asyncio.sleep(delay)
    
    @staticmethod
    async def action_delay() -> None:
        """Standard delay between major actions"""
        await AntiBan.random_delay(2, 10)
    
    @classmethod
    async def human_typing(cls, text: str) -> AsyncGenerator[str, None]:
        """Simulate human typing speed"""
        if cls.human_typing_enabled and cls.enabled:
            for char in text:
                await asyncio.sleep(random.uniform(0.05, 0.3))
                yield char
        else:
            yield text
    
    @classmethod
    def calculate_action_limit(cls) -> int:
        """Randomize daily action limits"""
        if not cls.enabled:
            return cls.max_actions_per_hour
        
        variation = cls.max_actions_per_hour * 0.2  # 20% variation
        return random.randint(
            int(cls.max_actions_per_hour - variation),
            int(cls.max_actions_per_hour + variation)
        )
    
    @classmethod
    async def random_action_skip(cls, skip_chance: float = 0.1) -> bool:
        """Randomly skip actions to appear more human-like"""
        if cls.enabled and random.random() < skip_chance:
            await cls.random_delay(3, 7)
            return True
        return False