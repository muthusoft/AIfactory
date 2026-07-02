"""
Configuration management utilities.

Handles loading and managing application configuration.
"""

import yaml
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages application configuration."""

    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    def load(cls, config_file: str = "config/config.yaml") -> Dict[str, Any]:
        """
        Load configuration from file.

        Args:
            config_file: Path to configuration file

        Returns:
            Configuration dictionary
        """
        config_path = Path(config_file)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {config_file}")
            return {}

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Expand environment variables
            config = cls._expand_env_vars(config)
            
            cls._config = config
            logger.info(f"Configuration loaded from {config_file}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key (supports dot notation: "llm.provider")
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = cls._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value

    @staticmethod
    def _expand_env_vars(config: Any) -> Any:
        """
        Expand environment variables in configuration.

        Args:
            config: Configuration (dict, list, or value)

        Returns:
            Configuration with expanded environment variables
        """
        if isinstance(config, dict):
            return {k: ConfigManager._expand_env_vars(v) for k, v in config.items()}
        
        elif isinstance(config, list):
            return [ConfigManager._expand_env_vars(item) for item in config]
        
        elif isinstance(config, str):
            # Replace ${VAR_NAME} with environment variable
            if config.startswith('${') and config.endswith('}'):
                env_var = config[2:-1]
                return os.environ.get(env_var, config)
            return config
        
        else:
            return config


def load_config(config_file: str = "config/config.yaml") -> Dict[str, Any]:
    """Convenience function to load configuration."""
    manager = ConfigManager()
    return manager.load(config_file)


def get_config(key: str, default: Any = None) -> Any:
    """Convenience function to get configuration value."""
    manager = ConfigManager()
    return manager.get(key, default)
