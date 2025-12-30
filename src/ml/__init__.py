"""
Machine Learning module for cognitive fatigue prediction with incremental learning.

This module provides:
- Incremental/online learning for adaptive predictions
- Feature engineering from activity and eye tracking data
- Personalized models that adapt to individual users
- Ensemble prediction methods for robust results
- Psychometric dataset loading and preprocessing (NASA-TLX, CFQ)
"""

from .ml_predictor import MLPredictor
from .feature_engineering import FeatureEngineer
from .personalization import PersonalizationEngine
from .model_manager import ModelManager
from .psychometric_loader import PsychometricLoader, PsychometricDataset
from .dataset_preprocessor import DatasetPreprocessor

__all__ = [
    'MLPredictor',
    'FeatureEngineer',
    'PersonalizationEngine',
    'ModelManager',
    'PsychometricLoader',
    'PsychometricDataset',
    'DatasetPreprocessor'
]
