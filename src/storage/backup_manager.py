"""Backup and restore functionality for application data"""
import zipfile
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from src.utils.logger import default_logger as logger


class BackupManager:
    """Manages data backup and restore operations"""

    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize backup manager.

        Args:
            backup_dir: Directory to store backups
        """
        if backup_dir is None:
            backup_dir = Path(__file__).parent.parent.parent / "backups"

        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.app_dir = Path(__file__).parent.parent.parent

        logger.info(f"Backup manager initialized: {self.backup_dir}")

    def create_backup(
            self,
            backup_name: Optional[str] = None) -> Optional[Path]:
        """
        Create a backup of all application data.

        Args:
            backup_name: Optional custom backup name

        Returns:
            Path to created backup file, or None if failed
        """
        try:
            # Generate backup filename
            if backup_name is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"backup_{timestamp}.zip"

            if not backup_name.endswith('.zip'):
                backup_name += '.zip'

            backup_path = self.backup_dir / backup_name

            # Create zip file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup database
                db_file = self.app_dir / "data" / "fatigue_tracker.db"
                if db_file.exists():
                    zipf.write(db_file, "data/fatigue_tracker.db")

                # Backup config
                config_file = self.app_dir / "config" / "user_config.json"
                if config_file.exists():
                    zipf.write(config_file, "config/user_config.json")

                # Backup ML models
                models_dir = self.app_dir / "models"
                if models_dir.exists():
                    for model_file in models_dir.rglob("*.pkl"):
                        rel_path = model_file.relative_to(self.app_dir)
                        zipf.write(model_file, str(rel_path))
                    for meta_file in models_dir.rglob("*.json"):
                        rel_path = meta_file.relative_to(self.app_dir)
                        zipf.write(meta_file, str(rel_path))

                # Backup user profiles
                profiles_dir = self.app_dir / "data" / "profiles"
                if profiles_dir.exists():
                    for profile_file in profiles_dir.rglob("*.json"):
                        rel_path = profile_file.relative_to(self.app_dir)
                        zipf.write(profile_file, str(rel_path))

                # Add backup metadata
                metadata = {
                    'created_at': datetime.now().isoformat(),
                    'version': '1.0.0',
                    'files_backed_up': zipf.namelist()
                }
                zipf.writestr(
                    'backup_metadata.json', json.dumps(
                        metadata, indent=2))

            logger.info(f"Created backup: {backup_path}")
            return backup_path

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None

    def restore_backup(self, backup_file: Path, confirm: bool = True) -> bool:
        """
        Restore data from a backup file.

        Args:
            backup_file: Path to backup zip file
            confirm: Whether to confirm before overwriting

        Returns:
            True if restore successful
        """
        try:
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_file}")
                return False

            # Validate backup
            if not zipfile.is_zipfile(backup_file):
                logger.error(f"Invalid backup file: {backup_file}")
                return False

            # Extract backup
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # Verify metadata
                try:
                    metadata_str = zipf.read(
                        'backup_metadata.json').decode('utf-8')
                    metadata = json.loads(metadata_str)
                    logger.info(
                        f"Restoring backup from {metadata['created_at']}")
                except Exception:
                    logger.warning(
                        "Backup metadata not found, proceeding anyway")

                # Extract all files
                zipf.extractall(self.app_dir)

            logger.info(f"Restored backup from {backup_file}")
            return True

        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return False

    def list_backups(self) -> List[dict]:
        """
        List all available backups.

        Returns:
            List of backup info dicts
        """
        backups = []

        for backup_file in self.backup_dir.glob("*.zip"):
            try:
                stats = backup_file.stat()

                # Try to get metadata
                metadata = None
                try:
                    with zipfile.ZipFile(backup_file, 'r') as zipf:
                        if 'backup_metadata.json' in zipf.namelist():
                            metadata = json.loads(
                                zipf.read('backup_metadata.json'))
                except Exception:
                    pass

                backups.append({
                    'file': backup_file,
                    'name': backup_file.name,
                    'size': stats.st_size,
                    'created': datetime.fromtimestamp(stats.st_mtime),
                    'metadata': metadata
                })
            except Exception as e:
                logger.error(f"Error reading backup {backup_file}: {e}")

        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)

        return backups

    def delete_backup(self, backup_file: Path) -> bool:
        """
        Delete a backup file.

        Args:
            backup_file: Path to backup file

        Returns:
            True if deleted successfully
        """
        try:
            if backup_file.exists():
                backup_file.unlink()
                logger.info(f"Deleted backup: {backup_file}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting backup: {e}")
            return False

    def auto_backup_on_exit(self, max_backups: int = 5):
        """
        Create automatic backup and manage backup count.

        Args:
            max_backups: Maximum number of backups to keep
        """
        # Create new backup
        self.create_backup()

        # Clean old backups
        backups = self.list_backups()
        if len(backups) > max_backups:
            for backup in backups[max_backups:]:
                self.delete_backup(backup['file'])
                logger.info(f"Removed old backup: {backup['name']}")
