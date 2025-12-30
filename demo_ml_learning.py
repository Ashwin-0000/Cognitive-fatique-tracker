"""Interactive demo showing ML model learning and predictions"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import numpy as np
from datetime import datetime, timedelta
from src.analysis.fatigue_analyzer import FatigueAnalyzer
from src.models.activity_data import ActivityData
import time


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_section(text):
    """Print formatted section"""
    print(f"\n{'─'*70}")
    print(f"  {text}")
    print(f"{'─'*70}")


def simulate_work_session(analyzer, session_name, duration_minutes, scenario):
    """Simulate a work session with predictions"""
    print_section(f"📅 {session_name}")
    
    # Start session
    analyzer.start_session()
    
    # Simulate activity over time
    num_samples = max(1, int(duration_minutes / 5))  # Sample every 5 minutes
    predictions = []
    
    print(f"\n⏱️  Duration: {duration_minutes} minutes")
    print(f"📊 Scenario: {scenario['description']}")
    print(f"\n{'Time':<10} {'Activity':<10} {'Blinks':<10} {'Prediction':<12} {'Level':<12} {'Method':<15}")
    print("-" * 70)
    
    for i in range(num_samples):
        elapsed = (i + 1) * 5
        
        # Simulate declining activity and blinks with fatigue
        fatigue_factor = elapsed / duration_minutes
        activity = scenario['initial_activity'] * (1 - fatigue_factor * scenario['activity_decline'])
        blink_rate = scenario['initial_blinks'] * (1 - fatigue_factor * scenario['blink_decline'])
        
        # Add some noise
        activity = max(3, activity + np.random.randn() * 1.5)
        blink_rate = max(7, blink_rate + np.random.randn() * 1.0)
        
        # Generate some activities
        for _ in range(int(activity * 5)):  # activities per 5 min
            event_type = 'keyboard' if np.random.rand() > 0.3 else 'mouse_click'
            analyzer.add_activity(ActivityData(event_type, datetime.now()))
        
        # Get prediction
        score = analyzer.calculate_score(
            work_duration_minutes=elapsed,
            activity_rate=activity,
            time_since_break_minutes=elapsed,
            blink_rate=blink_rate
        )
        
        predictions.append({
            'time': elapsed,
            'score': score.score,
            'level': score.get_level(),
            'method': score.factors.get('prediction_method', 'rule_based'),
            'ml_score': score.factors.get('ml_score'),
            'ml_weight': score.factors.get('ml_weight', 0.0)
        })
        
        # Print prediction
        method = score.factors.get('prediction_method', 'rule_based')
        method_display = f"{method}"
        if score.factors.get('ml_weight'):
            method_display += f" ({score.factors['ml_weight']:.0%})"
        
        print(f"{elapsed:>3} min    {activity:>5.1f}     {blink_rate:>6.1f}     {score.score:>6.1f}      {score.get_level():<12} {method_display}")
    
    # Train model with session data
    print(f"\n🎓 Training model with session data...")
    analyzer.train_ml_model()
    
    # Show summary
    final = predictions[-1]
    print(f"\n📈 Session Summary:")
    print(f"   Final Fatigue: {final['score']:.1f} ({final['level']})")
    print(f"   Prediction Method: {final['method']}")
    if final['ml_weight'] > 0:
        print(f"   ML Influence: {final['ml_weight']:.0%}")
    
    return predictions


def main():
    """Run interactive demo"""
    print_header("🧠 ML MODEL INCREMENTAL LEARNING DEMO")
    
    print("\nThis demo shows how the ML model:")
    print("  1. Makes predictions using the trained model")
    print("  2. Learns incrementally from each session")
    print("  3. Improves predictions over time")
    print("\nLoading ML model...")
    
    # Create analyzer with ML
    analyzer = FatigueAnalyzer(use_ml=True)
    
    if not analyzer.use_ml:
        print("❌ ML not available!")
        return
    
    print("✅ ML model loaded!")
    
    # Get initial stats
    stats = analyzer.get_ml_stats()
    pers = stats['personalization']
    
    print(f"\n📊 Initial Model State:")
    print(f"   Training Samples: {analyzer.ml_predictor._training_samples_count}")
    print(f"   Personalization: {pers['personalization_score']:.0%}")
    print(f"   ML Weight: {pers['ml_weight']:.0%}")
    
    print(f"\n🎯 Top 3 Important Features:")
    for name, importance in stats['feature_importance'][:3]:
        print(f"   • {name}: {importance:.3f}")
    
    # Define scenarios
    scenarios = [
        {
            'name': 'Light Morning Work Session',
            'duration': 45,
            'description': 'Fresh start, high productivity',
            'initial_activity': 18.0,
            'initial_blinks': 17.0,
            'activity_decline': 0.2,
            'blink_decline': 0.15
        },
        {
            'name': 'Focused Afternoon Work',
            'duration': 90,
            'description': 'Extended focus, gradual fatigue',
            'initial_activity': 15.0,
            'initial_blinks': 15.0,
            'activity_decline': 0.4,
            'blink_decline': 0.35
        },
        {
            'name': 'Intense Deep Work Session',
            'duration': 120,
            'description': 'Long session, high cognitive load',
            'initial_activity': 20.0,
            'initial_blinks': 16.0,
            'activity_decline': 0.5,
            'blink_decline': 0.45
        }
    ]
    
    print_header("RUNNING SIMULATED SESSIONS")
    
    all_session_results = []
    
    # Run scenarios
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n\n{'#'*70}")
        print(f"  SESSION {i}/{len(scenarios)}")
        print(f"{'#'*70}")
        
        predictions = simulate_work_session(
            analyzer,
            scenario['name'],
            scenario['duration'],
            scenario
        )
        
        all_session_results.append({
            'name': scenario['name'],
            'predictions': predictions
        })
        
        # Show updated stats
        stats = analyzer.get_ml_stats()
        pers = stats['personalization']
        
        print(f"\n📊 Updated Model State:")
        print(f"   Training Samples: {analyzer.ml_predictor._training_samples_count}")
        print(f"   Personalization: {pers['personalization_score']:.0%}")
        print(f"   ML Weight: {pers['ml_weight']:.0%}")
        
        if i < len(scenarios):
            print(f"\n{'⏳ Preparing next session...':^70}")
            time.sleep(1)
    
    # Final summary
    print_header("📊 FINAL RESULTS")
    
    print(f"\n🎓 Model Training Complete!")
    print(f"\n   Sessions Processed: {len(scenarios)}")
    
    stats = analyzer.get_ml_stats()
    pers = stats['personalization']
    perf = stats['model_performance']
    
    print(f"\n📈 Final Model Metrics:")
    print(f"   Total Training Samples: {analyzer.ml_predictor._training_samples_count}")
    print(f"   Model Initialized: {analyzer.ml_predictor._is_initialized}")
    print(f"   Personalization Score: {pers['personalization_score']:.2f}")
    print(f"   ML Weight: {pers['ml_weight']:.0%}")
    
    print(f"\n🔧 Adaptive Thresholds (Personalized):")
    thresholds = pers['adaptive_thresholds']
    print(f"   Low Fatigue:      < {thresholds['low']:.1f}")
    print(f"   Moderate Fatigue: < {thresholds['moderate']:.1f}")
    print(f"   High Fatigue:     < {thresholds['high']:.1f}")
    print(f"   Critical Fatigue: ≥ {thresholds['high']:.1f}")
    
    print(f"\n🎯 Top 5 Most Important Features:")
    for i, (name, importance) in enumerate(stats['feature_importance'][:5], 1):
        bar = '█' * int(importance * 100)
        print(f"   {i}. {name:30s} {bar} {importance:.4f}")
    
    print_header("✅ DEMO COMPLETE")
    
    print("\n🎉 Key Takeaways:")
    print("   • ML model makes predictions in real-time")
    print("   • Learning happens incrementally after each session")
    print(f"   • Model is now using {pers['ml_weight']:.0%} ML-based predictions")
    print("   • Personalization adapts to user patterns")
    print("   • Feature importance shows what matters most")
    
    print("\n💾 Model State:")
    print(f"   • Model file: models/current_model.pkl")
    print(f"   • Profile: data/profiles/user_profile.json")
    print(f"   • Ready for production use!")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
