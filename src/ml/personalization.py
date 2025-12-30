"""Personalization engine for user-specific adaptations"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import numpy as np
from src.utils.logger import default_logger as logger


class PersonalizationEngine:
    """Manages user-specific model personalization and adaptive thresholds"""
    
    def __init__(self, profile_dir: Optional[Path] = None):
        """
        Initialize personalization engine.
        
        Args:
            profile_dir: Directory to store user profiles
        """
        if profile_dir is None:
            profile_dir = Path(__file__).parent.parent.parent / "data" / "profiles"
        
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        
        self.profile_file = self.profile_dir / "user_profile.json"
        self.profile = self._load_profile()
        
        # Adaptive thresholds
        self.thresholds = self.profile.get('thresholds', {
            'low': 30,
            'moderate': 60,
            'high': 80
        })
        
        # User patterns
        self.patterns = self.profile.get('patterns', {})
        
        # Feedback history
        self.feedback_history = self.profile.get('feedback_history', [])
    
    def update_profile(
        self, 
        session_data: Dict,
        fatigue_scores: List[float],
        user_feedback: Optional[Dict] = None
    ):
        """
        Update user profile based on session data.
        
        Args:
            session_data: Session information (duration, breaks, etc.)
            fatigue_scores: List of fatigue scores from session
            user_feedback: Optional user feedback (corrections, preferences)
        """
        # Update session count
        self.profile['total_sessions'] = self.profile.get('total_sessions', 0) + 1
        
        # Update productive hours pattern
        self._update_productive_hours(session_data)
        
        # Update fatigue patterns
        self._update_fatigue_patterns(fatigue_scores)
        
        # Update thresholds based on user behavior
        self._adapt_thresholds(fatigue_scores, user_feedback)
        
        # Store feedback
        if user_feedback:
            self._store_feedback(user_feedback)
        
        # Update last activity timestamp
        self.profile['last_updated'] = datetime.now().isoformat()
        
        self._save_profile()
        logger.info("Updated user profile")
    
    def get_adaptive_thresholds(self) -> Dict[str, float]:
        """Get current adaptive thresholds"""
        return self.thresholds.copy()
    
    def get_personalization_score(self) -> float:
        """
        Get personalization score (0-1) indicating how personalized the model is.
        
        Returns:
            Score from 0 (not personalized) to 1 (highly personalized)
        """
        sessions = self.profile.get('total_sessions', 0)
        
        # Personalization increases with sessions (saturates at 50 sessions)
        score = min(sessions / 50.0, 1.0)
        
        return score
    
    def get_productivity_forecast(self, hour: int) -> float:
        """
        Get productivity forecast for a given hour (0-23).
        
        Args:
            hour: Hour of day (0-23)
        
        Returns:
            Productivity score (0-1)
        """
        hourly_patterns = self.patterns.get('hourly_productivity', {})
        
        return hourly_patterns.get(str(hour), 0.5)  # Default to neutral
    
    def should_adjust_sensitivity(self, current_score: float, user_action: str) -> bool:
        """
        Determine if sensitivity should be adjusted based on user behavior.
        
        Args:
            current_score: Current fatigue score
            user_action: User action ('took_break', 'dismissed_alert', etc.)
        
        Returns:
            Whether to adjust sensitivity
        """
        # Track user responses to alerts
        if user_action == 'dismissed_alert' and current_score < 70:
            # User dismissed alert at moderate fatigue - might be too sensitive
            return True
        elif user_action == 'took_break' and current_score > 40:
            # User took break even at low fatigue - might need earlier alerts
            return True
        
        return False
    
    def get_personalized_prediction_weight(self) -> float:
        """
        Get weight for ML prediction vs rule-based (0-1).
        
        Returns:
            Weight for ML prediction (0=use rule-based, 1=use ML)
        """
        sessions = self.profile.get('total_sessions', 0)
        
        if sessions < 5:
            return 0.0  # Use rule-based only
        elif sessions < 10:
            return 0.3  # Mostly rule-based
        elif sessions < 20:
            return 0.6  # Balanced
        else:
            return 0.85  # Mostly ML
    
    def _update_productive_hours(self, session_data: Dict):
        """Update patterns of productive hours"""
        start_time = session_data.get('start_time')
        if not start_time:
            return
        
        # Parse timestamp
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
        
        hour = start_time.hour
        
        # Track hourly productivity (based on activity)
        if 'hourly_productivity' not in self.patterns:
            self.patterns['hourly_productivity'] = {}
        
        # Simple exponential moving average
        current = self.patterns['hourly_productivity'].get(str(hour), 0.5)
        activity_score = session_data.get('productivity_score', 0.5)
        
        # EMA with alpha=0.2
        self.patterns['hourly_productivity'][str(hour)] = 0.8 * current + 0.2 * activity_score
    
    def _update_fatigue_patterns(self, fatigue_scores: List[float]):
        """Update fatigue patterns from session"""
        if not fatigue_scores:
            return
        
        # Track typical fatigue progression
        if 'fatigue_progression' not in self.patterns:
            self.patterns['fatigue_progression'] = {
                'mean': [],
                'std': []
            }
        
        # Bin scores by session time (e.g., every 15 minutes)
        bins = len(fatigue_scores) // 3  # Roughly 3 scores per bin
        if bins > 0:
            for i in range(min(bins, 8)):  # Max 8 bins (2 hours)
                start_idx = i * 3
                end_idx = min((i + 1) * 3, len(fatigue_scores))
                bin_scores = fatigue_scores[start_idx:end_idx]
                
                if bin_scores:
                    mean = np.mean(bin_scores)
                    
                    # Update running average
                    if len(self.patterns['fatigue_progression']['mean']) <= i:
                        self.patterns['fatigue_progression']['mean'].append(mean)
                    else:
                        current_mean = self.patterns['fatigue_progression']['mean'][i]
                        self.patterns['fatigue_progression']['mean'][i] = 0.7 * current_mean + 0.3 * mean
    
    def _adapt_thresholds(self, fatigue_scores: List[float], user_feedback: Optional[Dict]):
        """Adapt thresholds based on user behavior"""
        if not fatigue_scores:
            return
        
        # Calculate user's typical fatigue distribution
        mean_fatigue = np.mean(fatigue_scores)
        std_fatigue = np.std(fatigue_scores)
        
        # Adjust thresholds based on user's range
        # If user typically has lower fatigue, lower the thresholds
        # If user typically has higher fatigue, raise the thresholds
        
        base_thresholds = {'low': 30, 'moderate': 60, 'high': 80}
        
        # Shift based on mean (with limits)
        shift = (mean_fatigue - 40) * 0.2  # 40 is baseline mean
        shift = max(-10, min(10, shift))  # Limit shift to ±10
        
        # Update thresholds with exponential moving average
        alpha = 0.1  # Slow adaptation
        for key in base_thresholds:
            target = base_thresholds[key] + shift
            current = self.thresholds.get(key, base_thresholds[key])
            self.thresholds[key] = (1 - alpha) * current + alpha * target
        
        # Store in profile
        self.profile['thresholds'] = self.thresholds
        
        logger.debug(f"Adapted thresholds: {self.thresholds}")
    
    def _store_feedback(self, feedback: Dict):
        """Store user feedback"""
        feedback['timestamp'] = datetime.now().isoformat()
        self.feedback_history.append(feedback)
        
        # Keep only last 100 feedback entries
        if len(self.feedback_history) > 100:
            self.feedback_history = self.feedback_history[-100:]
        
        self.profile['feedback_history'] = self.feedback_history
    
    def get_feedback_summary(self) -> Dict:
        """Get summary of user feedback"""
        if not self.feedback_history:
            return {
                'total_feedback': 0,
                'positive_ratio': 0.0,
                'alert_dismissal_rate': 0.0
            }
        
        total = len(self.feedback_history)
        positive = sum(1 for f in self.feedback_history if f.get('type') == 'positive')
        dismissals = sum(1 for f in self.feedback_history if f.get('action') == 'dismissed_alert')
        
        return {
            'total_feedback': total,
            'positive_ratio': positive / total if total > 0 else 0.0,
            'alert_dismissal_rate': dismissals / total if total > 0 else 0.0
        }
    
    def reset_profile(self):
        """Reset user profile to defaults"""
        self.profile = {
            'created_at': datetime.now().isoformat(),
            'total_sessions': 0,
            'thresholds': {
                'low': 30,
                'moderate': 60,
                'high': 80
            },
            'patterns': {},
            'feedback_history': []
        }
        self.thresholds = self.profile['thresholds'].copy()
        self.patterns = {}
        self.feedback_history = []
        
        self._save_profile()
        logger.info("Reset user profile")
    
    def _load_profile(self) -> Dict:
        """Load user profile from file"""
        if not self.profile_file.exists():
            return {
                'created_at': datetime.now().isoformat(),
                'total_sessions': 0,
                'thresholds': {
                    'low': 30,
                    'moderate': 60,
                    'high': 80
                },
                'patterns': {},
                'feedback_history': []
            }
        
        try:
            with open(self.profile_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load profile: {e}")
            return {'total_sessions': 0}
    
    def _save_profile(self):
        """Save user profile to file"""
        try:
            with open(self.profile_file, 'w') as f:
                json.dump(self.profile, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
    
    def get_profile_stats(self) -> Dict:
        """Get profile statistics"""
        return {
            'total_sessions': self.profile.get('total_sessions', 0),
            'personalization_score': self.get_personalization_score(),
            'ml_weight': self.get_personalized_prediction_weight(),
            'adaptive_thresholds': self.get_adaptive_thresholds(),
            'created_at': self.profile.get('created_at'),
            'last_updated': self.profile.get('last_updated'),
            'feedback_summary': self.get_feedback_summary()
        }
