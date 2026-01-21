"""Model lifecycle management for ML predictor"""
import joblib
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
from src.utils.logger import default_logger as logger


class ModelManager:
    """Manages ML model persistence, versioning, and performance tracking"""

    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize model manager.

        Args:
            models_dir: Directory to store models
        """
        if models_dir is None:
            models_dir = Path(__file__).parent.parent.parent / "models"

        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.models_dir / "metadata.json"
        self.model_file = self.models_dir / "current_model.pkl"
        self.backup_dir = self.models_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        self._metadata = self._load_metadata()

    def save_model(
        self,
        model: Any,
        performance_metrics: Optional[Dict[str, float]] = None,
        version_name: Optional[str] = None
    ):
        """
        Save model with metadata.

        Args:
            model: Model object to save
            performance_metrics: Performance metrics (MAE, RMSE, R2, etc.)
            version_name: Optional version name
        """
        # Create backup of current model if it exists
        if self.model_file.exists():
            self._backup_current_model()

        # Save model
        joblib.dump(model, self.model_file)

        # Update metadata
        timestamp = datetime.now().isoformat()
        version = version_name or f"v{len(self._metadata.get('versions', [])) + 1}"

        model_info = {
            'version': version,
            'timestamp': timestamp,
            'performance_metrics': performance_metrics or {},
            'file_path': str(self.model_file)
        }

        if 'versions' not in self._metadata:
            self._metadata['versions'] = []

        self._metadata['versions'].append(model_info)
        self._metadata['current_version'] = version
        self._metadata['last_updated'] = timestamp

        self._save_metadata()

        logger.info(f"Saved model version {version}")

    def load_model(self) -> Optional[Any]:
        """Load current model"""
        if not self.model_file.exists():
            logger.warning("No model file found")
            return None

        try:
            model = joblib.load(self.model_file)
            logger.info("Loaded model successfully")
            return model
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return None

    def get_metadata(self) -> Dict:
        """Get model metadata"""
        return self._metadata.copy()

    def get_current_version(self) -> Optional[str]:
        """Get current model version"""
        return self._metadata.get('current_version')

    def get_performance_history(self) -> List[Dict]:
        """Get performance metrics history"""
        versions = self._metadata.get('versions', [])
        return [
            {
                'version': v['version'],
                'timestamp': v['timestamp'],
                'metrics': v.get('performance_metrics', {})
            }
            for v in versions
        ]

    def get_latest_metrics(self) -> Dict[str, float]:
        """Get latest performance metrics"""
        versions = self._metadata.get('versions', [])
        if not versions:
            return {}

        return versions[-1].get('performance_metrics', {})

    def update_metrics(self, metrics: Dict[str, float]):
        """Update performance metrics for current model"""
        versions = self._metadata.get('versions', [])
        if versions:
            versions[-1]['performance_metrics'] = metrics
            self._save_metadata()
            logger.info(f"Updated model metrics: {metrics}")

    def reset_model(self):
        """Reset model (delete current model and metadata)"""
        # Backup before reset
        if self.model_file.exists():
            self._backup_current_model()
            self.model_file.unlink()

        # Reset metadata
        self._metadata = {
            'versions': [],
            'current_version': None,
            'created_at': datetime.now().isoformat()
        }
        self._save_metadata()

        logger.info("Model reset complete")

    def _backup_current_model(self):
        """Create backup of current model"""
        if not self.model_file.exists():
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = self._metadata.get('current_version', 'unknown')
        backup_file = self.backup_dir / f"model_{version}_{timestamp}.pkl"

        # Copy model file to backup
        import shutil
        shutil.copy2(self.model_file, backup_file)

        logger.info(f"Created model backup: {backup_file.name}")

        # Keep only last 5 backups
        self._cleanup_old_backups(keep=5)

    def _cleanup_old_backups(self, keep: int = 5):
        """Remove old backup files"""
        backups = sorted(
            self.backup_dir.glob("model_*.pkl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for old_backup in backups[keep:]:
            old_backup.unlink()
            logger.debug(f"Removed old backup: {old_backup.name}")

    def _load_metadata(self) -> Dict:
        """Load metadata from file"""
        if not self.metadata_file.exists():
            return {
                'versions': [],
                'created_at': datetime.now().isoformat()
            }

        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return {'versions': []}

    def _save_metadata(self):
        """Save metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self._metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    def get_training_stats(self) -> Dict[str, Any]:
        """Get training statistics"""
        versions = self._metadata.get('versions', [])

        if not versions:
            return {
                'total_versions': 0,
                'created_at': self._metadata.get('created_at'),
                'last_updated': None,
                'has_model': False
            }

        metrics_history = [v.get('performance_metrics', {}) for v in versions]

        # Calculate average metrics if available
        avg_metrics = {}
        if metrics_history:
            metric_keys = set()
            for m in metrics_history:
                metric_keys.update(m.keys())

            for key in metric_keys:
                values = [m.get(key, 0) for m in metrics_history if key in m]
                if values:
                    avg_metrics[f'avg_{key}'] = sum(values) / len(values)

        return {
            'total_versions': len(versions),
            'current_version': self._metadata.get('current_version'),
            'created_at': self._metadata.get('created_at'),
            'last_updated': self._metadata.get('last_updated'),
            'has_model': self.model_file.exists(),
            'latest_metrics': self.get_latest_metrics(),
            'average_metrics': avg_metrics,
            'improvement_trend': self._calculate_improvement_trend(metrics_history)}

    def _calculate_improvement_trend(self, metrics_history: List[Dict]) -> str:
        """Calculate whether model is improving, stable, or degrading"""
        if len(metrics_history) < 3:
            return 'insufficient_data'

        # Use MAE or first available metric
        recent = metrics_history[-3:]

        # Try common metrics
        for metric_key in ['mae', 'rmse', 'mse']:
            values = [m.get(metric_key) for m in recent if metric_key in m]
            if len(values) >= 2:
                # For error metrics, decreasing is improving
                if values[-1] < values[0] * 0.95:
                    return 'improving'
                elif values[-1] > values[0] * 1.05:
                    return 'degrading'
                else:
                    return 'stable'

        # Try R² (higher is better)
        values = [m.get('r2') for m in recent if 'r2' in m]
        if len(values) >= 2:
            if values[-1] > values[0] * 1.05:
                return 'improving'
            elif values[-1] < values[0] * 0.95:
                return 'degrading'
            else:
                return 'stable'

        return 'unknown'
