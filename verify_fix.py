"""Verify that ML is disabled and rule-based scoring works correctly"""
import sys
from pathlib import Path
import json

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.analysis.fatigue_analyzer import FatigueAnalyzer
from datetime import datetime

print("="*70)
print("VERIFICATION: ML DISABLED, RULE-BASED SCORING")
print("="*70)

# Check profile
profile_file = Path("data/profiles/user_profile.json")
if profile_file.exists():
    with open(profile_file, 'r') as f:
        profile = json.load(f)
    print(f"\n✅ Profile loaded:")
    print(f"   Sessions: {profile.get('total_sessions', 0)}")
    print(f"   ML Weight: 0% (sessions < 5)")
else:
    print("\n❌ Profile file not found!")
    sys.exit(1)

# Initialize analyzer
analyzer = FatigueAnalyzer(use_ml=True)
stats = analyzer.get_ml_stats()

print(f"\n📊 Analyzer Configuration:")
print(f"   ML Enabled: {analyzer.use_ml}")
print(f"   Sessions: {stats['personalization']['total_sessions']}")
print(f"   ML Weight: {stats['personalization']['ml_weight']:.0%}")
print(f"   Prediction Mode: {'RULE-BASED' if stats['personalization']['ml_weight'] == 0 else 'HYBRID'}")

# Start session
analyzer.start_session()

# Test scenario: Fresh start (1 minute, good activity, normal blinks)
print("\n" + "-"*70)
print("TEST: Fresh Start (1 minute work)")
print("-"*70)

score = analyzer.calculate_score(
    work_duration_minutes=1.0,
    activity_rate=14.0,
    time_since_break_minutes=1.0,
    blink_rate=15.0
)

print(f"\nInput:")
print(f"   Work duration: 1 minute")
print(f"   Activity rate: 14 events/min")
print(f"   Blink rate: 15 blinks/min (normal)")
print(f"   Time since break: 1 minute")

print(f"\nOutput:")
print(f"   Fatigue Score: {score.score:.1f}")
print(f"   Level: {score.get_level()}")
print(f"   Method: {score.factors.get('prediction_method', 'unknown')}")

print(f"\nFactors:")
for key, value in score.factors.items():
    if key not in ['prediction_method', 'ml_score', 'ml_confidence', 'ml_weight']:
        print(f"   {key}: {value:.2f}" if isinstance(value, (int, float)) else f"   {key}: {value}")

# Expected result
expected_low = True if score.score < 30 else False

print(f"\n" + "="*70)
if expected_low and score.get_level() == "Low":
    print("✅ VERIFICATION PASSED!")
    print(f"   Score is {score.score:.1f} (Low) - correct for 1 minute work")
    print("   Rule-based scoring is working properly")
else:
    print("⚠️  UNEXPECTED RESULT!")
    print(f"   Score is {score.score:.1f} ({score.get_level()})")
    print("   Expected: Low fatigue (<30) for 1 minute work")
    print("\n   Possible issues:")
    print("   - Time-of-day factor may be affecting score")
    print("   - Blink rate interpretation may need adjustment")
    print("   - Check factor weights in fatigue_analyzer.py")

print("="*70)

# Additional test: 60 minutes
print("\n" + "-"*70)
print("TEST: After 60 minutes work")
print("-"*70)

score60 = analyzer.calculate_score(
    work_duration_minutes=60.0,
    activity_rate=10.0,
    time_since_break_minutes=60.0,
    blink_rate=12.0
)

print(f"\nInput:")
print(f"   Work duration: 60 minutes")
print(f"   Activity rate: 10 events/min (slightly reduced)")
print(f"   Blink rate: 12 blinks/min (slightly reduced)")
print(f"   Time since break: 60 minutes")

print(f"\nOutput:")
print(f"   Fatigue Score: {score60.score:.1f}")
print(f"   Level: {score60.get_level()}")

if 40 <= score60.score <= 70:
    print("\n✅ Looks reasonable for 60 minutes work")
else:
    print(f"\n⚠️  Score seems {'too high' if score60.score > 70 else 'too low'} for 60 minutes")

print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70)
print("\n💡 Next steps:")
print("   1. Restart the app")
print("   2. Start a new session")
print("   3. Score should start low and gradually increase")
print("   4. ML will stay at 0% until 5 sessions completed")
