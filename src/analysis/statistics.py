"""Statistics Manager for aggregating user data"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from src.storage.data_manager import DataManager
from src.utils.logger import default_logger as logger

class StatisticsManager:
    """Aggregates data for statistics dashboard"""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager

    def get_weekly_summary(self, days: int = 7) -> List[Dict]:
        """
        Get daily summary of active hours and average fatigue.
        Returns list of dicts: {'date': str, 'active_hours': float, 'avg_fatigue': float}
        """
        summary = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days-1)
        
        # Get all sessions in range
        sessions = self.data_manager.get_recent_sessions(days=days)
        
        # Fallback: If no sessions in last 7 days, try 30 days to show *something*
        if not sessions and days < 30:
            sessions = self.data_manager.get_recent_sessions(days=30)
            # Adjust start date to match the data we found, or keep it as is
            if sessions:
                 start_date = datetime.now() - timedelta(days=29)
        
        # Group by date
        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            day_sessions = [s for s in sessions if s.start_time.strftime("%Y-%m-%d") == date_str]
            
            total_seconds = 0
            fatigue_sum = 0
            fatigue_count = 0
            
            for session in day_sessions:
                # Calculate duration
                start = session.start_time
                end = session.end_time if session.end_time else datetime.now()
                duration = (end - start).total_seconds()
                total_seconds += duration
                
                # Get fatigue scores for this session
                scores = self.data_manager.get_fatigue_scores(session.session_id)
                if scores:
                    fatigue_sum += sum(s.score for s in scores)
                    fatigue_count += len(scores)
            
            avg_fatigue = fatigue_sum / fatigue_count if fatigue_count > 0 else 0
            active_hours = total_seconds / 3600
            
            summary.append({
                'date': current.strftime("%a"), # Mon, Tue, etc.
                'full_date': date_str,
                'active_hours': round(active_hours, 1),
                'avg_fatigue': round(avg_fatigue, 1)
            })
            
            current += timedelta(days=1)
            
        return summary

    def get_productivity_stats(self, days: int = 7) -> Dict:
        """
        Get productivity metrics.
        Returns: {'focus_score': float, 'peak_hour': str}
        """
        sessions = self.data_manager.get_recent_sessions(days=days)
        
        total_actions = 0
        total_minutes = 0
        hourly_activity = {h: 0 for h in range(24)}
        
        for session in sessions:
            # Calculate total actions
            total_actions += session.total_activity_count
            
            # Calculate duration in minutes
            start = session.start_time
            end = session.end_time if session.end_time else datetime.now()
            duration_mins = (end - start).total_seconds() / 60
            total_minutes += duration_mins
            
            # Track peak hours (simplified: just use start time hour)
            hourly_activity[start.hour] += session.total_activity_count
            
        # Focus Score: Actions per minute
        focus_score = total_actions / total_minutes if total_minutes > 0 else 0
        
        # Peak Hour
        if max(hourly_activity.values()) > 0:
            peak_hour_idx = max(hourly_activity, key=hourly_activity.get)
            peak_hour_str = f"{peak_hour_idx:02d}:00 - {(peak_hour_idx+1)%24:02d}:00"
        else:
            peak_hour_str = "--:--"
        
        return {
            'focus_score': round(focus_score, 1),
            'peak_hour': peak_hour_str
        }

    def get_break_effectiveness(self, days: int = 30) -> Dict:
        """
        Get break effectiveness stats.
        Returns: {'recovery_rate': float, 'total_breaks': int}
        """
        history = self.data_manager.get_activity_history(days=days)
        
        total_drop = 0
        count = 0
        
        for entry in history:
            before = entry.get('fatigue_before')
            after = entry.get('fatigue_after')
            
            if before is not None and after is not None:
                drop = before - after
                if drop > 0: # Only count positive recovery
                    total_drop += drop
                    count += 1
                    
        avg_recovery = total_drop / count if count > 0 else 0
        
        return {
            'recovery_rate': round(avg_recovery, 1),
            'total_breaks': len(history)
        }
    def get_daily_screen_time(self) -> str:
        """
        Get total screen time for today (or last active day if today is 0).
        Returns formatted string "Today: HH:MM" or "Last: HH:MM"
        """
        # Try today first
        sessions = self.data_manager.get_recent_sessions(days=1)
        today_str = datetime.now().strftime("%Y-%m-%d")
        total_seconds = 0
        target_date = "Today"
        
        for session in sessions:
            if session.start_time.strftime("%Y-%m-%d") == today_str:
                start = session.start_time
                end = session.end_time if session.end_time else datetime.now()
                total_seconds += (end - start).total_seconds()
        
        # If no time today, look back 7 days for last active
        if total_seconds == 0:
            sessions = self.data_manager.get_recent_sessions(days=7)
            if sessions:
                last_session = sessions[-1]
                target_date_obj = last_session.start_time
                target_date = target_date_obj.strftime("%b %d")
                
                # Calculate total for that specific day
                day_str = target_date_obj.strftime("%Y-%m-%d")
                for session in sessions:
                    if session.start_time.strftime("%Y-%m-%d") == day_str:
                        start = session.start_time
                        end = session.end_time if session.end_time else datetime.now()
                        total_seconds += (end - start).total_seconds()

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        return f"{target_date}: {hours}h {minutes}m"

    def get_weekly_input_volume(self) -> int:
        """
        Get total input events (keys + clicks) for the last 7 days.
        """
        sessions = self.data_manager.get_recent_sessions(days=7)
        return sum(s.total_activity_count for s in sessions)

    def get_fatigue_distribution(self, days: int = 7) -> Dict[str, float]:
        """
        Get distribution of time spent in each fatigue zone.
        Returns dict with percentage for 'Low', 'Medium', 'High', 'Critical'.
        """
        sessions = self.data_manager.get_recent_sessions(days=days)
        
        counts = {'Low': 0, 'Medium': 0, 'High': 0, 'Critical': 0}
        total_samples = 0
        
        for session in sessions:
            scores = self.data_manager.get_fatigue_scores(session.session_id)
            for s in scores:
                level = s.get_level()
                if level in counts:
                    counts[level] += 1
                total_samples += 1
                
        if total_samples == 0:
            return {k: 0.0 for k in counts}
            
        return {k: round((v / total_samples) * 100, 1) for k, v in counts.items()}

    def get_weekly_badges(self, days: int = 7) -> List[Dict[str, str]]:
        """
        Get badges based on performance metrics.
        Returns list of dicts: {'name': str, 'icon': str, 'description': str}
        """
        badges = []
        sessions = self.data_manager.get_recent_sessions(days=days)
        
        # 1. Consistency Badge (Sessions on >= 5 days)
        active_days = set()
        total_active_hours = 0
        early_start = False
        late_night = False
        
        for s in sessions:
            active_days.add(s.start_time.strftime("%Y-%m-%d"))
            
            # Duration calculation
            start = s.start_time
            end = s.end_time if s.end_time else datetime.now()
            duration_hours = (end - start).total_seconds() / 3600
            total_active_hours += duration_hours
            
            if start.hour < 8:
                early_start = True
            if start.hour >= 22 or (s.end_time and s.end_time.hour >= 22):
                late_night = True
                
        if len(active_days) >= 5:
            badges.append({
                'name': 'Consistent',
                'icon': '📅',
                'description': 'Active 5+ days/week',
                'color': '#3b82f6' # Blue
            })
            
        # 2. Early Bird / Night Owl
        if early_start:
            badges.append({
                'name': 'Early Bird',
                'icon': '🌅',
                'description': 'Starts before 8 AM',
                'color': '#f59e0b' # Amber
            })
        elif late_night:
            badges.append({
                'name': 'Night Owl',
                'icon': '🦉',
                'description': 'Works past 10 PM',
                'color': '#8b5cf6' # Purple
            })
            
        # 3. Focus Master (High productivity)
        prod = self.get_productivity_stats(days=days)
        if prod['focus_score'] > 50: # Arbitrary threshold
             badges.append({
                'name': 'Focus Master',
                'icon': '⚡',
                'description': 'High Input Rate',
                'color': '#facc15' # Yellow
            })
            
        # 4. Zen Master (Taking breaks)
        eff = self.get_break_effectiveness(days=days)
        if eff['total_breaks'] >= 5:
            badges.append({
                'name': 'Zen Master',
                'icon': '🧘',
                'description': 'Regular Breaks',
                'color': '#10b981' # Emerald
            })
            
        # Fallback badge if empty
        if not badges:
             badges.append({
                'name': 'Newcomer',
                'icon': '🌱',
                'description': 'Start tracking!',
                'color': '#94a3b8' # Gray
            })
            
        return badges[:3] # Return top 3

    def export_statistics(self, filepath: str):
        """
        Export statistics to a CSV file.
        """
        import csv
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 1. Report Header
            writer.writerow(["Cognitive Fatigue Tracker - Statistics Report"])
            writer.writerow([f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}"])
            writer.writerow([])
            
            # 2. Key Metrics
            writer.writerow(["--- Key Metrics ---"])
            
            prod = self.get_productivity_stats()
            writer.writerow(["Focus Score (actions/min)", prod['focus_score']])
            writer.writerow(["Peak Hour", prod['peak_hour']])
            
            eff = self.get_break_effectiveness()
            writer.writerow(["Recovery Rate", eff['recovery_rate']])
            writer.writerow(["Total Breaks", eff['total_breaks']])
            
            screen = self.get_daily_screen_time()
            writer.writerow(["Screen Time", screen])
            
            badges = self.get_weekly_badges()
            badge_names = ", ".join([b['name'] for b in badges])
            writer.writerow(["Badges Earned", badge_names])
            
            writer.writerow([])
            
            # 3. Weekly Summary
            writer.writerow(["--- Weekly Overview ---"])
            writer.writerow(["Date", "Active Hours", "Avg Fatigue"])
            
            summary = self.get_weekly_summary()
            for day in summary:
                writer.writerow([day['full_date'], day['active_hours'], day['avg_fatigue']])
                
            writer.writerow([])
            
            # 4. Fatigue Zones
            writer.writerow(["--- Fatigue Zones Distribution ---"])
            dist = self.get_fatigue_distribution()
            for zone, pct in dist.items():
                writer.writerow([zone, f"{pct}%"])
