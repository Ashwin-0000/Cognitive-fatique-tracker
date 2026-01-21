"""CSV export functionality for session data"""
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from src.storage.data_manager import DataManager
from src.utils.logger import default_logger as logger


class CSVExporter:
    """Export session data and statistics to CSV format"""

    def __init__(self, data_manager: DataManager):
        """
        Initialize CSV exporter.

        Args:
            data_manager: DataManager instance for accessing data
        """
        self.data_manager = data_manager

    def export_sessions(
        self,
        output_file: Path,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> bool:
        """
        Export session data to CSV.

        Args:
            output_file: Output CSV file path
            start_date: Start date filter (optional)
            end_date: End date filter (optional)

        Returns:
            True if export successful
        """
        try:
            # Get sessions from database
            sessions = self.data_manager.get_all_sessions(start_date, end_date)

            if not sessions:
                logger.warning("No sessions to export")
                return False

            # Write to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                # Header
                writer.writerow([
                    'Session ID',
                    'Start Time',
                    'End Time',
                    'Duration (minutes)',
                    'Work Duration (minutes)',
                    'Break Count',
                    'Total Activities',
                    'Average Fatigue',
                    'Max Fatigue',
                    'Status'
                ])

                # Data rows
                for session in sessions:
                    stats = session.get_stats()
                    writer.writerow([
                        session.session_id,
                        session.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                        session.end_time.strftime(
                            '%Y-%m-%d %H:%M:%S') if session.end_time else 'Active',
                        f"{stats['total_duration_minutes']:.1f}",
                        f"{stats['work_duration_minutes']:.1f}",
                        stats['break_count'],
                        stats['total_activity_count'],
                        '',  # Avg fatigue (would need to calculate)
                        '',  # Max fatigue
                        'Complete' if session.end_time else 'Active'
                    ])

            logger.info(f"Exported {len(sessions)} sessions to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error exporting sessions: {e}")
            return False

    def export_statistics(
        self,
        output_file: Path,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> bool:
        """
        Export statistics summary to CSV.

        Args:
            output_file: Output CSV file path
            start_date: Start date filter (optional)
            end_date: End date filter (optional)

        Returns:
            True if export successful
        """
        try:
            sessions = self.data_manager.get_all_sessions(start_date, end_date)

            if not sessions:
                return False

            # Calculate statistics
            total_duration = sum(
                s.get_stats()['total_duration_minutes'] for s in sessions)
            total_work = sum(
                s.get_stats()['work_duration_minutes'] for s in sessions)
            total_breaks = sum(s.get_stats()['break_count'] for s in sessions)
            total_activities = sum(
                s.get_stats()['total_activity_count'] for s in sessions)

            # Write summary
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)

                writer.writerow(['Metric', 'Value'])
                writer.writerow(['Total Sessions', len(sessions)])
                writer.writerow(['Total Duration (hours)',
                                f"{total_duration/60:.1f}"])
                writer.writerow(
                    ['Total Work Time (hours)', f"{total_work/60:.1f}"])
                writer.writerow(['Total Breaks', total_breaks])
                writer.writerow(['Total Activities', total_activities])
                writer.writerow(
                    ['Average Session Duration (minutes)', f"{total_duration/len(sessions):.1f}"])
                writer.writerow(['Average Breaks per Session',
                                f"{total_breaks/len(sessions):.1f}"])

            logger.info(f"Exported statistics to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error exporting statistics: {e}")
            return False
