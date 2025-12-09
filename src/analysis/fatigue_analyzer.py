"""Fatigue analyzer for calculating cognitive fatigue scores"""
from datetime import datetime, timedelta
from typing import Optional
from src.models.fatigue_score import FatigueScore, FatigueHistory
from src.utils.helpers import get_time_of_day_factor, normalize_score
from src.utils.logger import default_logger as logger


class FatigueAnalyzer:
    """Analyzes user activity to calculate fatigue scores"""
    
    def __init__(self):
        """Initialize fatigue analyzer"""
        self.history = FatigueHistory()
        self.baseline_activity_rate = 20.0  # Baseline events per minute
        self._initial_activity_rate: Optional[float] = None
        self._session_start_time: Optional[datetime] = None
    
    def start_session(self):
        """Start a new analysis session"""
        self._session_start_time = datetime.now()
        self._initial_activity_rate = None
        logger.info("Started fatigue analysis session")
    
    def calculate_score(
        self,
        work_duration_minutes: float,
        activity_rate: float,
        time_since_break_minutes: float = 0,
        is_on_break: bool = False,
        blink_rate: float = 15.0
    ) -> FatigueScore:
        """
        Calculate current fatigue score.
        
        Args:
            work_duration_minutes: Total work time in minutes
            activity_rate: Current activity rate (events per minute)
            time_since_break_minutes: Minutes since last break
            is_on_break: Whether currently on break
            blink_rate: Current blink rate (blinks per minute)
        
        Returns:
            FatigueScore object
        """
        # Initialize baseline from first reading
        if self._initial_activity_rate is None and activity_rate > 0:
            self._initial_activity_rate = activity_rate
            self.baseline_activity_rate = activity_rate
        
        factors = {}
        
        # 1. Time-based fatigue (0-35 points)
        # Fatigue increases with continuous work time
        time_factor = min(work_duration_minutes / 120, 1.0) * 35  # Max at 2 hours
        factors['time_based'] = time_factor
        
        # 2. Activity decline factor (0-30 points)
        # Fatigue increases when activity rate drops
        if self._initial_activity_rate and self._initial_activity_rate > 0:
            activity_ratio = activity_rate / self._initial_activity_rate
            decline_factor = (1.0 - min(activity_ratio, 1.0)) * 30
            factors['activity_decline'] = decline_factor
        else:
            factors['activity_decline'] = 0
        
        # 3. Break recency factor (0-20 points)
        # Fatigue increases with time since last break
        break_factor = min(time_since_break_minutes / 60, 1.0) * 20  # Max at 60 min
        factors['break_recency'] = break_factor
        
        # 4. Time of day factor (multiplier 0.8-1.3)
        tod_factor = get_time_of_day_factor()
        factors['time_of_day_multiplier'] = tod_factor
        
        # 5. Session duration factor (0-15 points)
        # Long sessions contribute to fatigue
        session_duration_hours = work_duration_minutes / 60
        duration_factor = min(session_duration_hours / 4, 1.0) * 15  # Max at 4 hours
        factors['session_duration'] = duration_factor
        
        # 6. Blink rate factor (0-25 points)
        # Low blink rate indicates eye strain and screen fatigue
        # Normal: 15-20 blinks/min, Low: < 15, Critical: < 10
        if blink_rate > 0:  # Only if eye tracking is enabled
            if blink_rate < 5:
                blink_factor = 25  # Critical eye strain
            elif blink_rate < 10:
                blink_factor = 20  # High eye strain
            elif blink_rate < 15:
                blink_factor = 10  # Moderate eye strain
            else:
                blink_factor = 0  # Normal
            factors['blink_rate'] = blink_rate
            factors['eye_strain'] = blink_factor
        else:
            blink_factor = 0
            factors['eye_strain'] = 0
        
        # Calculate base score
        base_score = (
            time_factor +
            factors['activity_decline'] +
            break_factor +
            duration_factor +
            blink_factor
        )
        
        # Apply time of day multiplier
        final_score = base_score * tod_factor
        
        # If on break, reduce score
        if is_on_break:
            final_score *= 0.5
            factors['on_break_reduction'] = True
        
        # Clamp to 0-100
        final_score = max(0, min(100, final_score))
        
        # Create fatigue score object
        fatigue_score = FatigueScore(
            score=final_score,
            timestamp=datetime.now(),
            factors=factors
        )
        
        # Add to history
        self.history.add_score(fatigue_score)
        
        logger.debug(f"Calculated fatigue score: {final_score:.1f} ({fatigue_score.get_level()})")
        
        return fatigue_score
    
    def get_recommendations(self, score: FatigueScore) -> list:
        """
        Get recommendations based on fatigue score.
        
        Args:
            score: Current fatigue score
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        level = score.get_level()
        
        if level == "Low":
            recommendations.append("✅ You're doing great! Keep up the good work.")
            recommendations.append("💡 Stay hydrated and maintain good posture.")
        
        elif level == "Moderate":
            recommendations.append("⚠️ Consider taking a short break soon.")
            recommendations.append("🚶 Stand up and stretch for a few minutes.")
            recommendations.append("💧 Drink some water.")
        
        elif level == "High":
            recommendations.append("⚠️ HIGH FATIGUE - Take a break now!")
            recommendations.append("🛑 Step away from your computer.")
            recommendations.append("🌳 Get some fresh air if possible.")
            recommendations.append("☕ Have a healthy snack or beverage.")
        
        else:  # Critical
            recommendations.append("🚨 CRITICAL FATIGUE LEVEL!")
            recommendations.append("🛑 Stop working immediately.")
            recommendations.append("😴 You may need a longer break or rest.")
            recommendations.append("🏥 Consider if you're overworking.")
        
        return recommendations
    
    def get_trend_analysis(self) -> dict:
        """Get trend analysis of fatigue levels"""
        if len(self.history) < 5:
            return {
                'trend': 'insufficient_data',
                'message': 'Not enough data for trend analysis'
            }
        
        trend = self.history.get_trend()
        latest = self.history.get_latest()
        average = self.history.get_average(minutes=30)
        
        if trend == "increasing":
            message = "⚠️ Your fatigue is increasing. Consider taking a break."
        elif trend == "decreasing":
            message = "✅ Your fatigue is decreasing. Good recovery!"
        else:
            message = "➡️ Your fatigue level is stable."
        
        return {
            'trend': trend,
            'latest_score': latest.score if latest else 0,
            'average_30min': average,
            'message': message
        }
    
    def reset(self):
        """Reset analyzer state"""
        self.history.clear()
        self._initial_activity_rate = None
        self._session_start_time = None
        logger.info("Reset fatigue analyzer")
