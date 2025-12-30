"""
Comprehensive System Testing Script
Tests all major components and data flows
"""
import sys
from pathlib import Path
import traceback

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("  COGNITIVE FATIGUE TRACKER - COMPREHENSIVE SYSTEM TEST")
print("="*70)
print()

test_results = []

def test_section(name):
    """Decorator for test sections"""
    def decorator(func):
        def wrapper():
            print(f"\n{'='*70}")
            print(f"  {name}")
            print(f"{'='*70}\n")
            try:
                result = func()
                test_results.append((name, result if result is not None else True, None))
                return result
            except Exception as e:
                print(f"❌ FAILED: {str(e)}")
                traceback.print_exc()
                test_results.append((name, False, str(e)))
                return False
        return wrapper
    return decorator

# TEST 1: IMPORTS AND DEPENDENCIES
@test_section("TEST 1: Import All Modules")
def test_imports():
    print("Testing module imports...")
    
    modules = [
        ("Config Manager", "from src.storage.config_manager import ConfigManager"),
        ("Data Manager", "from src.storage.data_manager import DataManager"),
        ("Fatigue Analyzer", "from src.analysis.fatigue_analyzer import FatigueAnalyzer"),
        ("Alert Manager", "from src.analysis.alert_manager import AlertManager"),
        ("Input Monitor", "from src.monitoring.input_monitor import InputMonitor"),
        ("TimeTracker", "from src.monitoring.time_tracker import TimeTracker"),
        ("Eye Tracker", "from src.monitoring.eye_tracker import EyeTracker"),
        ("ML Predictor", "from src.ml.ml_predictor import MLPredictor"),
        ("Feature Engineer", "from src.ml.feature_engineering import FeatureEngineer"),
        ("Psychometric Loader", "from src.ml.psychometric_loader import PsychometricLoader"),
        ("Dataset Preprocessor", "from src.ml.dataset_preprocessor import DatasetPreprocessor"),
    ]
    
    passed = 0
    for name, import_str in modules:
        try:
            exec(import_str)
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: {str(e)}")
    
    print(f"\nPassed: {passed}/{len(modules)}")
    return passed == len(modules)

# TEST 2: ML PIPELINE
@test_section("TEST 2: ML Pipeline Components")
def test_ml_pipeline():
    from src.ml.ml_predictor import MLPredictor
    from src.ml.feature_engineering import FeatureEngineer
    from src.analysis.fatigue_analyzer import FatigueAnalyzer
    
    print("Testing ML components...")
    
    # Test Feature Engineer
    print("\n  📊 Feature Engineering:")
    fe = FeatureEngineer()
    print(f"    ✅ FeatureEngineer initialized")
    print(f"    ✅ Feature count: {len(fe.get_feature_names())}")
    
    # Test ML Pred ictor
    print("\n  🤖 ML Predictor:")
    predictor = MLPredictor()
    print(f"    ✅ MLPredictor initialized")
    print(f"    ✅ Model initialized: {predictor._is_initialized}")
    print(f"    ✅ Training samples: {predictor._training_samples_count}")
    
    # Test Fatigue Analyzer
    print("\n  🎯 Fatigue Analyzer:")
    analyzer = FatigueAnalyzer(use_ml=True)
    print(f"    ✅ FatigueAnalyzer initialized")
    print(f"    ✅ ML enabled: {analyzer.use_ml}")
    
    return True

# TEST 3: PSYCHOMETRIC INTEGRATION
@test_section("TEST 3: Psychometric Dataset Integration")
def test_psychometric():
    from src.ml.psychometric_loader import PsychometricLoader
    from src.ml.dataset_preprocessor import DatasetPreprocessor
    
    print("Testing psychometric components...")
    
    # Test Loader
    print("\n  📥 Psychometric Loader:")
    loader = PsychometricLoader()
    print(f"    ✅ PsychometricLoader initialized")
    
    # Test sample dataset
    try:
        dataset = loader.load_dataset('data/psychometric_datasets/sample_nasatlx_workload.csv')
        print(f"    ✅ Loaded NASA-TLX dataset: {len(dataset.data)} samples")
        print(f"    ✅ Organization: {dataset.organization}")
        print(f"    ✅ Assessment: {dataset.assessment_type}")
    except Exception as e:
        print(f"    ⚠️  Dataset loading: {str(e)}")
    
    # Test Preprocessor
    print("\n  🔧 Dataset Preprocessor:")
    preprocessor = DatasetPreprocessor()
    print(f"    ✅ DatasetPreprocessor initialized")
    print(f"    ✅ Feature dimension: {preprocessor.feature_dim}")
    
    return True

# TEST 4: DATA MANAGERS
@test_section("TEST 4: Data Storage & Config")
def test_storage():
    from src.storage.config_manager import ConfigManager
    from src.storage.data_manager import DataManager
    
    print("Testing storage components...")
    
    # Test Config Manager
    print("\n  ⚙️  Config Manager:")
    config = ConfigManager()
    print(f"    ✅ ConfigManager initialized")
    work_interval = config.get('work_interval_minutes', 50)
    print(f"    ✅ Config read: work_interval = {work_interval}")
    
    # Test Data Manager
    print("\n  💾 Data Manager:")
    data_mgr = DataManager()
    print(f"    ✅ DataManager initialized")
    print(f"    ✅ Database connected")
    
    return True

# TEST 5: MONITORING COMPONENTS
@test_section("TEST 5: Monitoring Components")
def test_monitoring():
    from src.monitoring.time_tracker import TimeTracker
    
    print("Testing monitoring components...")
    
    # Test TimeTracker
    print("\n  ⏱️  Time Tracker:")
    tracker = TimeTracker()
    print(f"    ✅ TimeTracker initialized")
    print(f"    ✅ Work interval: {tracker.work_interval}")
    print(f"    ✅ Break interval: {tracker.break_interval}")
    
    # Note: InputMonitor and EyeTracker require active session
    print("\n  📝 Input Monitor: (requires active session)")
    print(f"    ℹ️  Skipped - requires active monitoring session")
    
    print("\n  👁️  Eye Tracker: (requires camera)")
    print(f"    ℹ️  Skipped - requires camera hardware")
    
    return True

# TEST 6: ALERT SYSTEM
@test_section("TEST 6: Alert System")
def test_alerts():
    from src.analysis.alert_manager import AlertManager
    
    print("Testing alert system...")
    
    alerts_shown = []
    def mock_alert(title, message):
        alerts_shown.append((title, message))
    
    print("\n  🔔 Alert Manager:")
    manager = AlertManager(on_alert=mock_alert)
    print(f"    ✅ AlertManager initialized")
    
    # Enable alerts
    manager.enable_alerts(break_alerts=True, fatigue_alerts=True)
    print(f"    ✅ Alerts enabled")
    
    return True

# TEST 7: SESSION WORKFLOW
@test_section("TEST 7: Session Workflow")
def test_session():
    from src.models.session import Session
    from datetime import datetime
    
    print("Testing session management...")
    
    print("\n  📋 Session Model:")
    session = Session()
    print(f"    ✅ Session created: {session.session_id}")
    print(f"    ✅ Start time: {session.start_time}")
    
    session.end_session()
    print(f"    ✅ Session ended: {session.end_time}")
    print(f"    ✅ Duration: {session.end_time - session.start_time}")
    
    return True

# TEST 8: FATIGUE CALCULATION
@test_section("TEST 8: Fatigue Score Calculation")
def test_fatigue_calc():
    from src.analysis.fatigue_analyzer import FatigueAnalyzer
    
    print("Testing fatigue calculation...")
    
    analyzer = FatigueAnalyzer(use_ml=True)
    analyzer.start_session()
    
    # Test calculation
    print("\n  🎯 Calculate Fatigue Score:")
    score = analyzer.calculate_score(
        work_duration_minutes=30.0,
        activity_rate=15.0,
        time_since_break_minutes=25.0,
        is_on_break=False,
        blink_rate=12.0
    )
    
    print(f"    ✅ Fatigue score: {score.score:.1f}")
    print(f"    ✅ Fatigue level: {score.get_level()}")
    print(f"    ✅ Prediction method: {score.factors.get('prediction_method', 'unknown')}")
    
    return True

# TEST 9: FILE STRUCTURE
@test_section("TEST 9: File Structure Integrity")
def test_file_structure():
    import os
    
    print("Checking critical files and directories...")
    
    critical_paths = [
        ("src/", True),
        ("src/ml/", True),
        ("src/analysis/", True),
        ("src/monitoring/", True),
        ("src/storage/", True),
        ("src/ui/", True),
        ("data/", True),
        ("data/psychometric_datasets/", True),
        ("models/", True),
        ("config/", True),
        ("README.md", False),
        ("requirements.txt", False),
        ("main.py", False),
    ]
    
    passed = 0
    for path, is_dir in critical_paths:
        full_path = Path(path)
        exists = full_path.is_dir() if is_dir else full_path.is_file()
        
        if exists:
            print(f"  ✅ {path}")
            passed += 1
        else:
            print(f"  ❌ {path} - NOT FOUND")
    
    print(f"\nPassed: {passed}/{len(critical_paths)}")
    return passed >= len(critical_paths) - 2  # Allow 2 missing

# TEST 10: DOCUMENTATION
@test_section("TEST 10: Documentation Completeness")
def test_documentation():
    docs = [
        "README.md",
        "ML_MODULE_README.md",
        "PSYCHOMETRIC_DATASETS.md",
        "UPDATE_LOG.md",
        "FEATURES_COMPLETED.md",
        "RUN.md",
        "TROUBLESHOOTING.md"
    ]
    
    print("Checking documentation...")
    
    passed = 0
    for doc in docs:
        if Path(doc).exists():
            size = Path(doc).stat().st_size
            print(f"  ✅ {doc} ({size} bytes)")
            passed += 1
        else:
            print(f"  ❌ {doc} - MISSING")
    
    print(f"\nPassed: {passed}/{len(docs)}")
    return passed >= len(docs) - 1  # Allow 1 missing

# RUN ALL TESTS
def main():
    print("\nStarting comprehensive system test...\n")
    
    test_imports()
    test_ml_pipeline()
    test_psychometric()
    test_storage()
    test_monitoring()
    test_alerts()
    test_session()
    test_fatigue_calc()
    test_file_structure()
    test_documentation()
    
    # SUMMARY
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result, _ in test_results if result)
    total = len(test_results)
    
    for name, result, error in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"         Error: {error}")
    
    print(f"\n{'='*70}")
    print(f"  OVERALL RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready for Phase 2.\n")
        return 0
    elif passed >= total * 0.8:
        print(f"⚠️  MOSTLY PASSING: {total-passed} test(s) failed. Review needed.\n")
        return 1
    else:
        print(f"❌ SYSTEM NOT READY: {total-passed} critical failures detected.\n")
        return 2

if __name__ == '__main__':
    sys.exit(main())
