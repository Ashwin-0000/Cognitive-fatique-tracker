"""Psychometric dataset loader for NASA-TLX and CFQ assessments"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from src.utils.logger import default_logger as logger


class PsychometricDataset:
    """Container for loaded psychometric data"""

    def __init__(
        self,
        data: pd.DataFrame,
        organization: str,
        assessment_type: str,
        features_description: str
    ):
        self.data = data
        self.organization = organization
        self.assessment_type = assessment_type
        self.features_description = features_description
        self.loaded_at = datetime.now()

    def __repr__(self):
        return (
            f"PsychometricDataset(org={self.organization}, "
            f"type={self.assessment_type}, samples={len(self.data)})"
        )


class PsychometricLoader:
    """Load and parse psychometric assessment datasets from CSV files"""

    # Expected column names for different assessment types
    NASA_TLX_COLUMNS = [
        'mental_demand', 'physical_demand', 'temporal_demand',
        'performance', 'effort', 'frustration'
    ]

    CFQ_COLUMNS = ['physical_fatigue', 'psychological_fatigue', 'total_score']

    REQUIRED_BASE_COLUMNS = ['participant_id', 'fatigue_score']

    def __init__(self):
        self.loaded_datasets: List[PsychometricDataset] = []

    def load_dataset(self, filepath: str) -> PsychometricDataset:
        """
        Load psychometric dataset from CSV file.

        Filename format: <organization>_<assessment>_<features>.csv
        Example: cogbeacon_nasatlx_multimodal.csv

        Args:
            filepath: Path to CSV file

        Returns:
            PsychometricDataset object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Dataset file not found: {filepath}")

        # Parse filename to extract metadata
        organization, assessment, features = self._parse_filename(
            filepath.stem)

        logger.info(
            f"Loading {assessment.upper()} dataset from {organization}")

        # Load CSV
        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            raise ValueError(f"Failed to read CSV file: {e}")

        # Validate and process based on assessment type
        if assessment.lower() in ['nasatlx', 'nasa-tlx', 'tlx']:
            df = self._validate_nasa_tlx(df)
        elif assessment.lower() in ['cfq', 'chalder']:
            df = self._validate_cfq(df)
        else:
            raise ValueError(
                f"Unknown assessment type: {assessment}. "
                "Supported: nasatlx, cfq"
            )

        dataset = PsychometricDataset(
            data=df,
            organization=organization,
            assessment_type=assessment,
            features_description=features
        )

        self.loaded_datasets.append(dataset)
        logger.info(f"Loaded {len(df)} samples from {filepath.name}")

        return dataset

    def _parse_filename(self, filename: str) -> Tuple[str, str, str]:
        """
        Parse filename to extract organization, assessment, and features.

        Format: <organization>_<assessment>_<features>

        Args:
            filename: Filename without extension

        Returns:
            Tuple of (organization, assessment, features)
        """
        parts = filename.split('_')

        if len(parts) < 3:
            raise ValueError(
                f"Invalid filename format: {filename}. "
                "Expected: <organization>_<assessment>_<features>"
            )

        organization = parts[0]
        assessment = parts[1]
        features = '_'.join(parts[2:])  # Join remaining parts

        return organization, assessment, features

    def _validate_nasa_tlx(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate NASA-TLX dataset format"""

        # Check required columns
        missing_cols = []
        for col in self.REQUIRED_BASE_COLUMNS:
            if col not in df.columns:
                missing_cols.append(col)

        for col in self.NASA_TLX_COLUMNS:
            if col not in df.columns:
                missing_cols.append(col)

        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}. "
                f"NASA-TLX requires: {self.REQUIRED_BASE_COLUMNS + self.NASA_TLX_COLUMNS}")

        # Validate score ranges (0-100 for NASA-TLX)
        for col in self.NASA_TLX_COLUMNS:
            if df[col].min() < 0 or df[col].max() > 100:
                logger.warning(f"Column {col} has values outside 0-100 range")

        # Validate fatigue_score (0-100)
        if df['fatigue_score'].min() < 0 or df['fatigue_score'].max() > 100:
            logger.warning("fatigue_score has values outside 0-100 range")

        # Convert timestamp if present
        if 'timestamp' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            except Exception as e:
                logger.warning(f"Failed to parse timestamp column: {e}")

        logger.info("NASA-TLX dataset validation passed")
        return df

    def _validate_cfq(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate CFQ dataset format"""

        # Check required columns
        missing_cols = []
        for col in self.REQUIRED_BASE_COLUMNS:
            if col not in df.columns:
                missing_cols.append(col)

        for col in self.CFQ_COLUMNS:
            if col not in df.columns:
                missing_cols.append(col)

        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}. "
                f"CFQ requires: {self.REQUIRED_BASE_COLUMNS + self.CFQ_COLUMNS}")

        # Validate score ranges
        # Physical fatigue: 0-21 (Likert) or 0-7 (bimodal)
        if df['physical_fatigue'].max() <= 7:
            logger.info("Detected bimodal scoring for physical_fatigue")
        elif df['physical_fatigue'].max() <= 21:
            logger.info("Detected Likert scoring for physical_fatigue")
        else:
            logger.warning("physical_fatigue has unexpected range")

        # Psychological fatigue: 0-12 (Likert) or 0-4 (bimodal)
        if df['psychological_fatigue'].max() <= 4:
            logger.info("Detected bimodal scoring for psychological_fatigue")
        elif df['psychological_fatigue'].max() <= 12:
            logger.info("Detected Likert scoring for psychological_fatigue")
        else:
            logger.warning("psychological_fatigue has unexpected range")

        # Validate fatigue_score (0-100)
        if df['fatigue_score'].min() < 0 or df['fatigue_score'].max() > 100:
            logger.warning("fatigue_score has values outside 0-100 range")

        # Convert timestamp if present
        if 'timestamp' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            except Exception as e:
                logger.warning(f"Failed to parse timestamp column: {e}")

        logger.info("CFQ dataset validation passed")
        return df

    def extract_nasa_tlx_features(
            self, dataset: PsychometricDataset) -> pd.DataFrame:
        """
        Extract NASA-TLX features from dataset.

        Args:
            dataset: Loaded psychometric dataset

        Returns:
            DataFrame with NASA-TLX features
        """
        if 'nasatlx' not in dataset.assessment_type.lower():
            raise ValueError("Dataset is not NASA-TLX")

        df = dataset.data.copy()

        # Calculate derived features
        # Weighted workload score (average of 6 dimensions)
        df['nasa_tlx_workload'] = df[self.NASA_TLX_COLUMNS].mean(axis=1)

        # Frustration-Effort ratio (indicator of task difficulty)
        df['frustration_effort_ratio'] = df['frustration'] / \
            (df['effort'] + 1e-6)

        # Cognitive load index (mental + temporal + effort)
        df['cognitive_load_index'] = (
            df['mental_demand'] + df['temporal_demand'] + df['effort']
        ) / 3.0

        # Physical strain index
        df['physical_strain_index'] = (
            df['physical_demand'] + df['effort']
        ) / 2.0

        logger.info(f"Extracted NASA-TLX features: {len(df)} samples")
        return df

    def extract_cfq_features(
            self,
            dataset: PsychometricDataset) -> pd.DataFrame:
        """
        Extract CFQ features from dataset.

        Args:
            dataset: Loaded psychometric dataset

        Returns:
            DataFrame with CFQ features
        """
        if 'cfq' not in dataset.assessment_type.lower():
            raise ValueError("Dataset is not CFQ")

        df = dataset.data.copy()

        # Calculate derived features
        # Physical vs psychological fatigue ratio
        df['fatigue_ratio'] = df['physical_fatigue'] / \
            (df['psychological_fatigue'] + 1e-6)

        # Normalize scores to 0-100 scale
        # Detect scoring method
        if df['total_score'].max() <= 11:
            # Bimodal scoring (0-11)
            df['cfq_normalized'] = (df['total_score'] / 11.0) * 100
        else:
            # Likert scoring (0-33)
            df['cfq_normalized'] = (df['total_score'] / 33.0) * 100

        logger.info(f"Extracted CFQ features: {len(df)} samples")
        return df

    def merge_datasets(
            self,
            datasets: List[PsychometricDataset]) -> pd.DataFrame:
        """
        Merge multiple datasets into single DataFrame.

        Args:
            datasets: List of psychometric datasets

        Returns:
            Merged DataFrame with source tracking
        """
        merged_frames = []

        for dataset in datasets:
            df = dataset.data.copy()
            df['source_organization'] = dataset.organization
            df['source_assessment'] = dataset.assessment_type
            merged_frames.append(df)

        merged = pd.concat(merged_frames, ignore_index=True)
        logger.info(
            f"Merged {len(datasets)} datasets: {len(merged)} total samples")

        return merged

    def get_statistics(self, dataset: PsychometricDataset) -> Dict:
        """Get dataset statistics"""
        df = dataset.data

        stats = {
            'organization': dataset.organization,
            'assessment_type': dataset.assessment_type,
            'sample_count': len(df),
            'participant_count': df['participant_id'].nunique() if 'participant_id' in df.columns else 0,
            'fatigue_score': {
                'mean': float(
                    df['fatigue_score'].mean()),
                'std': float(
                    df['fatigue_score'].std()),
                'min': float(
                    df['fatigue_score'].min()),
                'max': float(
                    df['fatigue_score'].max())}}

        # Add assessment-specific stats
        if 'nasatlx' in dataset.assessment_type.lower():
            stats['nasa_tlx'] = {
                col: {
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std())
                }
                for col in self.NASA_TLX_COLUMNS
            }
        elif 'cfq' in dataset.assessment_type.lower():
            stats['cfq'] = {
                col: {
                    'mean': float(df[col].mean()),
                    'std': float(df[col].std())
                }
                for col in self.CFQ_COLUMNS
            }

        return stats
