"""Test script for psychometric dataset integration"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ml.psychometric_loader import PsychometricLoader
from src.ml.dataset_preprocessor import DatasetPreprocessor
from src.ml.ml_predictor import MLPredictor
from src.analysis.fatigue_analyzer import FatigueAnalyzer
import numpy as np


def test_loader():
    """Test psychometric data loading"""
    print("\n" + "="*60)
    print("TEST 1: Loading Psychometric Datasets")
    print("="*60)
    
    loader = PsychometricLoader()
    
    # Test NASA-TLX
    print("\n📊 Loading NASA-TLX dataset...")
    try:
        nasa_dataset = loader.load_dataset('data/psychometric_datasets/sample_nasatlx_workload.csv')
        print(f"✅ Loaded: {nasa_dataset}")
        print(f"   Organization: {nasa_dataset.organization}")
        print(f"   Assessment: {nasa_dataset.assessment_type}")
        print(f"   Samples: {len(nasa_dataset.data)}")
        print(f"   First row: {nasa_dataset.data.iloc[0].to_dict()}")
        
        # Get statistics
        stats = loader.get_statistics(nasa_dataset)
        print(f"\n   Statistics:")
        print(f"   - Fatigue score range: {stats['fatigue_score']['min']:.1f} - {stats['fatigue_score']['max']:.1f}")
        print(f"   - Mean fatigue: {stats['fatigue_score']['mean']:.1f}")
        print(f"   - Participants: {stats['participant_count']}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test CFQ
    print("\n📊 Loading CFQ dataset...")
    try:
        cfq_dataset = loader.load_dataset('data/psychometric_datasets/sample_cfq_fatigue.csv')
        print(f"✅ Loaded: {cfq_dataset}")
        print(f"   Organization: {cfq_dataset.organization}")
        print(f"   Assessment: {cfq_dataset.assessment_type}")
        print(f"   Samples: {len(cfq_dataset.data)}")
        
        stats = loader.get_statistics(cfq_dataset)
        print(f"\n   Statistics:")
        print(f"   - Fatigue score range: {stats['fatigue_score']['min']:.1f} - {stats['fatigue_score']['max']:.1f}")
        print(f"   - Mean fatigue: {stats['fatigue_score']['mean']:.1f}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    return True


def test_preprocessing():
    """Test feature preprocessing"""
    print("\n" + "="*60)
    print("TEST 2: Feature Preprocessing")
    print("="*60)
    
    loader = PsychometricLoader()
    preprocessor = DatasetPreprocessor()
    
    # Preprocess NASA-TLX
    print("\n🔧 Preprocessing NASA-TLX dataset...")
    try:
        nasa_dataset = loader.load_dataset('data/psychometric_datasets/sample_nasatlx_workload.csv')
        features, targets = preprocessor.preprocess_nasa_tlx(nasa_dataset)
        
        print(f"✅ Preprocessed: {features.shape[0]} samples, {features.shape[1]} features")
        print(f"   Feature range: {features.min():.2f} - {features.max():.2f}")
        print(f"   Target range: {targets.min():.1f} - {targets.max():.1f}")
        print(f"   Sample feature vector (first 10): {features[0][:10]}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Preprocess CFQ
    print("\n🔧 Preprocessing CFQ dataset...")
    try:
        cfq_dataset = loader.load_dataset('data/psychometric_datasets/sample_cfq_fatigue.csv')
        features, targets = preprocessor.preprocess_cfq(cfq_dataset)
        
        print(f"✅ Preprocessed: {features.shape[0]} samples, {features.shape[1]} features")
        print(f"   Feature range: {features.min():.2f} - {features.max():.2f}")
        print(f"   Target range: {targets.min():.1f} - {targets.max():.1f}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    return True


def test_training():
    """Test model training from psychometric data"""
    print("\n" + "="*60)
    print("TEST 3: Model Training")
    print("="*60)
    
    print("\n🧠 Training ML model with NASA-TLX data...")
    try:
        predictor = MLPredictor()
        stats = predictor.train_from_psychometric_dataset(
            'data/psychometric_datasets/sample_nasatlx_workload.csv'
        )
        
        print(f"✅ Training complete!")
        print(f"   Organization: {stats['organization']}")
        print(f"   Assessment: {stats['assessment_type']}")
        print(f"   Training samples: {stats['sample_count']}")
        print(f"   Total model samples: {stats['model_samples']}")
        print(f"   Mean fatigue: {stats['fatigue_score']['mean']:.1f}")
        
        # Test prediction
        print("\n🔮 Testing prediction...")
        loader = PsychometricLoader()
        preprocessor = DatasetPreprocessor()
        dataset = loader.load_dataset('data/psychometric_datasets/sample_nasatlx_workload.csv')
        features, targets = preprocessor.preprocess_nasa_tlx(dataset)
        
        pred, conf = predictor.predict(features[0])
        actual = targets[0]
        error = abs(pred - actual)
        
        print(f"   Predicted: {pred:.1f}")
        print(f"   Actual: {actual:.1f}")
        print(f"   Error: {error:.1f}")
        print(f"   Confidence: {conf:.2f}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_fatigue_analyzer_integration():
    """Test integration with FatigueAnalyzer"""
    print("\n" + "="*60)
    print("TEST 4: FatigueAnalyzer Integration")
    print("="*60)
    
    print("\n🔗 Training through FatigueAnalyzer...")
    try:
        analyzer = FatigueAnalyzer(use_ml=True)
        
        stats = analyzer.train_from_psychometric_file(
            'data/psychometric_datasets/sample_nasatlx_workload.csv'
        )
        
        if 'error' in stats:
            print(f"❌ Failed: {stats['error']}")
            return False
        
        print(f"✅ Training successful!")
        print(f"   Samples: {stats['sample_count']}")
        print(f"   Model samples: {stats['model_samples']}")
        
        # Get ML stats
        ml_stats = analyzer.get_ml_stats()
        print(f"\n📊 ML Statistics:")
        print(f"   Enabled: {ml_stats['enabled']}")
        print(f"   samples: {ml_stats['model_performance'].get('samples_count', 0)}")
        print(f"   Initialized: {ml_stats['model_performance'].get('is_initialized', False)}")
        
        # Get dataset statistics
        dataset_stats = analyzer.get_dataset_statistics()
        print(f"\n📈 Dataset Statistics:")
        print(f"   Total samples: {dataset_stats['total_samples']}")
        print(f"   Model initialized: {dataset_stats['model_initialized']}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PSYCHOMETRIC INTEGRATION TEST SUITE")
    print("="*60)
    
    tests = [
        ('Data Loading', test_loader),
        ('Feature Preprocessing', test_preprocessing),
        ('Model Training', test_training),
        ('FatigueAnalyzer Integration', test_fatigue_analyzer_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test {name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
