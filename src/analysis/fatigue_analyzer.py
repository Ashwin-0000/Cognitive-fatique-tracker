"""Fatigue analyzer for calculating cognitive fatigue scores"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import numpy as np
from src.models.fatigue_score import FatigueScore, FatigueHistory
from src.models.activity_data import ActivityData
from src.utils.helpers import get_time_of_day_factor, normalize_score
from src.utils.logger import default_logger as logger

# ML imports
try:
    from src.ml.ml_predictor import MLPredictor
    from src.ml.feature_engineering import FeatureEngineer
    from src.ml.personalization import PersonalizationEngine
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML module not available: {e}")
    ML_AVAILABLE = False


class FatigueAnalyzer:
    """Analyzes user activity to calculate fatigue scores"""

    def __init__(self, use_ml: bool = True):
        """
        Initialize fatigue analyzer.

        Args:
            use_ml: Whether to use ML predictions (if available)
        """
        self.history = FatigueHistory()
        self.baseline_activity_rate = 20.0  # Baseline events per minute
        self._initial_activity_rate: Optional[float] = None
        self.session_start_time: Optional[datetime] = None

        # ML components
        self.use_ml = use_ml and ML_AVAILABLE
        if self.use_ml:
            try:
                self.feature_engineer = FeatureEngineer()
                self.ml_predictor = MLPredictor(
                    feature_engineer=self.feature_engineer)
                self.personalization = PersonalizationEngine()
                logger.info("ML prediction enabled")
            except Exception as e:
                logger.error(f"Failed to initialize ML components: {e}")
                self.use_ml = False

        # Session tracking for ML
        self._session_fatigue_scores = []
        self._session_features = []

    def start_session(self):
        """Start a new analysis session"""
        self.session_start_time = datetime.now()
        self._initial_activity_rate = None
        self._session_fatigue_scores = []
        self._session_features = []

        if self.use_ml:
            self.feature_engineer.start_session()

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

        # RULE-BASED CALCULATION (original logic)
        # 1. Time-based fatigue (0-35 points)
        time_factor = min(work_duration_minutes / 120, 1.0) * 35
        factors['time_based'] = time_factor

        # 2. Activity intensity & decline factor (0-35 points)
        if self._initial_activity_rate and self._initial_activity_rate > 0:
            activity_ratio = activity_rate / self._initial_activity_rate

            # Decline factor: fatigue increases when activity drops (0-15
            # points)
            decline_factor = max(0, (1.0 - min(activity_ratio, 1.0))) * 15

            # Intensity factor: fatigue increases with sustained high activity (0-20 points)
            # High activity above baseline is mentally taxing
            if activity_ratio > 1.0:
                # Activity is above baseline - this causes fatigue!
                intensity_excess = min(
                    (activity_ratio - 1.0),
                    2.0)  # Cap at 2x baseline
                intensity_factor = (intensity_excess / 2.0) * 20
            else:
                intensity_factor = 0

            factors['activity_decline'] = decline_factor
            factors['activity_intensity'] = intensity_factor
        else:
            factors['activity_decline'] = 0
            factors['activity_intensity'] = 0

        # 3. Break recency factor (0-20 points)
        break_factor = min(time_since_break_minutes / 60, 1.0) * 20
        factors['break_recency'] = break_factor

        # 4. Time of day factor (multiplier 0.8-1.3)
        tod_factor = get_time_of_day_factor()
        factors['time_of_day_multiplier'] = tod_factor

        # 5. Session duration factor (0-15 points)
        session_duration_hours = work_duration_minutes / 60
        duration_factor = min(session_duration_hours / 4, 1.0) * 15
        factors['session_duration'] = duration_factor

        # 6. Blink rate factor (0-25 points)
        if blink_rate > 0:
            if blink_rate < 5:
                blink_factor = 25
            elif blink_rate < 10:
                blink_factor = 20
            elif blink_rate < 15:
                blink_factor = 10
            else:
                blink_factor = 0
            factors['blink_rate'] = blink_rate
            factors['eye_strain'] = blink_factor
        else:
            blink_factor = 0
            factors['eye_strain'] = 0

        # Calculate rule-based score
        base_score = (
            time_factor +
            factors.get('activity_decline', 0) +
            # NEW: High activity increases fatigue
            factors.get('activity_intensity', 0) +
            break_factor +
            duration_factor +
            blink_factor
        )
        final_score_rule = base_score * tod_factor

        if is_on_break:
            final_score_rule *= 0.5
            factors['on_break_reduction'] = True

        final_score_rule = max(0, min(100, final_score_rule))

        # ML PREDICTION (if available)
        ml_score = None
        ml_confidence = 0.0
        ml_weight = 0.0

        if self.use_ml:
            try:
                # Extract features
                features = self.feature_engineer.extract_features(
                    current_time=datetime.now(),
                    blink_rate=blink_rate,
                    session_duration_minutes=work_duration_minutes,
                    time_since_break_minutes=time_since_break_minutes
                )

                # Get ML prediction
                ml_score, ml_confidence = self.ml_predictor.predict(features)

                # Get personalized weight for ML
                ml_weight = self.personalization.get_personalized_prediction_weight()

                # Store for training
                self._session_features.append(features)

                factors['ml_score'] = ml_score
                factors['ml_confidence'] = ml_confidence
                factors['ml_weight'] = ml_weight

            except Exception as e:
                logger.error(f"ML prediction error: {e}")
                ml_score = None

        # HYBRID PREDICTION
        if ml_score is not None and ml_weight > 0:
            # Weighted combination of rule-based and ML
            final_score = (
                ml_weight * ml_score +
                (1 - ml_weight) * final_score_rule
            )
            factors['prediction_method'] = 'hybrid'
            logger.debug(
                f"Hybrid prediction: ML={ml_score:.1f} (w={ml_weight:.2f}), Rule={final_score_rule:.1f}, Final={final_score:.1f}")
        else:
            # Fall back to rule-based
            final_score = final_score_rule
            factors['prediction_method'] = 'rule_based'

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

        # Track for ML training
        if self.use_ml:
            self._session_fatigue_scores.append(final_score)
            # Add fatigue score to feature engineer for historical features
            self.feature_engineer.add_fatigue_score(final_score)

        logger.debug(
            f"Calculated fatigue score: {final_score:.1f} ({fatigue_score.get_level()})")

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
            recommendations.append(
                "✅ You're doing great! Keep up the good work.")
            recommendations.append(
                "💡 Stay hydrated and maintain good posture.")

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
        self.session_start_time = None
        self._session_fatigue_scores = []
        self._session_features = []

        if self.use_ml:
            self.feature_engineer.reset()

        logger.info("Reset fatigue analyzer")

    def add_activity(self, activity: ActivityData):
        """
        Add activity data for ML feature extraction.

        Args:
            activity: Activity data event
        """
        if self.use_ml:
            self.feature_engineer.add_activity(activity)

    def train_ml_model(self, feedback_score: Optional[float] = None):
        """
        Train ML model with session data.

        Args:
            feedback_score: Optional user-provided correction to last score
        """
        if not self.use_ml:
            return

        if len(self._session_features) == 0:
            logger.warning("No features collected for training")
            return

        try:
            # Train on collected samples
            for i, features in enumerate(self._session_features):
                if i < len(self._session_fatigue_scores):
                    target_score = self._session_fatigue_scores[i]

                    # Use feedback if provided for last sample
                    if feedback_score is not None and i == len(
                            self._session_features) - 1:
                        target_score = feedback_score

                    # Incremental update
                    self.ml_predictor.partial_fit(features, target_score)

            # Update personalization
            session_data = {
                'start_time': self.session_start_time,
                'productivity_score': 0.5  # TODO: Calculate from activity
            }
            self.personalization.update_profile(
                session_data,
                self._session_fatigue_scores
            )

            # Save model periodically
            if self.ml_predictor._training_samples_count % 50 == 0:
                self.ml_predictor.save_model()

            logger.info(
                f"Trained ML model with {len(self._session_features)} samples")

        except Exception as e:
            logger.error(f"ML training error: {e}")

    def get_ml_stats(self) -> Dict:
        """Get ML model statistics"""
        if not self.use_ml:
            return {'enabled': False}

        return {
            'enabled': True,
            'model_performance': self.ml_predictor.get_performance_metrics(),
            'personalization': self.personalization.get_profile_stats(),
            'feature_importance': self.ml_predictor.get_top_features(5)
        }

    def train_from_psychometric_file(self, filepath: str) -> Dict:
        """
        Train ML model from psychometric dataset CSV file.

        Args:
            filepath: Path to psychometric CSV file

        Returns:
            Training statistics
        """
        if not self.use_ml:
            logger.warning(
                "ML not enabled, cannot train from psychometric file")
            return {'error': 'ML not enabled'}

        try:
            stats = self.ml_predictor.train_from_psychometric_dataset(filepath)
            logger.info(f"Trained from psychometric dataset: {filepath}")
            return stats
        except Exception as e:
            logger.error(f"Failed to train from psychometric file: {e}")
            return {'error': str(e)}

    def get_dataset_statistics(self) -> Dict:
        """Get statistics about training data sources"""
        if not self.use_ml:
            return {'enabled': False}

        metrics = self.ml_predictor.get_performance_metrics()
        return {
            'enabled': True,
            'total_samples': metrics.get('samples_count', 0),
            'model_initialized': metrics.get('is_initialized', False),
            'mae': metrics.get('mae', 0.0),
            'rmse': metrics.get('rmse', 0.0)
        }

    def reset_ml_model(self):
        """Reset ML model and personalization"""
        if not self.use_ml:
            return

        self.ml_predictor.reset()
        self.personalization.reset_profile()
        logger.info("Reset ML model and personalization")
