"""Activity manager for tracking and recommending refresh activities"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from src.ui.activities.activity_definitions import Activity, get_activity_by_id, get_all_activities


class ActivityManager:
    """Manages activity recommendations and completion tracking"""
    
    def __init__(self, data_manager=None):
        """
        Initialize activity manager
        
        Args:
            data_manager: DataManager instance for persistence (optional)
        """
        self.data_manager = data_manager
        self._completion_history: List[Dict] = []
    
    def recommend_activity(
        self,
        fatigue_score: float,
        session_duration_minutes: int = 0,
        blink_rate: Optional[float] = None,
        keyboard_activity: Optional[float] = None
    ) -> List[str]:
        """
        Recommend activities based on current state
        
        Args:
            fatigue_score: Current fatigue score (0-100)
            session_duration_minutes: How long user has been working
            blink_rate: Current blink rate (blinks per minute) if available
            keyboard_activity: Keyboard activity rate if available
        
        Returns:
            List of activity IDs, ordered by relevance
        """
        recommendations = []
        
        # Critical fatigue - comprehensive refresh needed
        if fatigue_score >= 80:
            recommendations.extend([
                "combo_energizer",      # 5-min intensive refresh
                "combo_quick_refresh",  # 3-min combination
                "breathing_deep"        # 5-min deep breathing
            ])
        
        # High fatigue - multi-faceted approach
        elif fatigue_score >= 60:
            recommendations.extend([
                "combo_quick_refresh",         # 3-min combination
                "breathing_physiological_sigh", # Quick stress relief
                "physical_walk",               # 2-min walk
                "meditation_body_scan"         # 3-min body scan
            ])
        
        # Moderate fatigue - targeted interventions
        elif fatigue_score >= 40:
            # Eye strain check
            if blink_rate and blink_rate < 15:  # Low blink rate
                recommendations.append("eye_20_20_20")
                recommendations.append("eye_rapid_blink")
            
            # Physical strain from typing
            if keyboard_activity and keyboard_activity > 50:
                recommendations.append("physical_wrist_stretch")
                recommendations.append("physical_shoulder_release")
            
            # General moderate fatigue
            recommendations.extend([
                "breathing_box",           # 2-min box breathing
                "physical_shoulder_release", # 90s shoulder release
                "eye_20_20_20"            # 20s eye relief
            ])
        
        # Low fatigue - preventive care
        else:
            recommendations.extend([
                "eye_20_20_20",              # Prevent eye strain
                "breathing_physiological_sigh", # Quick refresh
                "physical_wrist_stretch"     # Prevent RSI
            ])
        
        # Long session bonus recommendations
        if session_duration_minutes > 120:  # 2+ hours
            if "physical_walk" not in recommendations:
                recommendations.insert(0, "physical_walk")
            if "physical_desk_exercises" not in recommendations:
                recommendations.append("physical_desk_exercises")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for activity_id in recommendations:
            if activity_id not in seen:
                seen.add(activity_id)
                unique_recommendations.append(activity_id)
        
        return unique_recommendations[:5]  # Return top 5
    
    def get_recommended_activities(
        self,
        fatigue_score: float,
        session_duration_minutes: int = 0,
        blink_rate: Optional[float] = None,
        keyboard_activity: Optional[float] = None
    ) -> List[Activity]:
        """
        Get recommended Activity objects (not just IDs)
        
        Same arguments as recommend_activity
        
        Returns:
            List of Activity objects
        """
        activity_ids = self.recommend_activity(
            fatigue_score,
            session_duration_minutes,
            blink_rate,
            keyboard_activity
        )
        
        activities = []
        for activity_id in activity_ids:
            activity = get_activity_by_id(activity_id)
            if activity:
                activities.append(activity)
        
        return activities
    
    def track_activity_start(
        self,
        activity_id: str,
        session_id: Optional[int] = None,
        fatigue_before: Optional[float] = None
    ) -> Dict:
        """
        Track when an activity starts
        
        Args:
            activity_id: ID of the activity
            session_id: Current session ID if in a session
            fatigue_before: Fatigue score before starting
        
        Returns:
            Activity tracking dictionary
        """
        tracking = {
            'activity_id': activity_id,
            'session_id': session_id,
            'started_at': datetime.now(),
            'fatigue_before': fatigue_before,
            'completed': False
        }
        
        return tracking
    
    def track_activity_completion(
        self,
        activity_id: str,
        session_id: Optional[int] = None,
        fatigue_before: Optional[float] = None,
        fatigue_after: Optional[float] = None,
        started_at: Optional[datetime] = None
    ):
        """
        Track completed activity
        
        Args:
            activity_id: ID of the completed activity
            session_id: Current session ID if in a session
            fatigue_before: Fatigue score before activity
            fatigue_after: Fatigue score after activity
            started_at: When activity started (default: now)
        """
        if started_at is None:
            started_at = datetime.now()
        
        completed_at = datetime.now()
        duration = (completed_at - started_at).total_seconds()
        
        completion = {
            'activity_id': activity_id,
            'session_id': session_id,
            'started_at': started_at,
            'completed_at': completed_at,
            'duration_seconds': int(duration),
            'fatigue_before': fatigue_before,
            'fatigue_after': fatigue_after
        }
        
        # Store in memory
        self._completion_history.append(completion)
        
        # Persist to database if available
        if self.data_manager:
            try:
                self.data_manager.log_activity_completion(
                    session_id=session_id,
                    activity_id=activity_id,
                    started_at=started_at,
                    completed_at=completed_at,
                    duration_seconds=int(duration),
                    fatigue_before=fatigue_before,
                    fatigue_after=fatigue_after
                )
            except Exception as e:
                # Log but don't fail if DB write fails
                print(f"Warning: Could not save activity completion to database: {e}")
    
    def get_activity_history(
        self,
        session_id: Optional[int] = None,
        days: int = 30
    ) -> List[Dict]:
        """
        Get activity completion history
        
        Args:
            session_id: Filter by session ID (None = all sessions)
            days: Number of days to look back
        
        Returns:
            List of activity completion dictionaries
        """
        # Try to get from database first
        if self.data_manager:
            try:
                return self.data_manager.get_activity_history(session_id, days)
            except Exception:
                pass  # Fall back to in-memory
        
        # Filter in-memory history
        cutoff = datetime.now() - timedelta(days=days)
        filtered = [
            comp for comp in self._completion_history
            if comp['completed_at'] >= cutoff and
            (session_id is None or comp.get('session_id') == session_id)
        ]
        
        return filtered
    
    def get_activity_stats(self) -> Dict:
        """
        Get statistics about activity usage
        
        Returns:
            Dictionary with activity statistics
        """
        history = self.get_activity_history(days=30)
        
        if not history:
            return {
                'total_completed': 0,
                'most_popular': None,
                'avg_fatigue_reduction': 0,
                'by_category': {}
            }
        
        # Count completions by activity
        activity_counts = {}
        fatigue_reductions = []
        category_stats = {}
        
        for comp in history:
            activity_id = comp['activity_id']
            activity = get_activity_by_id(activity_id)
            
            # Count
            activity_counts[activity_id] = activity_counts.get(activity_id, 0) + 1
            
            # Fatigue reduction
            if comp.get('fatigue_before') and comp.get('fatigue_after'):
                reduction = comp['fatigue_before'] - comp['fatigue_after']
                fatigue_reductions.append(reduction)
            
            # Category stats
            if activity:
                cat = activity.category.value
                if cat not in category_stats:
                    category_stats[cat] = {'count': 0, 'reductions': []}
                category_stats[cat]['count'] += 1
                if comp.get('fatigue_before') and comp.get('fatigue_after'):
                    reduction = comp['fatigue_before'] - comp['fatigue_after']
                    category_stats[cat]['reductions'].append(reduction)
        
        # Most popular activity
        most_popular = max(activity_counts.items(), key=lambda x: x[1])[0] if activity_counts else None
        
        # Average fatigue reduction
        avg_reduction = sum(fatigue_reductions) / len(fatigue_reductions) if fatigue_reductions else 0
        
        # Process category stats
        for cat in category_stats:
            reductions = category_stats[cat]['reductions']
            category_stats[cat]['avg_reduction'] = sum(reductions) / len(reductions) if reductions else 0
        
        return {
            'total_completed': len(history),
            'most_popular': most_popular,
            'avg_fatigue_reduction': avg_reduction,
            'by_category': category_stats,
            'activity_counts': activity_counts
        }
    
    def get_effectiveness_for_user(self, activity_id: str) -> Optional[float]:
        """
        Calculate how effective an activity has been for this user
        
        Args:
            activity_id: Activity ID to check
        
        Returns:
            Average fatigue reduction for this activity, or None if no data
        """
        history = self.get_activity_history(days=90)
        
        reductions = []
        for comp in history:
            if comp['activity_id'] == activity_id:
                if comp.get('fatigue_before') and comp.get('fatigue_after'):
                    reduction = comp['fatigue_before'] - comp['fatigue_after']
                    reductions.append(reduction)
        
        return sum(reductions) / len(reductions) if reductions else None
