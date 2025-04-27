# File: core/anti_ban/fingerprints.py
import random
from dataclasses import dataclass
from typing import Dict

@dataclass
class DeviceFingerprint:
    """Class to generate and manage device fingerprints"""
    
    device_model: str
    system_version: str
    app_version: str
    lang_code: str = "en"
    
    @classmethod
    def random_android(cls) -> 'DeviceFingerprint':
        """Generate random Android device fingerprint"""
        models = [
            "Samsung Galaxy S23",
            "Google Pixel 7",
            "Xiaomi Redmi Note 12",
            "OnePlus 11",
            "Sony Xperia 1 IV"
        ]
        versions = [
            "10", "11", "12", "13"
        ]
        app_versions = [
            "9.4.0", "9.3.5", "9.2.1", "8.9.2"
        ]
        
        return cls(
            device_model=random.choice(models),
            system_version=random.choice(versions),
            app_version=random.choice(app_versions)
        )
    
    def to_dict(self) -> Dict[str, str]:
        """Convert fingerprint to dictionary"""
        return {
            "device_model": self.device_model,
            "system_version": self.system_version,
            "app_version": self.app_version,
            "lang_code": self.lang_code
        }