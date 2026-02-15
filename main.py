"""
Cognitive Fatigue Tracker
A Python application that monitors user activity and tracks cognitive fatigue levels.
"""
import sys
import traceback
import os
from pathlib import Path

# Suppress TensorFlow/Abseil/MediaPipe warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # FATAL
os.environ['ABSL_LOG_LEVEL'] = 'error'
os.environ['GLOG_minloglevel'] = '3'  # FATAL - Suppress ALL C++ GLOG (MediaPipe)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Suppress oneDNN warnings

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.ui.main_window import MainWindow
from src.utils.logger import default_logger as logger


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler to catch all uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow Ctrl+C to work normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    print(f"\n{'='*60}")
    print("FATAL ERROR - Application crashed")
    print(f"{'='*60}")
    print(f"Error: {exc_value}")
    print(f"\nPlease check logs/app_*.log for details")
    print(f"{'='*60}\n")


# Set global exception handler
sys.excepthook = handle_exception



def main():
    """Main application entry point"""
    try:
        logger.info("Starting Cognitive Fatigue Tracker")
        
        # Create and run application
        app = MainWindow()
        app.mainloop()
        
        logger.info("Application closed")
    
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\nError: {e}")
        print("Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
