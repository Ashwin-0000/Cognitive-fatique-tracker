"""Screenshot manager for capturing charts and dashboard"""
from pathlib import Path
from typing import Optional
from datetime import datetime
import io
from PIL import Image

from src.utils.logger import default_logger as logger


class ScreenshotManager:
    """Manages screenshot capture of charts and UI elements"""
    
    def __init__(self, screenshots_dir: Optional[Path] = None):
        """
        Initialize screenshot manager.
        
        Args:
            screenshots_dir: Directory to save screenshots
        """
        if screenshots_dir is None:
            screenshots_dir = Path(__file__).parent.parent.parent / "screenshots"
        
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Screenshot manager initialized: {self.screenshots_dir}")
    
    def save_matplotlib_figure(
        self,
        figure,
        filename: Optional[str] = None,
        format: str = 'png',
        dpi: int = 300
    ) -> Optional[Path]:
        """
        Save matplotlib figure as image.
        
        Args:
            figure: Matplotlib figure object
            filename: Output filename (auto-generated if None)
            format: Image format (png, jpg, svg)
            dpi: DPI resolution
        
        Returns:
            Path to saved screenshot
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"chart_{timestamp}.{format}"
            
            if not filename.endswith(f'.{format}'):
                filename += f'.{format}'
            
            output_path = self.screenshots_dir / filename
            
            # Save figure
            figure.savefig(
                output_path,
                format=format,
                dpi=dpi,
                bbox_inches='tight',
                facecolor='white'
            )
            
            logger.info(f"Saved chart screenshot: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving chart screenshot: {e}")
            return None
    
    def save_widget_screenshot(
        self,
        widget,
        filename: Optional[str] = None,
        format: str = 'png'
    ) -> Optional[Path]:
        """
        Save CustomTkinter widget as screenshot.
        
        Args:
            widget: CustomTkinter widget
            filename: Output filename
            format: Image format
        
        Returns:
            Path to saved screenshot
        """
        try:
            if filename is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"dashboard_{timestamp}.{format}"
            
            if not filename.endswith(f'.{format}'):
                filename += f'.{format}'
            
            output_path = self.screenshots_dir / filename
            
            # For CustomTkinter, we'd need to use a different approach
            # This is a placeholder - actual implementation would depend on the widget type
            logger.warning("Widget screenshot not fully implemented")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving widget screenshot: {e}")
            return None
    
    def get_screenshot_path(self, filename: str) -> Path:
        """Get full path for a screenshot filename"""
        return self.screenshots_dir / filename
