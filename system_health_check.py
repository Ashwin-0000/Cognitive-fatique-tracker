"""
Quick System Health Check
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("  COGNITIVE FATIGUE TRACKER - SYSTEM HEALTH CHECK")
print("="*70 + "\n")

results = {"passed": [], "failed": [], "warnings": []}

# Test 1: Core Imports
print("TEST 1: Core Module Imports")
print("-"*70)
try:
    from src.storage.config_manager import ConfigManager
    from src.storage.data_manager import DataManager
    from src.analysis.fatigue_analyzer import FatigueAnalyzer  
    from src.ml.ml_predictor import MLPredictor
    from src.ml.psychometric_loader import PsychometricLoader
    print("[PASS] All core modules imported successfully")
    results["passed"].append("Core Imports")
except Exception as e:
    print(f"[FAIL] Import error: {e}")
    results["failed"].append(("Core Imports", str(e)))

# Test 2: ML Model Status
print("\nTEST 2: ML Model Status")
print("-"*70)
try:
    from src.ml.ml_predictor import MLPredictor
    predictor = MLPredictor()
    print(f"Model Initialized: {predictor._is_initialized}")
    print(f"Training Samples: {predictor._training_samples_count}")
    print("[PASS] ML model loaded successfully")
    results["passed"].append("ML Model")
except Exception as e:
    print(f"[FAIL] ML error: {e}")
    results["failed"].append(("ML Model", str(e)))

# Test 3: Psychometric Integration
print("\nTEST 3: Psychometric Dataset Support")
print("-"*70)
try:
    from src.ml.psychometric_loader import PsychometricLoader
    loader = PsychometricLoader()
    dataset = loader.load_dataset('data/psychometric_datasets/sample_nasatlx_workload.csv')
    print(f"Dataset: {dataset.organization} - {dataset.assessment_type}")
    print(f"Samples: {len(dataset.data)}")
    print("[PASS] Psychometric integration working")
    results["passed"].append("Psychometric Integration")  
except Exception as e:
    print(f"[FAIL] Psychometric error: {e}")
    results["failed"].append(("Psychometric Integration", str(e)))

# Test 4: Configuration
print("\nTEST 4: Configuration Management")
print("-"*70)
try:
    from src.storage.config_manager import ConfigManager
    config = ConfigManager()
    work_int = config.get('work_interval_minutes', 50)
    print(f"Work Interval: {work_int} minutes")
    print("[PASS] Configuration loaded")
    results["passed"].append("Configuration")
except Exception as e:
    print(f"[FAIL] Config error: {e}")
    results["failed"].append(("Configuration", str(e)))

# Test 5: Fatigue Calculation
print("\nTEST 5: Fatigue Score Calculation")
print("-"*70)
try:
    from src.analysis.fatigue_analyzer import FatigueAnalyzer
    analyzer = FatigueAnalyzer(use_ml=True)
    analyzer.start_session()
    score = analyzer.calculate_score(
        work_duration_minutes=30.0,
        activity_rate=15.0,
        time_since_break_minutes=25.0,
        is_on_break=False,
        blink_rate=12.0
    )
    print(f"Fatigue Score: {score.score:.1f}")
    print(f"Fatigue Level: {score.get_level()}")
    print(f"Method: {score.factors.get('prediction_method', 'unknown')}")
    print("[PASS] Fatigue calculation working")
    results["passed"].append("Fatigue Calculation")
except Exception as e:
    print(f"[FAIL] Fatigue calc error: {e}")
    results["failed"].append(("Fatigue Calculation", str(e)))

# Test 6: File Structure
print("\nTEST 6: Critical Files & Directories")
print("-"*70)
critical = [
    "src/ml/", "src/analysis/", "src/monitoring/", "src/storage/", "src/ui/",
    "data/psychometric_datasets/", "models/", "README.md", "main.py"
]
missing = []
for path in critical:
    p = Path(path)
    exists = p.is_dir() if path.endswith('/') else p.is_file()
    if not exists:
        missing.append(path)
        
if missing:
    print(f"[WARN] Missing: {', '.join(missing)}")
    results["warnings"].append(f"Missing files: {missing}")
else:
    print("[PASS] All critical files present")
    results["passed"].append("File Structure")

# Test 7: Documentation
print("\nTEST 7: Documentation")
print("-"*70)
docs = ["README.md", "ML_MODULE_README.md", "PSYCHOMETRIC_DATASETS.md"]
missing_docs = [d for d in docs if not Path(d).exists()]
if missing_docs:
    print(f"[WARN] Missing docs: {', '.join(missing_docs)}")
    results["warnings"].append(f"Missing docs: {missing_docs}")
else:
    print("[PASS] All key documentation present")
    results["passed"].append("Documentation")

# SUMMARY
print("\n" + "="*70)
print("  SUMMARY")
print("="*70)

passed_count = len(results["passed"])
failed_count = len(results["failed"])
warning_count = len(results["warnings"])

print(f"\nPassed Tests: {passed_count}")
for test in results["passed"]:
    print(f"  [PASS] {test}")

if results["failed"]:
    print(f"\nFailed Tests: {failed_count}")
    for test, error in results["failed"]:
        print(f"  [FAIL] {test}")
        print(f"         {error}")

if results["warnings"]:
    print(f"\nWarnings: {warning_count}")
    for warning in results["warnings"]:
        print(f"  [WARN] {warning}")

print("\n" + "="*70)

if failed_count == 0:
    print("STATUS: SYSTEM READY FOR PHASE 2")
    print("="*70 + "\n")
    sys.exit(0)
elif failed_count <= 2:
    print("STATUS: MINOR ISSUES - REVIEW RECOMMENDED")
    print("="*70 + "\n")
    sys.exit(1)
else:
    print("STATUS: CRITICAL ISSUES - FIX REQUIRED")
    print("="*70 + "\n")
    sys.exit(2)
