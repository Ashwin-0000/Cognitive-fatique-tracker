"""Theme customization manager"""
from pathlib import Path
from typing import Optional, Dict
import json
from src.utils.logger import default_logger as logger


class ThemeManager:
    """Manages custom color themes and appearance"""

    PRESET_THEMES = {
        'default_dark': {
            'name': 'Default Dark',
            'mode': 'dark',
            'primary': '#3498db',
            'success': '#2ecc71',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'background': '#2c3e50',
            'surface': '#34495e',
            'text': '#ecf0f1'
        },
        'default_light': {
            'name': 'Default Light',
            'mode': 'light',
            'primary': '#2980b9',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#c0392b',
            'background': '#ecf0f1',
            'surface': '#ffffff',
            'text': '#2c3e50'
        },
        'ocean': {
            'name': 'Ocean',
            'mode': 'dark',
            'primary': '#3498db',
            'success': '#1abc9c',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'background': '#1a252f',
            'surface': '#273849',
            'text': '#ecf0f1'
        },
        'forest': {
            'name': 'Forest',
            'mode': 'dark',
            'primary': '#27ae60',
            'success': '#2ecc71',
            'warning': '#f1c40f',
            'danger': '#e67e22',
            'background': '#1e3a2b',
            'surface': '#2d5f3f',
            'text': '#ecf0f1'
        },
        'sunset': {
            'name': 'Sunset',
            'mode': 'dark',
            'primary': '#e67e22',
            'success': '#f39c12',
            'warning': '#e74c3c',
            'danger': '#c0392b',
            'background': '#2c1e1e',
            'surface': '#3d2a2a',
            'text': '#ecf0f1'
        }
    }

    def __init__(self, themes_file: Optional[Path] = None):
        """
        Initialize theme manager.

        Args:
            themes_file: File to store custom themes
        """
        if themes_file is None:
            themes_file = Path(__file__).parent.parent.parent / \
                "config" / "themes.json"

        self.themes_file = Path(themes_file)
        self.themes_file.parent.mkdir(parents=True, exist_ok=True)

        self.custom_themes = self._load_themes()
        self.active_theme = 'default_dark'

        logger.info("Theme manager initialized")

    def _load_themes(self) -> Dict:
        """Load custom themes"""
        if self.themes_file.exists():
            try:
                with open(self.themes_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading themes: {e}")

        return {}

    def _save_themes(self):
        """Save custom themes"""
        try:
            with open(self.themes_file, 'w') as f:
                json.dump(self.custom_themes, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving themes: {e}")

    def get_theme(self, theme_id: str) -> Optional[Dict]:
        """Get a theme by ID"""
        if theme_id in self.PRESET_THEMES:
            return self.PRESET_THEMES[theme_id]
        return self.custom_themes.get(theme_id)

    def get_all_themes(self) -> Dict:
        """Get all available themes"""
        all_themes = self.PRESET_THEMES.copy()
        all_themes.update(self.custom_themes)
        return all_themes

    def create_custom_theme(self, theme_id: str, theme_data: Dict) -> bool:
        """
        Create a custom theme.

        Args:
            theme_id: Unique theme ID
            theme_data: Theme configuration

        Returns:
            True if created successfully
        """
        if theme_id in self.PRESET_THEMES:
            return False

        self.custom_themes[theme_id] = theme_data
        self._save_themes()
        return True

    def delete_custom_theme(self, theme_id: str) -> bool:
        """Delete a custom theme"""
        if theme_id in self.custom_themes:
            del self.custom_themes[theme_id]
            self._save_themes()
            return True
        return False

    def set_active_theme(self, theme_id: str):
        """Set the active theme"""
        if self.get_theme(theme_id):
            self.active_theme = theme_id
            logger.info(f"Active theme set to: {theme_id}")

    def get_active_theme(self) -> Dict:
        """Get the currently active theme"""
        return self.get_theme(
            self.active_theme) or self.PRESET_THEMES['default_dark']
