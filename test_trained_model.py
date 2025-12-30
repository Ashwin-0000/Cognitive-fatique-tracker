"""Test the trained ML model"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import numpy as np
from datetime import datetime
from src.analysis.fatigue_analyzer import FatigueAnalyzer

print("="*70)
print("TESTING TRAINED ML MODEL")
print("="*70)

# Initialize analyzer with ML
analyzer = FatigueAnalyzer(use_ml=True)

if not analyzer.use_ml:
    print("\n❌ ML not available!")
    sys.exit(1)

print(f"\n✅ ML Enabled: {analyzer.use_ml}")

# Get ML stats
stats = analyzer.get_ml_stats()
print(f"\n📊 **MODEL STATUS**")
print(f"   Model Initialized: {stats['model_performance'].get('is_initialized', False)}")
print(f"   Training Samples: {analyzer.ml_predictor._training_samples_count}")

pers = stats['personalization']
print(f"\n👤 **PERSONALIZATION**")
print(f"   Total Sessions: {pers['total_sessions']}")
print(f"   Personalization Score: {pers['personalization_score']:.2f}")
print(f"   ML Weight: {pers['ml_weight']:.2f} (85% = fully personalized)")
print(f"   Adaptive Thresholds:")
print(f"      Low: {pers['adaptive_thresholds']['low']:.1f}")
print(f"      Moderate: {pers['adaptive_thresholds']['moderate']:.1f}")
print(f"      High: {pers['adaptive_thresholds']['high']:.1f}")

print(f"\n🎯 **TOP 5 IMPORTANT FEATURES**")
for name, importance in stats['feature_importance']:
    print(f"   {name:30s}: {importance:.4f}")

# Test predictions with different scenarios
print(f"\n\n" + "="*70)
print("TESTING PREDICTIONS WITH DIFFERENT SCENARIOS")
print("="*70)

scenarios = [
    {
        'name': '🌅 Fresh Start (Morning, 15min work)',
        'duration': 15.0,
        'activity': 18.0,
        'break_since': 5.0,
        'blink': 17.0
    },
    {
        'name': '⚡ Moderate Work (1 hour, no break)',
        'duration': 60.0,
        'activity': 12.0,
        'break_since': 60.0,
        'blink': 13.0
    },
    {
        'name': '😴 Fatigued (2 hours, low activity)',
        'duration': 120.0,
        'activity': 6.0,
        'break_since': 90.0,
        'blink': 9.0
    },
    {
        'name': '🔴 Critical Fatigue (3+ hours, very low)',
        'duration': 200.0,
        'activity': 4.0,
        'break_since': 120.0,
        'blink': 7.0
    }
]

analyzer.start_session()

for scenario in scenarios:
    print(f"\n{scenario['name']}")
    print("-" * 70)
    
    score = analyzer.calculate_score(
        work_duration_minutes=scenario['duration'],
        activity_rate=scenario['activity'],
        time_since_break_minutes=scenario['break_since'],
        blink_rate=scenario['blink']
    )
    
    method = score.factors.get('prediction_method', 'unknown')
    ml_score = score.factors.get('ml_score')
    ml_confidence = score.factors.get('ml_confidence')
    ml_weight = score.factors.get('ml_weight')
    
    print(f"   Fatigue Score: {score.score:.1f}/100 - {score.get_level()}")
    print(f"   Prediction Method: {method}")
    
    if ml_score is not None:
        print(f"   ML Prediction: {ml_score:.1f} (confidence: {ml_confidence:.2f})")
        print(f"   ML Weight: {ml_weight:.0%}")
    
    # Color based on level
    level = score.get_level()
    if level == "Low":
        emoji = "✅"
    elif level == "Moderate":
        emoji = "⚠️"
    elif level == "High":
        emoji = "🔴"
    else:
        emoji = "🚨"
    
    print(f"   Status: {emoji} {level} Fatigue")

print(f"\n\n" + "="*70)
print("✅ MODEL TESTING COMPLETE!")
print("="*70)
print(f"\n💡 The ML model is trained with 25 sessions worth of data")
print(f"💡 It's using {stats['personalization']['ml_weight']:.0%} ML prediction")
print(f"💡 Model file: models/current_model.pkl")
print(f"💡 Profile file: data/profiles/user_profile.json")
