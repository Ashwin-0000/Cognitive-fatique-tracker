"""Preprocessing pipeline for psychometric datasets"""
import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Optional
from sklearn.preprocessing import StandardScaler
from src.ml.psychometric_loader import PsychometricDataset, PsychometricLoader
from src.utils.logger import default_logger as logger


class DatasetPreprocessor:
    """Preprocess psychometric data for ML training"""

    def __init__(self):
        self.scaler = StandardScaler()
        self.feature_dim = 35  # Updated from 28 to include psychometric features

    def preprocess_nasa_tlx(
        self,
        dataset: PsychometricDataset
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert NASA-TLX dataset to training samples.

        Creates synthetic activity features based on workload dimensions,
        then combines with psychometric features.

        Args:
            dataset: NASA-TLX psychometric dataset

        Returns:
            Tuple of (features, targets) as numpy arrays
        """
        loader = PsychometricLoader()
        df = loader.extract_nasa_tlx_features(dataset)

        features_list = []
        targets = df['fatigue_score'].values

        for idx, row in df.iterrows():
            # Synthesize activity features based on workload
            activity_features = self._synthesize_activity_from_nasa_tlx(row)

            # Extract psychometric features
            psychometric_features = self._extract_nasa_tlx_psychometric(row)

            # Combine (28 activity + 7 psychometric = 35 total)
            combined_features = np.concatenate([
                activity_features,
                psychometric_features
            ])

            features_list.append(combined_features)

        features = np.array(features_list)

        logger.info(f"Preprocessed NASA-TLX dataset: {features.shape}")
        return features, targets

    def preprocess_cfq(
        self,
        dataset: PsychometricDataset
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert CFQ dataset to training samples.

        Args:
            dataset: CFQ psychometric dataset

        Returns:
            Tuple of (features, targets) as numpy arrays
        """
        loader = PsychometricLoader()
        df = loader.extract_cfq_features(dataset)

        features_list = []
        targets = df['fatigue_score'].values

        for idx, row in df.iterrows():
            # Synthesize activity features based on fatigue
            activity_features = self._synthesize_activity_from_cfq(row)

            # Extract psychometric features
            psychometric_features = self._extract_cfq_psychometric(row)

            # Combine
            combined_features = np.concatenate([
                activity_features,
                psychometric_features
            ])

            features_list.append(combined_features)

        features = np.array(features_list)

        logger.info(f"Preprocessed CFQ dataset: {features.shape}")
        return features, targets

    def _synthesize_activity_from_nasa_tlx(self, row: pd.Series) -> np.ndarray:
        """
        Generate plausible activity features from NASA-TLX dimensions.

        Mapping strategy:
        - Mental Demand → keyboard/mouse activity
        - Temporal Demand → session duration
        - Effort → activity consistency
        - Performance → activity decline
        - Physical Demand → mouse movement

        Returns 28-element feature vector matching real-time activity features
        """
        # Extract NASA-TLX values (0-100 scale)
        mental = row['mental_demand'] / 100.0
        physical = row['physical_demand'] / 100.0
        temporal = row['temporal_demand'] / 100.0
        performance = row['performance'] / 100.0  # Higher = better
        effort = row['effort'] / 100.0
        frustration = row['frustration'] / 100.0

        # Activity Features (8)
        # Higher mental demand → higher activity rate
        activity_rate_1min = 10 + mental * 20  # 10-30 events/min
        activity_rate_5min = activity_rate_1min * \
            (0.9 + np.random.uniform(-0.1, 0.1))
        activity_rate_15min = activity_rate_5min * \
            (0.85 + np.random.uniform(-0.1, 0.1))

        keyboard_rate = mental * 15  # Mental work → typing
        mouse_rate = (mental * 0.5 + physical * 0.5) * 10  # Both types

        # Higher variance with frustration
        activity_variance = frustration * 5

        # Activity trend: poor performance → declining
        activity_trend = -1.0 * (1.0 - performance) * 0.5

        # Decline ratio based on effort and performance
        activity_decline_ratio = (effort * 0.7 - performance * 0.3)

        # Eye Tracking Features (6)
        # Higher mental/temporal demand → lower blink rate (eye strain)
        blink_rate = 15 - (mental + temporal) * 7  # 8-15 blinks/min
        blink_rate = max(5, min(20, blink_rate))

        blink_rate_5min_avg = blink_rate * \
            (0.95 + np.random.uniform(-0.05, 0.05))
        blink_rate_variance = frustration * 2
        blink_rate_trend = -(mental + temporal) * 0.3

        # Eye strain from high workload
        eye_strain_level = (mental + temporal + effort) / 3.0 * 25  # 0-25
        blink_decline_ratio = (mental + temporal) / 2.0 * 0.5

        # Temporal Features (6)
        # Use current time or default
        hour = 14  # Default afternoon
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        day_of_week = 2  # Default mid-week
        is_weekend = 0
        time_of_day_category = 1  # Afternoon

        # Session elapsed based on temporal demand
        session_elapsed_normalized = temporal * 0.8

        # Session Features (3)
        # Higher temporal demand → longer session
        session_duration_minutes = 30 + temporal * 90  # 30-120 min

        # Time since break based on effort
        time_since_break_minutes = effort * 60  # 0-60 min

        # Break frequency inversely related to temporal demand
        break_frequency = (1.0 - temporal) * 5

        # Historical Features (5) - defaults for new data
        fatigue_5min_ago = 0
        fatigue_15min_ago = 0
        fatigue_avg_1hour = 0
        fatigue_trend = 0
        fatigue_variance = 0

        # Combine all 28 features
        features = np.array([
            # Activity (8)
            activity_rate_1min, activity_rate_5min, activity_rate_15min,
            keyboard_rate, mouse_rate, activity_variance,
            activity_trend, activity_decline_ratio,

            # Eye Tracking (6)
            blink_rate, blink_rate_5min_avg, blink_rate_variance,
            blink_rate_trend, eye_strain_level, blink_decline_ratio,

            # Temporal (6)
            hour_sin, hour_cos, day_of_week, is_weekend,
            time_of_day_category, session_elapsed_normalized,

            # Session (3)
            session_duration_minutes, time_since_break_minutes, break_frequency,

            # Historical (5)
            fatigue_5min_ago, fatigue_15min_ago, fatigue_avg_1hour,
            fatigue_trend, fatigue_variance
        ])

        return features

    def _synthesize_activity_from_cfq(self, row: pd.Series) -> np.ndarray:
        """
        Generate plausible activity features from CFQ scores.

        Uses fatigue scores to estimate activity patterns.
        Higher fatigue → lower activity, lower blink rate, etc.
        """
        # Normalize fatigue to 0-1
        fatigue_norm = row['cfq_normalized'] / 100.0

        physical_fatigue = row['physical_fatigue']
        psychological_fatigue = row['psychological_fatigue']

        # Activity Features (8)
        # Higher fatigue → lower activity
        activity_rate_1min = 25 - fatigue_norm * 15  # 10-25
        activity_rate_5min = activity_rate_1min * 0.95
        activity_rate_15min = activity_rate_5min * 0.9

        keyboard_rate = (1.0 - psychological_fatigue / 12.0) * 15
        mouse_rate = (1.0 - physical_fatigue / 21.0) * 10

        activity_variance = fatigue_norm * 3
        activity_trend = -fatigue_norm * 0.5
        activity_decline_ratio = fatigue_norm * 0.7

        # Eye Tracking (6)
        blink_rate = 15 - psychological_fatigue / 12.0 * 7
        blink_rate = max(5, min(20, blink_rate))

        blink_rate_5min_avg = blink_rate * 0.98
        blink_rate_variance = fatigue_norm * 2
        blink_rate_trend = -fatigue_norm * 0.3
        eye_strain_level = psychological_fatigue / 12.0 * 25
        blink_decline_ratio = fatigue_norm * 0.5

        # Temporal (6) - defaults
        hour_sin = 0.0
        hour_cos = 1.0
        day_of_week = 2
        is_weekend = 0
        time_of_day_category = 1
        session_elapsed_normalized = fatigue_norm * 0.8

        # Session (3)
        session_duration_minutes = 60 + fatigue_norm * 60
        time_since_break_minutes = fatigue_norm * 50
        break_frequency = (1.0 - fatigue_norm) * 4

        # Historical (5) - defaults
        fatigue_5min_ago = 0
        fatigue_15min_ago = 0
        fatigue_avg_1hour = 0
        fatigue_trend = 0
        fatigue_variance = 0

        features = np.array([
            # Activity (8)
            activity_rate_1min, activity_rate_5min, activity_rate_15min,
            keyboard_rate, mouse_rate, activity_variance,
            activity_trend, activity_decline_ratio,

            # Eye Tracking (6)
            blink_rate, blink_rate_5min_avg, blink_rate_variance,
            blink_rate_trend, eye_strain_level, blink_decline_ratio,

            # Temporal (6)
            hour_sin, hour_cos, day_of_week, is_weekend,
            time_of_day_category, session_elapsed_normalized,

            # Session (3)
            session_duration_minutes, time_since_break_minutes, break_frequency,

            # Historical (5)
            fatigue_5min_ago, fatigue_15min_ago, fatigue_avg_1hour,
            fatigue_trend, fatigue_variance
        ])

        return features

    def _extract_nasa_tlx_psychometric(self, row: pd.Series) -> np.ndarray:
        """Extract 7 psychometric features from NASA-TLX"""
        return np.array([
            row['mental_demand'],
            row['physical_demand'],
            row['temporal_demand'],
            row['performance'],
            row['effort'],
            row['frustration'],
            row['nasa_tlx_workload']
        ])

    def _extract_cfq_psychometric(self, row: pd.Series) -> np.ndarray:
        """Extract 7 psychometric features from CFQ (padded to match dimension)"""
        # Use same 7 slots but fill first 3 with CFQ data
        return np.array([
            row['physical_fatigue'] * 100 / 21,  # Normalize to 0-100
            row['psychological_fatigue'] * 100 / 12,  # Normalize to 0-100
            row['cfq_normalized'],
            row['fatigue_ratio'] * 10,  # Scale ratio
            0,  # Padding
            0,  # Padding
            row['cfq_normalized']  # Overall score
        ])

    def balance_dataset(
        self,
        features: np.ndarray,
        targets: np.ndarray,
        bins: int = 5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Balance dataset by fatigue score bins.

        Args:
            features: Feature array
            targets: Target fatigue scores
            bins: Number of bins for balancing

        Returns:
            Balanced (features, targets)
        """
        # Create bins
        bin_edges = np.linspace(0, 100, bins + 1)
        bin_indices = np.digitize(targets, bin_edges)

        # Find minimum bin size
        bin_counts = np.bincount(bin_indices, minlength=bins + 2)
        min_count = min(bin_counts[1:-1])  # Exclude edge bins

        if min_count == 0:
            logger.warning("Some fatigue bins are empty, skipping balancing")
            return features, targets

        # Sample equally from each bin
        balanced_indices = []
        for bin_idx in range(1, bins + 1):
            bin_mask = bin_indices == bin_idx
            bin_idx_array = np.where(bin_mask)[0]

            if len(bin_idx_array) > 0:
                sampled = np.random.choice(
                    bin_idx_array,
                    size=min(min_count, len(bin_idx_array)),
                    replace=False
                )
                balanced_indices.extend(sampled)

        balanced_features = features[balanced_indices]
        balanced_targets = targets[balanced_indices]

        logger.info(
            f"Balanced dataset: {len(features)} → {len(balanced_features)} samples")

        return balanced_features, balanced_targets

    def add_noise(
        self,
        features: np.ndarray,
        noise_level: float = 0.05
    ) -> np.ndarray:
        """
        Add Gaussian noise to features for data augmentation.

        Args:
            features: Feature array
            noise_level: Standard deviation of noise relative to feature values

        Returns:
            Noisy features
        """
        noise = np.random.normal(0, noise_level, features.shape)
        noisy_features = features + noise * np.abs(features)

        return noisy_features
