"""Statistics analyzer for productivity analytics"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict
import statistics

from src.storage.data_manager import DataManager
from src.models.session import Session
from src.utils.logger import default_logger as logger


class StatisticsAnalyzer:
    """Analyzes session data to provide productivity insights"""

    def __init__(self, data_manager: DataManager):
        """
        Initialize statistics analyzer.

        Args:
            data_manager: DataManager instance
        """
        self.data_manager = data_manager

    def get_weekly_stats(self) -> Dict:
        """Get statistics for the last 7 days"""
        start_date = datetime.now() - timedelta(days=7)
        return self._calculate_stats(start_date, datetime.now())

    def get_monthly_stats(self) -> Dict:
        """Get statistics for the last 30 days"""
        start_date = datetime.now() - timedelta(days=30)
        return self._calculate_stats(start_date, datetime.now())

    def get_productivity_by_hour(self, days: int = 30) -> Dict[int, float]:
        """
        Analyze productivity by hour of day.

        Args:
            days: Number of days to analyze

        Returns:
            Dict mapping hour (0-23) to average productivity score
        """
        start_date = datetime.now() - timedelta(days=days)
        sessions = self.data_manager.get_all_sessions(
            start_date, datetime.now())

        hourly_data = defaultdict(list)

        for session in sessions:
            hour = session.start_time.hour
            stats = session.get_stats()

            # Calculate productivity score (activity per minute)
            if stats['total_duration_minutes'] > 0:
                productivity = stats['total_activity_count'] / \
                    stats['total_duration_minutes']
                hourly_data[hour].append(productivity)

        # Calculate averages
        hourly_avg = {}
        for hour in range(24):
            if hour in hourly_data and hourly_data[hour]:
                hourly_avg[hour] = statistics.mean(hourly_data[hour])
            else:
                hourly_avg[hour] = 0.0

        return hourly_avg

    def get_best_work_hours(self, days: int = 30) -> List[int]:
        """
        Identify best work hours based on productivity.

        Args:
            days: Number of days to analyze

        Returns:
            List of hours (sorted by productivity)
        """
        hourly_prod = self.get_productivity_by_hour(days)

        # Sort by productivity
        sorted_hours = sorted(
            hourly_prod.items(),
            key=lambda x: x[1],
            reverse=True)

        # Return top 5 hours
        return [hour for hour, _ in sorted_hours[:5]]

    def get_daily_trends(self, days: int = 30) -> Dict[str, List]:
        """
        Get daily trends for various metrics.

        Args:
            days: Number of days to analyze

        Returns:
            Dict with daily data series
        """
        start_date = datetime.now() - timedelta(days=days)
        sessions = self.data_manager.get_all_sessions(
            start_date, datetime.now())

        # Group by date
        daily_data = defaultdict(lambda: {
            'total_time': 0,
            'work_time': 0,
            'breaks': 0,
            'activities': 0,
            'sessions': 0
        })

        for session in sessions:
            date_key = session.start_time.date().isoformat()
            stats = session.get_stats()

            daily_data[date_key]['total_time'] += stats['total_duration_minutes']
            daily_data[date_key]['work_time'] += stats['work_duration_minutes']
            daily_data[date_key]['breaks'] += stats['break_count']
            daily_data[date_key]['activities'] += stats['total_activity_count']
            daily_data[date_key]['sessions'] += 1

        # Convert to lists
        dates = sorted(daily_data.keys())
        return {
            'dates': dates,
            'total_time': [daily_data[d]['total_time'] for d in dates],
            'work_time': [daily_data[d]['work_time'] for d in dates],
            'breaks': [daily_data[d]['breaks'] for d in dates],
            'activities': [daily_data[d]['activities'] for d in dates],
            'sessions': [daily_data[d]['sessions'] for d in dates]
        }

    def get_streak_info(self) -> Dict:
        """
        Calculate streak information (consecutive days with sessions).

        Returns:
            Dict with current streak and longest streak
        """
        # Get all sessions
        sessions = self.data_manager.get_all_sessions()

        if not sessions:
            return {
                'current_streak': 0,
                'longest_streak': 0,
                'last_session_date': None}

        # Get unique dates
        session_dates = sorted(set(s.start_time.date() for s in sessions))

        # Calculate current streak
        current_streak = 0
        today = datetime.now().date()

        for i in range(len(session_dates)):
            expected_date = today - timedelta(days=i)
            if expected_date in session_dates:
                current_streak += 1
            else:
                break

        # Calculate longest streak
        longest_streak = 1
        current_run = 1

        for i in range(1, len(session_dates)):
            if (session_dates[i] - session_dates[i - 1]).days == 1:
                current_run += 1
                longest_streak = max(longest_streak, current_run)
            else:
                current_run = 1

        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'last_session_date': session_dates[-1] if session_dates else None
        }

    def _calculate_stats(
            self,
            start_date: datetime,
            end_date: datetime) -> Dict:
        """Calculate statistics for a date range"""
        sessions = self.data_manager.get_all_sessions(start_date, end_date)

        if not sessions:
            return {
                'total_sessions': 0,
                'total_time': 0,
                'total_work_time': 0,
                'total_breaks': 0,
                'avg_session_length': 0,
                'avg_breaks_per_session': 0,
                'total_activities': 0
            }

        total_time = sum(
            s.get_stats()['total_duration_minutes'] for s in sessions)
        total_work = sum(
            s.get_stats()['work_duration_minutes'] for s in sessions)
        total_breaks = sum(s.get_stats()['break_count'] for s in sessions)
        total_activities = sum(
            s.get_stats()['total_activity_count'] for s in sessions)

        return {
            'total_sessions': len(sessions),
            'total_time': total_time,
            'total_work_time': total_work,
            'total_breaks': total_breaks,
            'avg_session_length': total_time / len(sessions),
            'avg_breaks_per_session': total_breaks / len(sessions),
            'total_activities': total_activities
        }
