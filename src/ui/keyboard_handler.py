"""Keyboard shortcut handler for the Cognitive Fatigue Tracker"""
import customtkinter as ctk
from typing import Callable, Dict, Optional
from src.utils.logger import default_logger as logger


class KeyboardHandler:
    """Manages keyboard shortcuts for the application"""
    
    def __init__(self, root: ctk.CTk):
        """
        Initialize keyboard handler.
        
        Args:
            root: Main application window
        """
        self.root = root
        self.shortcuts: Dict[str, Callable] = {}
        self.enabled = True
        
        # Setup key bindings
        self._setup_bindings()
        
        logger.info("Keyboard handler initialized")
    
    def _setup_bindings(self):
        """Setup keyboard event bindings"""
        # Bind all key events to the handler
        self.root.bind_all("<KeyPress>", self._on_key_press)
    
    def register_shortcut(self, key_combination: str, callback: Callable, description: str = ""):
        """
        Register a keyboard shortcut.
        
        Args:
            key_combination: Key combination (e.g., "<Control-b>", "<Control-Shift-S>")
            callback: Function to call when shortcut is triggered
            description: Human-readable description
        """
        self.shortcuts[key_combination.lower()] = {
            'callback': callback,
            'description': description
        }
        logger.debug(f"Registered shortcut: {key_combination} - {description}")
    
    def unregister_shortcut(self, key_combination: str):
        """Remove a keyboard shortcut"""
        key = key_combination.lower()
        if key in self.shortcuts:
            del self.shortcuts[key]
            logger.debug(f"Unregistered shortcut: {key_combination}")
    
    def _on_key_press(self, event):
        """Handle key press events"""
        if not self.enabled:
            return
        
        # Build key combination string
        modifiers = []
        if event.state & 0x0004:  # Control
            modifiers.append("Control")
        if event.state & 0x0001:  # Shift
            modifiers.append("Shift")
        if event.state & 0x0008 or event.state & 0x0080:  # Alt
            modifiers.append("Alt")
        
        # Get the key symbol
        key = event.keysym
        
        # Build the combination
        if modifiers:
            combination = f"<{'-'.join(modifiers)}-{key}>"
        else:
            combination = f"<{key}>"
        
        combination = combination.lower()
        
        # Check if this combination is registered
        if combination in self.shortcuts:
            try:
                self.shortcuts[combination]['callback']()
                logger.debug(f"Shortcut triggered: {combination}")
                return "break"  # Prevent further propagation
            except Exception as e:
                logger.error(f"Error executing shortcut {combination}: {e}")
    
    def enable(self):
        """Enable keyboard shortcuts"""
        self.enabled = True
        logger.info("Keyboard shortcuts enabled")
    
    def disable(self):
        """Disable keyboard shortcuts"""
        self.enabled = False
        logger.info("Keyboard shortcuts disabled")
    
    def get_shortcuts_list(self) -> list:
        """
        Get list of all registered shortcuts.
        
        Returns:
            List of (key_combination, description) tuples
        """
        return [
            (key.upper(), info['description']) 
            for key, info in self.shortcuts.items()
        ]
    
    def show_shortcuts_dialog(self):
        """Display a dialog with all keyboard shortcuts"""
        from src.ui.shortcuts_help_dialog import ShortcutsHelpDialog
        
        dialog = ShortcutsHelpDialog(self.root, self.get_shortcuts_list())
        dialog.grab_set()  # Make dialog modal
