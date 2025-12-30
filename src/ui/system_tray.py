"""System tray icon for the Cognitive Fatigue Tracker"""
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from typing import Callable, Optional
import threading
from src.utils.logger import default_logger as logger


class SystemTray:
    """Manages system tray icon and menu"""
    
    def __init__(self):
        """Initialize system tray"""
        self.icon: Optional[pystray.Icon] = None
        self.callbacks = {
            'show': None,
            'hide': None,
            'start_session': None,
            'stop_session': None,
            'take_break': None,
            'settings': None,
            'quit': None
        }
        
        # Create icon image
        self.image = self._create_icon_image()
        
        logger.info("System tray initialized")
    
    def _create_icon_image(self) -> Image.Image:
        """
        Create a simple icon image for the system tray.
        
        Returns:
            PIL Image for the tray icon
        """
        # Create a 64x64 image with a simple design
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), color=(30, 30, 30))
        dc = ImageDraw.Draw(image)
        
        # Draw a brain icon (simplified circle with details)
        # Outer circle
        dc.ellipse([8, 8, 56, 56], fill=(100, 100, 255), outline=(150, 150, 255), width=2)
        
        # Inner details (simplified brain squiggles)
        dc.arc([12, 16, 52, 48], 0, 180, fill=(150, 150, 255), width=3)
        dc.arc([20, 24, 44, 40], 180, 360, fill=(150, 150, 255), width=3)
        
        return image
    
    def set_callback(self, action: str, callback: Callable):
        """
        Set callback for a tray action.
        
        Args:
            action: Action name (show, hide, start_session, etc.)
            callback: Function to call
        """
        if action in self.callbacks:
            self.callbacks[action] = callback
            logger.debug(f"Set tray callback for: {action}")
    
    def _on_show(self, icon, item):
        """Show main window"""
        if self.callbacks['show']:
            self.callbacks['show']()
    
    def _on_hide(self, icon, item):
        """Hide main window"""
        if self.callbacks['hide']:
            self.callbacks['hide']()
    
    def _on_start_session(self, icon, item):
        """Start session"""
        if self.callbacks['start_session']:
            self.callbacks['start_session']()
    
    def _on_stop_session(self, icon, item):
        """Stop session"""
        if self.callbacks['stop_session']:
            self.callbacks['stop_session']()
    
    def _on_take_break(self, icon, item):
        """Take break"""
        if self.callbacks['take_break']:
            self.callbacks['take_break']()
    
    def _on_settings(self, icon, item):
        """Open settings"""
        if self.callbacks['settings']:
            self.callbacks['settings']()
    
    def _on_quit(self, icon, item):
        """Quit application"""
        if self.callbacks['quit']:
            self.callbacks['quit']()
        self.stop()
    
    def _create_menu(self):
        """Create the tray menu"""
        return pystray.Menu(
            item('Show Window', self._on_show, default=True),
            item('Hide Window', self._on_hide),
            pystray.Menu.SEPARATOR,
            item('Start Session', self._on_start_session),
            item('Stop Session', self._on_stop_session),
            item('Take Break', self._on_take_break),
            pystray.Menu.SEPARATOR,
            item('Settings', self._on_settings),
            item('Quit', self._on_quit)
        )
    
    def start(self):
        """Start the system tray icon"""
        if self.icon is not None:
            logger.warning("System tray already started")
            return
        
        self.icon = pystray.Icon(
            name="CognitiveFatigueTracker",
            icon=self.image,
            title="Cognitive Fatigue Tracker",
            menu=self._create_menu()
        )
        
        # Run in separate thread
        threading.Thread(target=self.icon.run, daemon=True).start()
        logger.info("System tray icon started")
    
    def stop(self):
        """Stop the system tray icon"""
        if self.icon:
            self.icon.stop()
            self.icon = None
            logger.info("System tray icon stopped")
    
    def update_tooltip(self, text: str):
        """Update the tray icon tooltip"""
        if self.icon:
            self.icon.title = f"Cognitive Fatigue Tracker - {text}"
    
    def show_notification(self, title: str, message: str):
        """
        Show a notification from the tray icon.
        
        Args:
            title: Notification title
            message: Notification message
        """
        if self.icon:
            try:
                self.icon.notify(title=title, message=message)
                logger.debug(f"Tray notification: {title}")
            except Exception as e:
                logger.error(f"Failed to show tray notification: {e}")
