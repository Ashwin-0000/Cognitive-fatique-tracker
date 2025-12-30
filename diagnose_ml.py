"""Diagnose ML prediction issues"""
import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import numpy as np
from datetime import datetime
from src.analysis.fatigue_analyzer import FatigueAnalyzer
from src.models.activity_data import ActivityData

print("="*70)
print("ML PREDICTION DIAGNOSTICS")
print("="*70)

# Initialize analyzer
analyzer = FatigueAnalyzer(use_ml=True)

if not analyzer.use_ml:
    print("\n❌ ML not available!")
    sys.exit(1)

print(f"\n✅ ML enabled")
print(f"Training samples: {analyzer.ml_predictor._training_samples_count}")

# Start session
analyzer.start_session()

# Test with minimal activity (fresh start scenario)
print("\n" + "-"*70)
print("TEST 1: Fresh Start (5 min, high activity)")
print("-"*70)

# Add some activities
for i in range(50):  # 50 events = 10 events/min
    analyzer.add_activity(ActivityData('keyboard', datetime.now()))

score = analyzer.calculate_score(
    work_duration_minutes=5.0,
    activity_rate=10.0,
    time_since_break_minutes=5.0,
    blink_rate=17.0
)

print(f"\nInput parameters:")
print(f"  Duration: 5 minutes")
print(f"  Activity rate: 10 events/min")
print(f"  Blink rate: 17 blinks/min (normal)")
print(f"  Time since break: 5 minutes")

print(f"\nPrediction results:")
print(f"  Final score: {score.score:.1f}")
print(f"  Level: {score.get_level()}")
print(f"  Method: {score.factors.get('prediction_method', 'unknown')}")

if 'ml_score' in score.factors:
    print(f"\n  ML Details:")
    print(f"    ML score: {score.factors['ml_score']:.1f}")
    print(f"    ML confidence: {score.factors['ml_confidence']:.3f}")
    print(f"    ML weight: {score.factors['ml_weight']:.3f}")
    print(f"    Rule-based would be: ~{score.score / (score.factors['ml_weight'] * score.factors['ml_score'] / score.score + (1-score.factors['ml_weight'])):.1f}")

print(f"\n  Contributing factors:")
for key, value in score.factors.items():
    if key not in ['prediction_method', 'ml_score', 'ml_confidence', 'ml_weight']:
        print(f"    {key}: {value}")

# Extract features to see what's being fed to model
print(f"\n" + "-"*70)
print("FEATURE EXTRACTION ANALYSIS")
print("-"*70)

features = analyzer.feature_engineer.extract_features(
    current_time=datetime.now(),
    blink_rate=17.0,
    session_duration_minutes=5.0,
    time_since_break_minutes=5.0
)

feature_names = analyzer.feature_engineer.get_feature_names()

print(f"\nExtracted {len(features)} features:")
print(f"{'Feature Name':<35} {'Value':>10}")
print("-"*47)
for name, value in zip(feature_names, features):
    print(f"{name:<35} {value:>10.2f}")

# Check model predictions directly
print(f"\n" + "-"*70)
print("DIRECT MODEL PREDICTION")
print("-"*70)

ml_score, ml_confidence = analyzer.ml_predictor.predict(features)
print(f"\nDirect ML prediction: {ml_score:.1f}")
print(f"Confidence: {ml_confidence:.3f}")

# Get feature importance
print(f"\n" + "-"*70)
print("FEATURE IMPORTANCE")
print("-"*70)

importance = analyzer.ml_predictor.get_top_features(10)
print(f"\nTop 10 features affecting prediction:")
for i, (name, imp) in enumerate(importance, 1):
    feature_idx = feature_names.index(name)
    feature_value = features[feature_idx]
    print(f"{i:2d}. {name:<30} importance={imp:.4f}  value={feature_value:>8.2f}")

# Check model statistics
print(f"\n" + "-"*70)
print("MODEL STATISTICS")
print("-"*70)

stats = analyzer.get_ml_stats()
pers = stats['personalization']

print(f"\nPersonalization:")
print(f"  Total sessions: {pers['total_sessions']}")
print(f"  Personalization score: {pers['personalization_score']:.2f}")
print(f"  ML weight: {pers['ml_weight']:.2f}")
print(f"  Thresholds: Low={pers['adaptive_thresholds']['low']:.1f}, " +
      f"Mod={pers['adaptive_thresholds']['moderate']:.1f}, " +
      f"High={pers['adaptive_thresholds']['high']:.1f}")

print("\n" + "="*70)
print("DIAGNOSIS COMPLETE")
print("="*70)

print("\n🔍 Analysis:")
print("  1. Check if ML score is much higher than expected")
print("  2. Look at which features have high values")
print("  3. Compare feature values to what you'd expect")
print("  4. Model may be overtrained on synthetic data patterns")

print("\n💡 Possible fixes:")
print("  1. Reset model and retrain with real data")
print("  2. Lower ML weight initially")
print("  3. Add feature normalization bounds")
print("  4. Adjust baseline values for real usage")
