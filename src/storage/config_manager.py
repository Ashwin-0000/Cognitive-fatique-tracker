"""Configuration manager for user settings"""
import json
from pathlib import Path
from typing import Any, Optional
from src.utils.logger import default_logger as logger


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing config files
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "config"
        
        self.config_dir = Path(config_dir)
        self.default_config_path = self.config_dir / "default_settings.json"
        self.user_config_path = self.config_dir / "user_settings.json"
        
        self._config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from files"""
        # Load default config
        try:
            with open(self.default_config_path, 'r') as f:
                config = json.load(f)
            logger.info("Loaded default configuration")
        except Exception as e:
            logger.error(f"Failed to load default config: {e}")
            config = {}
        
        # Override with user config if exists
        if self.user_config_path.exists():
            try:
                with open(self.user_config_path, 'r') as f:
                    user_config = json.load(f)
                config.update(user_config)
                logger.info("Loaded user configuration")
            except Exception as e:
                logger.warning(f"Failed to load user config: {e}")
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'ui.theme')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        logger.debug(f"Set config {key} = {value}")
    
    def save(self):
        """Save current configuration to user config file"""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.user_config_path, 'w') as f:
                json.dump(self._config, f, indent=2)
            logger.info("Saved user configuration")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def reset_to_default(self):
        """Reset configuration to defaults"""
        self._config = self._load_config()
        if self.user_config_path.exists():
            self.user_config_path.unlink()
        logger.info("Reset configuration to defaults")
    
    def get_all(self) -> dict:
        """Get all configuration"""
        return self._config.copy()
