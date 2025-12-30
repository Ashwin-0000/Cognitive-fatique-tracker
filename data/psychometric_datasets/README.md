# Psychometric Datasets

This directory contains psychometric assessment datasets for training the ML-based fatigue prediction model.

## Dataset Naming Convention

CSV files follow this naming pattern:
```
<organization>_<assessment>_<features>.csv
```

**Examples:**
- `cogbeacon_nasatlx_multimodal.csv` - CogBeacon dataset with NASA-TLX scores
- `mimbcd_nasatlx_clinical.csv` - UTA4/MIMBCD clinical workload data
-`mefar_cfq_occupational.csv` - MEFAR occupational fatigue data
- `sample_nasatlx_workload.csv` - Sample NASA-TLX demonstration data
- `sample_cfq_fatigue.csv` - Sample CFQ demonstration data

## Supported Assessments

### NASA Task Load Index (NASA-TLX)

**Required Columns:**
- `participant_id` - Unique participant identifier
- `timestamp` - Timestamp of assessment (YYYY-MM-DD HH:MM:SS)
- `mental_demand` - Mental demand (0-100)
- `physical_demand` - Physical demand (0-100)
- `temporal_demand` - Temporal demand (0-100)
- `performance` - Performance (0-100, higher = better)
- `effort` - Effort (0-100)
- `frustration` - Frustration (0-100)
- `fatigue_score` - Ground truth fatigue score (0-100)

**CSV Format:**
```csv
participant_id,timestamp,mental_demand,physical_demand,temporal_demand,performance,effort,frustration,fatigue_score
P001,2024-12-14 10:30:00,75,30,60,80,70,40,65
```

### Chalder Fatigue Questionnaire (CFQ)

**Required Columns:**
- `participant_id` - Unique participant identifier
- `timestamp` - Timestamp of assessment
- `physical_fatigue` - Physical fatigue subscore (0-21 Likert or 0-7 bimodal)
- `psychological_fatigue` - Psychological fatigue subscore (0-12 Likert or 0-4 bimodal)
- `total_score` - Total CFQ score (0-33 Likert or 0-11 bimodal)
- `fatigue_score` - Normalized fatigue score (0-100)

**CSV Format:**
```csv
participant_id,timestamp,physical_fatigue,psychological_fatigue,total_score,fatigue_score
P001,2024-12-14 10:30:00,18,10,28,75
```

## Usage

### Loading a Dataset

```python
from src.ml.psychometric_loader import PsychometricLoader

loader = PsychometricLoader()
dataset = loader.load_dataset('data/psychometric_datasets/sample_nasatlx_workload.csv')

print(f"Organization: {dataset.organization}")
print(f"Assessment: {dataset.assessment_type}")
print(f"Samples: {len(dataset.data)}")
```

### Training Model

```python
from src.ml.ml_predictor import MLPredictor

predictor = MLPredictor()
stats = predictor.train_from_psychometric_dataset(
    'data/psychometric_datasets/sample_nasatlx_workload.csv'
)

print(f"Training complete: {stats['sample_count']} samples")
```

### Through FatigueAnalyzer

```python
from src.analysis.fatigue_analyzer import FatigueAnalyzer

analyzer = FatigueAnalyzer(use_ml=True)
analyzer.train_from_psychometric_file(
    'data/psychometric_datasets/sample_nasatlx_workload.csv'
)
```

## Public Dataset Sources

### CogBeacon
- **Source**: GitHub - Multi-modal cognitive fatigue dataset
- **Content**: 76 cognitive tasks, 19 participants
- **Link**: https://github.com/CogBeacon
- **Features**: Physiological, behavioral, performance + fatigue reports

### UTA4/MIMBCD-UI
- **Source**: Kaggle, figshare
- **Content**: NASA-TLX workload from 31 clinicians
- **Link**: https://www.kaggle.com/datasets/mimbcd-ui/uta4-nasa-tlx
- **Features**: Clinical workload assessments

### MEFAR
- **Source**: NIH - Occupational mental fatigue dataset
- **Content**: 23 participants during professional work
- **Link**: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9318822/
- **Features**: Physiological signals + Chalder Fatigue Scale

## Creating Custom Datasets

1. **Prepare your data** in CSV format following the required columns
2. **Name the file** using the naming convention: `<org>_<assessment>_<features>.csv`
3. **Place the file** in this directory
4. **Load and train** using the code examples above

## Data Privacy

- All data must be anonymized (use participant IDs, not names)
- No personally identifiable information (PII) in CSV files
- Data stays local - no external API calls
- Complies with HIPAA/GDPR requirements for research data

## Example Data

This directory includes sample datasets for demonstration:
- `sample_nasatlx_workload.csv` - 15 samples across 3 participants
- `sample_cfq_fatigue.csv` - 12 samples across 3 participants

These can be used for testing the training pipeline.
