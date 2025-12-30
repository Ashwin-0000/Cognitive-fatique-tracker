# 📍 ML Model & Training Data Locations

## Quick Reference Guide

### 🤖 Trained Model Files

**Main Directory:** `d:\code3\cognitive_fatigue_tracker\models\`

#### Primary Model
```
models/current_model.pkl
```
- **Size:** 2,809 bytes (2.8 KB)
- **Contains:**
  - Trained SGDRegressor
  - Trained PassiveAggressiveRegressor
  - StandardScaler (feature normalization)
  - Model weights
  - Training configuration
- **Status:** ✅ Trained with 300+ samples
- **Personalization:** 85% ML weight

#### Model Metadata
```
models/metadata.json
```
- **Size:** 4,971 bytes (5.0 KB)
- **Contains:**
  - 23 version history entries
  - Performance metrics per version
  - Timestamps and file paths
  - Created: 2025-12-11 12:01:16
  - Last updated: 2025-12-11 12:02:47

#### Model Backups (Last 5)
```
models/backups/
├── model_v19_20251211_120244.pkl
├── model_v20_20251211_120245.pkl
├── model_v21_20251211_120246.pkl
├── model_v22_20251211_120247.pkl
└── model_v23_20251211_120247.pkl  ← Latest
```

---

### 👤 User Profile & Training Data

**Main Directory:** `d:\code3\cognitive_fatigue_tracker\data\`

#### User Personalization Profile
```
data/profiles/user_profile.json
```
- **Size:** 902 bytes
- **Contains:**
  - Total sessions: 76
  - Adaptive thresholds:
    - Low: 32.0
    - Moderate: 62.0
    - High: 82.0
  - Hourly productivity patterns (9AM-4PM)
  - Fatigue progression patterns (8 time bins)
  - Feedback history
- **Created:** 2025-12-11 11:44:59
- **Last updated:** 2025-12-11 12:02:47

#### Application Database
```
data/fatigue_tracker.db
```
- **Type:** SQLite database
- **Contains:**
  - Session history
  - Activity events
  - Fatigue scores
  - Historical data for analysis

---

### 📊 Training Data Generator

**Script:** `generate_training_data.py`

**What it generated:**
- 25 synthetic work sessions
- ~300 feature vectors (28 features each)
- Ground truth fatigue scores
- Realistic patterns:
  - Morning productivity
  - Afternoon slump
  - Fatigue buildup over time
  - Activity decline patterns
  - Blink rate reduction

**Generated patterns stored in:**
- Model weights (current_model.pkl)
- Personalization profile (user_profile.json)
- Model metadata (metadata.json)

---

### 🔍 How to View the Data

#### View Model Metadata
```python
import json
with open('models/metadata.json', 'r') as f:
    metadata = json.load(f)
    print(f"Versions: {len(metadata['versions'])}")
    print(f"Latest: {metadata['current_version']}")
```

#### View User Profile
```python
import json
with open('data/profiles/user_profile.json', 'r') as f:
    profile = json.load(f)
    print(f"Sessions: {profile['total_sessions']}")
    print(f"Thresholds: {profile['thresholds']}")
```

#### Load Trained Model
```python
import joblib
model_state = joblib.load('models/current_model.pkl')
print(f"Models: {model_state['models'].keys()}")
print(f"Training samples: {model_state['training_samples_count']}")
```

---

### 📦 File Sizes Summary

| File | Size | Purpose |
|------|------|---------|
| current_model.pkl | 2.8 KB | Main trained model |
| metadata.json | 5.0 KB | Version history |
| user_profile.json | 902 bytes | Personalization |
| Backup models (5×) | ~2.8 KB each | Safety backups |
| **Total ML files** | **~20 KB** | Complete ML system |

---

### 🚀 Using the Trained Model

The model loads automatically when you run the app:

```bash
python main.py
```

**What happens:**
1. `FatigueAnalyzer` initializes with `use_ml=True`
2. `MLPredictor` loads `models/current_model.pkl`
3. `PersonalizationEngine` loads `data/profiles/user_profile.json`
4. App starts with 85% ML predictions enabled
5. Continues learning from your real sessions

**Dependencies required:**
```bash
pip install scikit-learn>=1.3.0 joblib>=1.3.0 numpy>=1.24.0
```

✅ **Already installed in `venv311`!**

---

### 🔄 Model Updates

**Automatic saves occur:**
- Every 50 training samples
- After full retrain (every 100 samples)
- When you call `analyzer.train_ml_model()`

**Backups created:**
- Before each model save
- Last 5 versions retained
- Older backups automatically deleted

**To reset model:**
```python
from src.analysis.fatigue_analyzer import FatigueAnalyzer
analyzer = FatigueAnalyzer(use_ml=True)
analyzer.reset_ml_model()
```

---

### 📍 Full Path Reference

**Windows paths:**
```
D:\code3\cognitive_fatigue_tracker\models\current_model.pkl
D:\code3\cognitive_fatigue_tracker\models\metadata.json
D:\code3\cognitive_fatigue_tracker\models\backups\
D:\code3\cognitive_fatigue_tracker\data\profiles\user_profile.json
D:\code3\cognitive_fatigue_tracker\data\fatigue_tracker.db
```

**Python access:**
```python
from pathlib import Path

# Model directory
models_dir = Path(__file__).parent / "models"
model_file = models_dir / "current_model.pkl"
metadata_file = models_dir / "metadata.json"

# Data directory  
data_dir = Path(__file__).parent / "data"
profile_file = data_dir / "profiles" / "user_profile.json"
db_file = data_dir / "fatigue_tracker.db"
```

---

### ✅ Verification Checklist

- ✅ Model file exists: `models/current_model.pkl`
- ✅ Metadata exists: `models/metadata.json`
- ✅ Profile exists: `data/profiles/user_profile.json`
- ✅ Backups created: `models/backups/` (5 files)
- ✅ Dependencies installed: scikit-learn, joblib, numpy
- ✅ Model loaded successfully in app
- ✅ Ready for production use

---

**🎉 Everything is in place and ready to use!**
