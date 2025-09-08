#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Dict, Any, Optional

class AppConfig:
    """Simple configuration management for the application."""
    
    def __init__(self):
        # Store config in user's home directory
        self.config_dir = Path.home() / '.config' / 'dircolor-editor'
        self.config_file = self.config_dir / 'config.json'
        
        # Default configuration
        self.defaults = {
            'preview_background_color': {
                'r': 0.1,
                'g': 0.1, 
                'b': 0.1,
                'a': 1.0
            },
            'window_width': 1200,
            'window_height': 800,
        }
        
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file.exists():
            return self.defaults.copy()
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults to handle missing keys
                merged = self.defaults.copy()
                merged.update(config)
                return merged
        except (json.JSONDecodeError, IOError):
            print(f"Warning: Could not load config from {self.config_file}")
            return self.defaults.copy()
            
    def save_config(self) -> bool:
        """Save current configuration to file."""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError as e:
            print(f"Warning: Could not save config to {self.config_file}: {e}")
            return False
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self.config[key] = value
        
    def get_background_color(self) -> Dict[str, float]:
        """Get the preview background color."""
        return self.config['preview_background_color']
        
    def set_background_color(self, r: float, g: float, b: float, a: float = 1.0) -> None:
        """Set the preview background color."""
        self.config['preview_background_color'] = {
            'r': r, 'g': g, 'b': b, 'a': a
        }
        self.save_config()
        
    def get_window_size(self) -> tuple[int, int]:
        """Get the window size."""
        return (self.config['window_width'], self.config['window_height'])
        
    def set_window_size(self, width: int, height: int) -> None:
        """Set the window size."""
        self.config['window_width'] = width
        self.config['window_height'] = height
        self.save_config()

# Global config instance
app_config = AppConfig()