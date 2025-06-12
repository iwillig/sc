"""Simple configuration manager for Shortcut CLI."""

import os
import yaml
from pathlib import Path
from typing import Optional


class ConfigManager:
    """Simple config manager for loading API token."""

    def __init__(self):
        self.config_dir = Path.home() / ".config" / "shortcut"
        self.config_file = self.config_dir / "config.yml"
        self.config = {}
        self.load()

    def load(self):
        """Load configuration from YAML file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
            except:
                self.config = {}

    def get_api_token(self) -> Optional[str]:
        """Get API token from config or environment."""
        # First check environment variable
        token = os.environ.get('SHORTCUT_API_TOKEN')
        if token:
            return token
        
        # Then check config file
        if 'auth' in self.config and 'token' in self.config['auth']:
            return self.config['auth']['token']
        
        return None


# Global instance
_config = None

def get_config() -> ConfigManager:
    """Get the config manager instance."""
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config