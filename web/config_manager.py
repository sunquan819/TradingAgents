import os
import json
from pathlib import Path
from typing import Dict, Optional

CONFIG_FILE = Path.home() / ".tradingagents" / "web_config.json"

def load_config() -> Dict:
    """Load saved configuration from file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(config: Dict) -> bool:
    """Save configuration to file."""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def clear_config() -> bool:
    """Clear saved configuration."""
    try:
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        return True
    except Exception as e:
        print(f"Error clearing config: {e}")
        return False

def get_api_key_from_config(provider: str) -> Optional[str]:
    """Get API key for a provider from saved config."""
    config = load_config()
    return config.get("api_keys", {}).get(provider)

def save_api_key(provider: str, api_key: str) -> bool:
    """Save API key for a provider."""
    config = load_config()
    config.setdefault("api_keys", {})
    config["api_keys"][provider] = api_key
    return save_config(config)

def get_all_saved_api_keys() -> Dict[str, str]:
    """Get all saved API keys."""
    config = load_config()
    return config.get("api_keys", {})

def save_settings(settings: Dict) -> bool:
    """Save general settings (provider, models, etc.)."""
    config = load_config()
    config["settings"] = settings
    return save_config(config)

def get_saved_settings() -> Dict:
    """Get saved general settings."""
    config = load_config()
    return config.get("settings", {})

def get_config_file_path() -> Path:
    """Get the path to the config file."""
    return CONFIG_FILE