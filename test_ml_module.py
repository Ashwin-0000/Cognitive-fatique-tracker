"""Test script for ML module functionality"""
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


def test_feature_engineering():
    """Test feature engineering"""
    print("Testing Feature Engineering...")
    
    fe = FeatureEngineer()
    fe.start_session()
    
    # Add some activity data
    for i in range(20):
        activity = ActivityData('keyboard', datetime.now() - timedelta(seconds=i*3))
        fe.add_activity(activity)
    
    # Extract features
    features = fe.extract_features(
        blink_rate=15.0,
        session_duration_minutes=10.0,
        time_since_break_minutes=5.0
    )
    
    print(f"  ✓ Extracted {len(features)} features")
    print(f"  ✓ Feature vector shape: {features.shape}")
    assert len(features) == 28, f"Expected 28 features, got {len(features)}"
    print("  ✓ Feature engineering working!\n")
    
    return fe


def test_ml_predictor(fe):
    """Test ML predictor"""
    print("Testing ML Predictor...")
    
    predictor = MLPredictor(feature_engineer=fe)
    
    # Test prediction before training (should return neutral)
    features = fe.extract_features(blink_rate=15.0)
    score, confidence = predictor.predict(features)
    print(f"  ✓ Initial prediction: {score:.1f} (confidence: {confidence:.2f})")
    assert score == 50.0, "Expected neutral score before training"
    assert confidence == 0.0, "Expected zero confidence before training"
    
    # Add training samples
    print("  Training with synthetic data...")
    np.random.seed(42)
    for i in range(30):
        # Create synthetic features
        synthetic_features = np.random.rand(28) * 50
        # Create target based on some features (simulate pattern)
        target = 30 + synthetic_features[0] * 0.5 + synthetic_features[8] * 0.3
        target = np.clip(target, 0, 100)
        
        predictor.partial_fit(synthetic_features, target)
    
    print(f"  ✓ Trained with 30 samples")
    
    # Test prediction after training
    features = fe.extract_features(blink_rate=15.0)
    score, confidence = predictor.predict(features)
    print(f"  ✓ Prediction after training: {score:.1f} (confidence: {confidence:.2f})")
    assert confidence > 0.0, "Expected non-zero confidence after training"
    
    # Test feature importance
    importance = predictor.get_top_features(5)
    print(f"  ✓ Top 5 important features:")
    for name, imp in importance[:5]:
        print(f"     - {name}: {imp:.4f}")
    
    # Test performance metrics
    metrics = predictor.get_performance_metrics()
    print(f"  ✓ Model metrics: {metrics}")
    
    print("  ✓ ML Predictor working!\n")
    
    return predictor


def test_personalization():
    """Test personalization engine"""
    print("Testing Personalization Engine...")
    
    pe = PersonalizationEngine()
    
    # Get initial stats
    stats = pe.get_profile_stats()
    print(f"  ✓ Initial sessions: {stats['total_sessions']}")
    print(f"  ✓ Personalization score: {stats['personalization_score']:.2f}")
    print(f"  ✓ ML weight: {stats['ml_weight']:.2f}")
    
    # Simulate session
    session_data = {
        'start_time': datetime.now() - timedelta(hours=1),
        'productivity_score': 0.7
    }
    fatigue_scores = [20, 25, 30, 35, 40, 45]
    
    pe.update_profile(session_data, fatigue_scores)
    
    # Check updated stats
    stats = pe.get_profile_stats()
    print(f"  ✓ Sessions after update: {stats['total_sessions']}")
    print(f"  ✓ Adaptive thresholds: {stats['adaptive_thresholds']}")
    
    print("  ✓ Personalization working!\n")
    
    return pe


def test_integration():
    """Test integrated workflow"""
    print("\nTesting Integrated Workflow...")
    
    from src.analysis.fatigue_analyzer import FatigueAnalyzer
    
    analyzer = FatigueAnalyzer(use_ml=True)
    
    if not analyzer.use_ml:
        print("  ⚠ ML not available in analyzer")
        return
    
    print(f"  ✓ ML enabled: {analyzer.use_ml}")
    
    # Start session
    analyzer.start_session()
    
    # Add some activities
    for i in range(15):
        activity = ActivityData('keyboard', datetime.now() - timedelta(seconds=i*2))
        analyzer.add_activity(activity)
    
    # Calculate score
    score = analyzer.calculate_score(
        work_duration_minutes=15.0,
        activity_rate=5.0,
        time_since_break_minutes=10.0,
        blink_rate=14.0
    )
    
    print(f"  ✓ Fatigue score: {score.score:.1f} ({score.get_level()})")
    print(f"  ✓ Prediction method: {score.factors.get('prediction_method', 'unknown')}")
    
    if 'ml_score' in score.factors:
        print(f"  ✓ ML score: {score.factors['ml_score']:.1f}")
        print(f"  ✓ ML confidence: {score.factors['ml_confidence']:.2f}")
        print(f"  ✓ ML weight: {score.factors['ml_weight']:.2f}")
    
    # Get ML stats
    ml_stats = analyzer.get_ml_stats()
    print(f"  ✓ ML Stats: {ml_stats['enabled']}")
    
    print("  ✓ Integration working!\n")


def main():
    """Run all tests"""
    print("="*60)
    print("ML MODULE TEST SUITE")
    print("="*60 + "\n")
    
    try:
        # Test individual components
        fe = test_feature_engineering()
        predictor = test_ml_predictor(fe)
        pe = test_personalization()
        
        # Test integration
        test_integration()
        
        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
