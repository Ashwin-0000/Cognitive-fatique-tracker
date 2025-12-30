"""Feature engineering for ML-based fatigue prediction"""
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque
from src.models.activity_data import ActivityData
from src.utils.logger import default_logger as logger


class FeatureEngineer:
    """Extracts and engineers features from raw activity data"""
    
    def __init__(self, window_size_minutes: int = 15):
        """
        Initialize feature engineer.
        
        Args:
            window_size_minutes: Size of rolling window for feature computation
        """
        self.window_size = window_size_minutes
        
        # Rolling buffers for temporal features
        self._activity_buffer = deque(maxlen=1000)
        self._fatigue_buffer = deque(maxlen=100)
        self._eye_buffer = deque(maxlen=100)
        
        # Baseline metrics (computed from initial data)
        self._baseline_activity_rate: Optional[float] = None
        self._baseline_blink_rate: Optional[float] = None
        
        # Session start time
        self._session_start: Optional[datetime] = None
    
    def start_session(self):
        """Start a new feature extraction session"""
        self._session_start = datetime.now()
        self._activity_buffer.clear()
        self._fatigue_buffer.clear()
        self._eye_buffer.clear()
        logger.info("Started feature engineering session")
    
    def add_activity(self, activity: ActivityData):
        """Add activity data to buffer"""
        self._activity_buffer.append(activity)
    
    def add_fatigue_score(self, score: float, timestamp: Optional[datetime] = None):
        """Add fatigue score to buffer"""
        if timestamp is None:
            timestamp = datetime.now()
        self._fatigue_buffer.append((timestamp, score))
    
    def add_eye_data(self, blink_rate: float, timestamp: Optional[datetime] = None):
        """Add eye tracking data to buffer"""
        if timestamp is None:
            timestamp = datetime.now()
        self._eye_buffer.append((timestamp, blink_rate))
    
    def extract_features(
        self,
        current_time: Optional[datetime] = None,
        blink_rate: float = 15.0,
        session_duration_minutes: float = 0.0,
        time_since_break_minutes: float = 0.0
    ) -> np.ndarray:
        """
        Extract feature vector for current state.
        
        Args:
            current_time: Current timestamp
            blink_rate: Current blink rate
            session_duration_minutes: Total session duration
            time_since_break_minutes: Time since last break
        
        Returns:
            Feature vector as numpy array
        """
        if current_time is None:
            current_time = datetime.now()
        
        features = {}
        
        # 1. Activity Features (8 features)
        activity_features = self._extract_activity_features(current_time)
        features.update(activity_features)
        
        # 2. Eye Tracking Features (6 features)
        eye_features = self._extract_eye_features(current_time, blink_rate)
        features.update(eye_features)
        
        # 3. Temporal Features (6 features)
        temporal_features = self._extract_temporal_features(current_time)
        features.update(temporal_features)
        
        # 4. Session Features (3 features)
        session_features = {
            'session_duration_minutes': session_duration_minutes,
            'time_since_break_minutes': time_since_break_minutes,
            'break_frequency': self._calculate_break_frequency(current_time)
        }
        features.update(session_features)
        
        # 5. Historical Features (5 features)
        historical_features = self._extract_historical_features(current_time)
        features.update(historical_features)
        
        # Convert to ordered numpy array
        feature_vector = self._dict_to_vector(features)
        
        logger.debug(f"Extracted {len(feature_vector)} features")
        return feature_vector
    
    def _extract_activity_features(self, current_time: datetime) -> Dict[str, float]:
        """Extract activity-based features"""
        features = {}
        
        if not self._activity_buffer:
            return {
                'activity_rate_1min': 0.0,
                'activity_rate_5min': 0.0,
                'activity_rate_15min': 0.0,
                'keyboard_rate': 0.0,
                'mouse_rate': 0.0,
                'activity_variance': 0.0,
                'activity_trend': 0.0,
                'activity_decline_ratio': 1.0
            }
        
        # Calculate activity rates for different time windows
        activity_1min = self._count_events_in_window(current_time, 1)
        activity_5min = self._count_events_in_window(current_time, 5)
        activity_15min = self._count_events_in_window(current_time, 15)
        
        features['activity_rate_1min'] = activity_1min
        features['activity_rate_5min'] = activity_5min / 5.0
        features['activity_rate_15min'] = activity_15min / 15.0
        
        # Keyboard vs mouse activity
        keyboard_count = self._count_events_by_type(current_time, 5, 'keyboard')
        mouse_count = self._count_events_by_type(current_time, 5, 
                                                  ['mouse_click', 'mouse_move', 'mouse_scroll'])
        
        features['keyboard_rate'] = keyboard_count / 5.0
        features['mouse_rate'] = mouse_count / 5.0
        
        # Activity variance (measure of consistency)
        minute_rates = [
            self._count_events_in_window(current_time - timedelta(minutes=i), 1)
            for i in range(5)
        ]
        features['activity_variance'] = np.std(minute_rates) if minute_rates else 0.0
        
        # Activity trend (increasing/decreasing)
        if len(minute_rates) >= 3:
            features['activity_trend'] = minute_rates[0] - minute_rates[-1]
        else:
            features['activity_trend'] = 0.0
        
        # Activity decline ratio (vs baseline)
        if self._baseline_activity_rate is None and activity_5min > 0:
            self._baseline_activity_rate = activity_5min / 5.0
        
        if self._baseline_activity_rate and self._baseline_activity_rate > 0:
            features['activity_decline_ratio'] = (activity_5min / 5.0) / self._baseline_activity_rate
        else:
            features['activity_decline_ratio'] = 1.0
        
        return features
    
    def _extract_eye_features(self, current_time: datetime, current_blink_rate: float) -> Dict[str, float]:
        """Extract eye tracking features"""
        features = {}
        
        # Add current blink rate to buffer
        self.add_eye_data(current_blink_rate, current_time)
        
        # Current blink rate
        features['blink_rate'] = current_blink_rate
        
        # Average blink rate over 5 minutes
        recent_blinks = [
            rate for ts, rate in self._eye_buffer
            if (current_time - ts).total_seconds() <= 300
        ]
        features['blink_rate_5min_avg'] = np.mean(recent_blinks) if recent_blinks else current_blink_rate
        
        # Blink rate variance
        features['blink_rate_variance'] = np.std(recent_blinks) if len(recent_blinks) > 1 else 0.0
        
        # Blink rate trend
        if len(recent_blinks) >= 3:
            features['blink_rate_trend'] = recent_blinks[-1] - recent_blinks[0]
        else:
            features['blink_rate_trend'] = 0.0
        
        # Eye strain indicator (normalized)
        # Normal: 15-20 blinks/min, Low: <15, Critical: <10
        if current_blink_rate < 10:
            features['eye_strain_level'] = 1.0  # Critical
        elif current_blink_rate < 15:
            features['eye_strain_level'] = 0.5  # Moderate
        else:
            features['eye_strain_level'] = 0.0  # Normal
        
        # Blink rate decline ratio
        if self._baseline_blink_rate is None and current_blink_rate > 0:
            self._baseline_blink_rate = current_blink_rate
        
        if self._baseline_blink_rate and self._baseline_blink_rate > 0:
            features['blink_decline_ratio'] = current_blink_rate / self._baseline_blink_rate
        else:
            features['blink_decline_ratio'] = 1.0
        
        return features
    
    def _extract_temporal_features(self, current_time: datetime) -> Dict[str, float]:
        """Extract time-based features"""
        features = {}
        
        # Hour of day (normalized 0-1, with cyclical encoding)
        hour = current_time.hour + current_time.minute / 60.0
        features['hour_sin'] = np.sin(2 * np.pi * hour / 24.0)
        features['hour_cos'] = np.cos(2 * np.pi * hour / 24.0)
        
        # Day of week (0=Monday, 6=Sunday)
        features['day_of_week'] = current_time.weekday() / 6.0
        
        # Weekend indicator
        features['is_weekend'] = 1.0 if current_time.weekday() >= 5 else 0.0
        
        # Time of day category (0: morning, 0.33: afternoon, 0.66: evening, 1: night)
        if 6 <= current_time.hour < 12:
            features['time_of_day_category'] = 0.0  # Morning
        elif 12 <= current_time.hour < 18:
            features['time_of_day_category'] = 0.33  # Afternoon
        elif 18 <= current_time.hour < 22:
            features['time_of_day_category'] = 0.66  # Evening
        else:
            features['time_of_day_category'] = 1.0  # Night
        
        # Session time elapsed (normalized by 4 hours)
        if self._session_start:
            elapsed_hours = (current_time - self._session_start).total_seconds() / 3600.0
            features['session_elapsed_normalized'] = min(elapsed_hours / 4.0, 1.0)
        else:
            features['session_elapsed_normalized'] = 0.0
        
        return features
    
    def _extract_historical_features(self, current_time: datetime) -> Dict[str, float]:
        """Extract features from historical fatigue scores"""
        features = {}
        
        if not self._fatigue_buffer:
            return {
                'fatigue_5min_ago': 0.0,
                'fatigue_15min_ago': 0.0,
                'fatigue_avg_1hour': 0.0,
                'fatigue_trend': 0.0,
                'fatigue_variance': 0.0
            }
        
        # Get scores from different time points
        score_5min_ago = self._get_score_at_time(current_time - timedelta(minutes=5))
        score_15min_ago = self._get_score_at_time(current_time - timedelta(minutes=15))
        
        features['fatigue_5min_ago'] = score_5min_ago
        features['fatigue_15min_ago'] = score_15min_ago
        
        # Average fatigue over last hour
        recent_scores = [
            score for ts, score in self._fatigue_buffer
            if (current_time - ts).total_seconds() <= 3600
        ]
        features['fatigue_avg_1hour'] = np.mean(recent_scores) if recent_scores else 0.0
        
        # Fatigue trend
        if len(recent_scores) >= 3:
            features['fatigue_trend'] = recent_scores[-1] - recent_scores[0]
        else:
            features['fatigue_trend'] = 0.0
        
        # Fatigue variance
        features['fatigue_variance'] = np.std(recent_scores) if len(recent_scores) > 1 else 0.0
        
        return features
    
    def _count_events_in_window(self, end_time: datetime, minutes: int) -> float:
        """Count activity events in a time window"""
        start_time = end_time - timedelta(minutes=minutes)
        count = sum(
            1 for activity in self._activity_buffer
            if start_time <= activity.timestamp <= end_time
        )
        return float(count)
    
    def _count_events_by_type(
        self, 
        end_time: datetime, 
        minutes: int, 
        event_types: any
    ) -> float:
        """Count specific event types in a time window"""
        start_time = end_time - timedelta(minutes=minutes)
        
        if isinstance(event_types, str):
            event_types = [event_types]
        
        count = sum(
            1 for activity in self._activity_buffer
            if start_time <= activity.timestamp <= end_time
            and activity.event_type in event_types
        )
        return float(count)
    
    def _get_score_at_time(self, target_time: datetime) -> float:
        """Get fatigue score closest to target time"""
        if not self._fatigue_buffer:
            return 0.0
        
        # Find closest score
        closest_score = min(
            self._fatigue_buffer,
            key=lambda x: abs((x[0] - target_time).total_seconds())
        )
        
        return closest_score[1]
    
    def _calculate_break_frequency(self, current_time: datetime) -> float:
        """Calculate break frequency (breaks per hour)"""
        # TODO: Implement break detection from activity gaps
        # For now, return 0.0
        return 0.0
    
    def _dict_to_vector(self, features: Dict[str, float]) -> np.ndarray:
        """Convert feature dictionary to ordered numpy array"""
        # Define feature order (must be consistent)
        feature_order = [
            # Activity features (8)
            'activity_rate_1min',
            'activity_rate_5min',
            'activity_rate_15min',
            'keyboard_rate',
            'mouse_rate',
            'activity_variance',
            'activity_trend',
            'activity_decline_ratio',
            # Eye features (6)
            'blink_rate',
            'blink_rate_5min_avg',
            'blink_rate_variance',
            'blink_rate_trend',
            'eye_strain_level',
            'blink_decline_ratio',
            # Temporal features (6)
            'hour_sin',
            'hour_cos',
            'day_of_week',
            'is_weekend',
            'time_of_day_category',
            'session_elapsed_normalized',
            # Session features (3)
            'session_duration_minutes',
            'time_since_break_minutes',
            'break_frequency',
            # Historical features (5)
            'fatigue_5min_ago',
            'fatigue_15min_ago',
            'fatigue_avg_1hour',
            'fatigue_trend',
            'fatigue_variance'
        ]
        
        # Extract features in order
        vector = np.array([features.get(f, 0.0) for f in feature_order])
        return vector
    
    def get_feature_names(self) -> List[str]:
        """Get ordered list of feature names"""
        return [
            'activity_rate_1min', 'activity_rate_5min', 'activity_rate_15min',
            'keyboard_rate', 'mouse_rate', 'activity_variance', 'activity_trend',
            'activity_decline_ratio', 'blink_rate', 'blink_rate_5min_avg',
            'blink_rate_variance', 'blink_rate_trend', 'eye_strain_level',
            'blink_decline_ratio', 'hour_sin', 'hour_cos', 'day_of_week',
            'is_weekend', 'time_of_day_category', 'session_elapsed_normalized',
            'session_duration_minutes', 'time_since_break_minutes', 'break_frequency',
            'fatigue_5min_ago', 'fatigue_15min_ago', 'fatigue_avg_1hour',
            'fatigue_trend', 'fatigue_variance'
        ]
    
    def reset(self):
        """Reset feature engineer state"""
        self._activity_buffer.clear()
        self._fatigue_buffer.clear()
        self._eye_buffer.clear()
        self._baseline_activity_rate = None
        self._baseline_blink_rate = None
        self._session_start = None
        logger.info("Reset feature engineer")
