"""Enhanced logger with state tracking for debugging"""
import logging
import sys
from pathlib import Path
from datetime import datetime
import json


# Create logs directory if it doesn't exist
log_dir = Path(__file__).parent.parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

# Create debug logs directory
debug_log_dir = log_dir / "debug"
debug_log_dir.mkdir(exist_ok=True)


def setup_logger(name: str, debug_mode: bool = False) -> logging.Logger:
    """
    Setup logger with file and console handlers.
    
    Args:
        name: Logger name
        debug_mode: Enable debug level logging
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


class StateLogger:
    """Logger for tracking application state changes"""
    
    def __init__(self, name: str):
        self.logger = setup_logger(f"{name}.state", debug_mode=True)
        self.state_file = debug_log_dir / f"state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.states = []
    
    def log_state(self, component: str, action: str, state: dict):
        """
        Log a state change.
        
        Args:
            component: Component name (e.g., "EyeTracker", "Dashboard")
            action: Action being performed
            state: State dictionary
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "action": action,
            "state": state
        }
        
        self.states.append(entry)
        self.logger.debug(f"{component}.{action}: {state}")
        
        # Save to file periodically
        if len(self.states) % 10 == 0:
            self._save_states()
    
    def _save_states(self):
        """Save states to JSON file"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.states, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save states: {e}")


# Default logger
default_logger = setup_logger("CognitiveFatigueTracker")

# State logger for debugging
state_logger = StateLogger("CognitiveFatigueTracker")
