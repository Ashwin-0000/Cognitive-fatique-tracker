"""Generate realistic synthetic training data and train ML model"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import numpy as np
from datetime import datetime, timedelta
from src.ml.feature_engineering import FeatureEngineer
from src.ml.ml_predictor import MLPredictor
from src.ml.personalization import PersonalizationEngine
from src.models.activity_data import ActivityData


class SyntheticDataGenerator:
    """Generates realistic user behavior data"""
    
    def __init__(self, user_profile='normal'):
        """
        Initialize data generator.
        
        Args:
            user_profile: 'morning_person', 'night_owl', 'normal', 'workaholic'
        """
        self.profile = user_profile
        self.rng = np.random.RandomState(42)
        
    def generate_session(self, session_num: int, duration_hours: float = 2.0):
        """
        Generate a realistic work session.
        
        Args:
            session_num: Session number (affects time of day, fatigue patterns)
            duration_hours: Session duration in hours
        
        Returns:
            Tuple of (activities, blink_rates, timestamps, true_fatigue_scores)
        """
        # Determine time of day based on session number
        hour_of_day = 9 + (session_num % 8)  # Rotate through 9am-5pm
        start_time = datetime.now().replace(hour=hour_of_day, minute=0, second=0)
        
        num_samples = int(duration_hours * 12)  # Sample every 5 minutes
        
        activities = []
        blink_rates = []
        timestamps = []
        true_fatigue_scores = []
        
        # Session parameters
        initial_activity = self._get_initial_activity(hour_of_day)
        initial_blink = 17.0 + self.rng.randn() * 2.0  # Normal: 15-19
        
        for i in range(num_samples):
            timestamp = start_time + timedelta(minutes=i*5)
            elapsed_hours = i * 5 / 60.0
            
            # Simulate fatigue buildup
            fatigue_factor = self._calculate_fatigue_factor(
                elapsed_hours, hour_of_day, session_num
            )
            
            # Activity decreases with fatigue
            activity_rate = initial_activity * (1 - fatigue_factor * 0.4)
            activity_rate = max(5, activity_rate + self.rng.randn() * 2)
            
            # Generate activities
            num_activities = int(activity_rate * 5)  # events per 5 minutes
            for j in range(num_activities):
                event_time = timestamp + timedelta(seconds=self.rng.randint(0, 300))
                event_type = 'keyboard' if self.rng.rand() > 0.3 else 'mouse_click'
                activities.append(ActivityData(event_type, event_time))
            
            # Blink rate decreases with fatigue and screen time
            blink_rate = initial_blink * (1 - fatigue_factor * 0.5)
            blink_rate = max(8, blink_rate + self.rng.randn() * 1.5)
            blink_rates.append(blink_rate)
            
            # Calculate true fatigue score
            true_score = self._calculate_true_fatigue(
                elapsed_hours, hour_of_day, activity_rate, 
                blink_rate, session_num
            )
            true_fatigue_scores.append(true_score)
            timestamps.append(timestamp)
        
        return activities, blink_rates, timestamps, true_fatigue_scores
    
    def _get_initial_activity(self, hour: int) -> float:
        """Get initial activity rate based on time of day and profile"""
        base_rate = 20.0
        
        # Time of day effect
        if hour < 10:  # Early morning
            time_factor = 0.8
        elif hour < 14:  # Mid-day
            time_factor = 1.0
        elif hour < 16:  # Afternoon slump
            time_factor = 0.7
        else:  # Late afternoon
            time_factor = 0.85
        
        # Profile adjustments
        if self.profile == 'morning_person':
            if hour < 12:
                time_factor *= 1.2
            else:
                time_factor *= 0.9
        elif self.profile == 'night_owl':
            if hour < 12:
                time_factor *= 0.8
            else:
                time_factor *= 1.1
        elif self.profile == 'workaholic':
            time_factor *= 1.3
        
        return base_rate * time_factor
    
    def _calculate_fatigue_factor(
        self, 
        elapsed_hours: float, 
        hour: int, 
        session_num: int
    ) -> float:
        """Calculate fatigue factor (0-1)"""
        # Base fatigue increases with time
        base_fatigue = min(elapsed_hours / 3.0, 0.8)
        
        # Time of day effect
        if hour >= 14 and hour <= 16:  # Afternoon slump
            base_fatigue += 0.15
        
        # Session number effect (cumulative fatigue)
        cumulative = min(session_num * 0.02, 0.2)
        
        return min(base_fatigue + cumulative, 1.0)
    
    def _calculate_true_fatigue(
        self,
        elapsed_hours: float,
        hour: int,
        activity_rate: float,
        blink_rate: float,
        session_num: int
    ) -> float:
        """Calculate ground truth fatigue score"""
        # Time-based component (0-35)
        time_component = min(elapsed_hours / 2.0, 1.0) * 35
        
        # Activity component (0-30)
        baseline_activity = 20.0
        activity_component = (1 - min(activity_rate / baseline_activity, 1.0)) * 30
        
        # Blink rate component (0-25)
        if blink_rate < 10:
            blink_component = 25
        elif blink_rate < 15:
            blink_component = 15
        else:
            blink_component = 5
        
        # Time of day multiplier
        if hour >= 14 and hour <= 16:
            tod_multiplier = 1.2
        elif hour >= 10 and hour <= 12:
            tod_multiplier = 0.9
        else:
            tod_multiplier = 1.0
        
        # Session duration component
        duration_component = min(elapsed_hours / 4.0, 1.0) * 15
        
        score = (time_component + activity_component + blink_component + duration_component) * tod_multiplier
        
        # Add some noise
        score += self.rng.randn() * 3
        
        return np.clip(score, 0, 100)


def train_model_with_synthetic_data(num_sessions: int = 25, profile: str = 'normal'):
    """
    Generate synthetic data and train ML model.
    
    Args:
        num_sessions: Number of sessions to generate
        profile: User profile type
    """
    print("="*70)
    print(f"GENERATING SYNTHETIC DATA AND TRAINING ML MODEL")
    print(f"Profile: {profile.upper()}, Sessions: {num_sessions}")
    print("="*70 + "\n")
    
    generator = SyntheticDataGenerator(user_profile=profile)
    
    # Initialize ML components
    feature_engineer = FeatureEngineer()
    ml_predictor = MLPredictor(feature_engineer=feature_engineer)
    personalization = PersonalizationEngine()
    
    all_maes = []
    
    for session_num in range(num_sessions):
        print(f"\n📊 Session {session_num + 1}/{num_sessions}")
        print("-" * 70)
        
        # Generate session data
        session_duration = 1.5 + np.random.rand() * 1.5  # 1.5-3 hours
        activities, blink_rates, timestamps, true_scores = generator.generate_session(
            session_num, session_duration
        )
        
        print(f"  Generated: {len(activities)} activities, {len(true_scores)} samples")
        print(f"  Duration: {session_duration:.1f} hours")
        print(f"  Time of day: {timestamps[0].strftime('%H:%M')}")
        
        # Reset for new session
        feature_engineer.start_session()
        
        session_predictions = []
        session_errors = []
        session_features_list = []
        
        # Process each sample in the session
        for i, (timestamp, blink_rate, true_score) in enumerate(
            zip(timestamps, blink_rates, true_scores)
        ):
            # Add activities up to this point
            relevant_activities = [
                a for a in activities 
                if a.timestamp <= timestamp
            ]
            for act in relevant_activities:
                if act not in feature_engineer._activity_buffer:
                    feature_engineer.add_activity(act)
            
            # Extract features
            elapsed_minutes = (timestamp - timestamps[0]).total_seconds() / 60
            features = feature_engineer.extract_features(
                current_time=timestamp,
                blink_rate=blink_rate,
                session_duration_minutes=elapsed_minutes,
                time_since_break_minutes=min(elapsed_minutes, 60)
            )
            
            # Get prediction
            predicted_score, confidence = ml_predictor.predict(features)
            
            # Calculate error
            error = abs(predicted_score - true_score)
            session_errors.append(error)
            session_predictions.append((predicted_score, true_score, confidence))
            session_features_list.append(features)
            
            # Incremental training
            ml_predictor.partial_fit(features, true_score)
        
        # Session statistics
        mae = np.mean(session_errors)
        all_maes.append(mae)
        
        avg_confidence = np.mean([c for _, _, c in session_predictions])
        
        print(f"\n  📈 Session Results:")
        print(f"     MAE: {mae:.2f}")
        print(f"     Avg Confidence: {avg_confidence:.2f}")
        print(f"     Samples trained: {ml_predictor._training_samples_count}")
        
        # Show some predictions
        print(f"\n  🎯 Sample Predictions:")
        for j in [0, len(session_predictions)//2, -1]:
            pred, true, conf = session_predictions[j]
            print(f"     Sample {j+1}: Predicted={pred:.1f}, True={true:.1f}, Error={abs(pred-true):.1f}, Confidence={conf:.2f}")
        
        # Update personalization
        session_data = {
            'start_time': timestamps[0],
            'productivity_score': 0.7
        }
        personalization.update_profile(session_data, [p[1] for p in session_predictions])
    
    # Save final model
    print("\n" + "="*70)
    print("TRAINING COMPLETE - SAVING MODEL")
    print("="*70)
    
    ml_predictor.save_model()
    
    # Final statistics
    print(f"\n📊 **FINAL MODEL STATISTICS**\n")
    
    metrics = ml_predictor.get_performance_metrics()
    print(f"Total Samples Trained: {ml_predictor._training_samples_count}")
    print(f"Model Initialized: {ml_predictor._is_initialized}")

    
    print(f"\n📉 **ERROR PROGRESSION**")
    print(f"First 5 sessions MAE: {np.mean(all_maes[:5]):.2f}")
    print(f"Last 5 sessions MAE: {np.mean(all_maes[-5:]):.2f}")
    improvement = ((np.mean(all_maes[:5]) - np.mean(all_maes[-5:])) / np.mean(all_maes[:5])) * 100
    print(f"Improvement: {improvement:.1f}%")
    
    print(f"\n🎯 **TOP 5 IMPORTANT FEATURES**")
    top_features = ml_predictor.get_top_features(5)
    for name, importance in top_features:
        print(f"  {name:30s}: {importance:.4f}")
    
    print(f"\n👤 **PERSONALIZATION**")
    pers_stats = personalization.get_profile_stats()
    print(f"Total Sessions: {pers_stats['total_sessions']}")
    print(f"Personalization Score: {pers_stats['personalization_score']:.2f}")
    print(f"ML Weight: {pers_stats['ml_weight']:.2f}")
    print(f"Adaptive Thresholds: Low={pers_stats['adaptive_thresholds']['low']:.1f}, " +
          f"Moderate={pers_stats['adaptive_thresholds']['moderate']:.1f}, " +
          f"High={pers_stats['adaptive_thresholds']['high']:.1f}")
    
    print("\n" + "="*70)
    print("✅ MODEL TRAINED AND SAVED SUCCESSFULLY!")
    print("="*70)
    
    return ml_predictor, personalization


if __name__ == "__main__":
    # Train with different profiles
    profiles = ['normal']  # Can also try: 'morning_person', 'night_owl', 'workaholic'
    
    for profile in profiles:
        print("\n\n")
        ml_predictor, personalization = train_model_with_synthetic_data(
            num_sessions=25,
            profile=profile
        )
        print(f"\n💾 Model saved to: models/current_model.pkl")
        print(f"📁 Profile saved to: data/profiles/user_profile.json")
