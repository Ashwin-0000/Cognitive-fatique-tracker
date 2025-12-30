"""ML-based fatigue predictor with incremental learning"""
import numpy as np
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from sklearn.linear_model import SGDRegressor, PassiveAggressiveRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

from src.ml.feature_engineering import FeatureEngineer
from src.ml.model_manager import ModelManager
from src.ml.personalization import PersonalizationEngine
from src.utils.logger import default_logger as logger


class MLPredictor:
    """
    ML-based predictor with incremental learning for fatigue estimation.
    
    Uses ensemble of online learning models that adapt to user patterns.
    """
    
    def __init__(
        self,
        feature_engineer: Optional[FeatureEngineer] = None,
        model_manager: Optional[ModelManager] = None,
        personalization: Optional[PersonalizationEngine] = None
    ):
        """
        Initialize ML predictor.
        
        Args:
            feature_engineer: Feature engineering instance
            model_manager: Model management instance
            personalization: Personalization engine instance
        """
        self.feature_engineer = feature_engineer or FeatureEngineer()
        self.model_manager = model_manager or ModelManager()
        self.personalization = personalization or PersonalizationEngine()
        
        # Ensemble of incremental learners
        self.models = {
            'sgd': SGDRegressor(
                loss='squared_error',
                penalty='l2',
                alpha=0.0001,
                learning_rate='invscaling',
                eta0=0.01,
                power_t=0.25,
                random_state=42
            ),
            'passive_aggressive': PassiveAggressiveRegressor(
                C=1.0,
                epsilon=0.1,
                random_state=42
            )
        }
        
        # Feature scaler for normalization
        self.scaler = StandardScaler()
        
        # Model weights (updated based on performance)
        self.model_weights = {
            'sgd': 0.5,
            'passive_aggressive': 0.5
        }
        
        # Training buffer
        self.training_buffer: List[Tuple[np.ndarray, float]] = []
        self.max_buffer_size = 1000
        
        # Performance tracking
        self.prediction_errors: List[float] = []
        self.max_error_history = 100
        
        # State
        self._is_initialized = False
        self._training_samples_count = 0
        self._last_retrain_count = 0
        
        # Load saved model if exists
        self._load_model()
    
    def predict(self, features: np.ndarray, use_ensemble: bool = True) -> Tuple[float, float]:
        """
        Predict fatigue score from features.
        
        Args:
            features: Feature vector
            use_ensemble: Whether to use ensemble prediction
        
        Returns:
            Tuple of (predicted_score, confidence)
        """
        if not self._is_initialized:
            logger.debug("Model not initialized, returning neutral prediction")
            return 50.0, 0.0  # Neutral score with zero confidence
        
        try:
            # Scale features
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            if use_ensemble:
                # Ensemble prediction
                predictions = []
                weights = []
                
                for name, model in self.models.items():
                    try:
                        pred = model.predict(features_scaled)[0]
                        predictions.append(pred)
                        weights.append(self.model_weights[name])
                    except Exception as e:
                        logger.warning(f"Model {name} prediction failed: {e}")
                
                if not predictions:
                    return 50.0, 0.0
                
                # Weighted average
                weights_array = np.array(weights)
                weights_normalized = weights_array / weights_array.sum()
                predicted_score = np.average(predictions, weights=weights_normalized)
                
                # Confidence based on agreement between models
                if len(predictions) > 1:
                    std = np.std(predictions)
                    # Low std = high confidence
                    confidence = max(0.0, 1.0 - (std / 50.0))
                else:
                    confidence = 0.5
                
            else:
                # Single model prediction (SGD)
                predicted_score = self.models['sgd'].predict(features_scaled)[0]
                confidence = 0.5
            
            # Clamp to valid range
            predicted_score = max(0.0, min(100.0, predicted_score))
            
            # Adjust confidence based on training data
            data_confidence = min(self._training_samples_count / 100.0, 1.0)
            confidence = confidence * data_confidence
            
            logger.debug(f"ML prediction: {predicted_score:.1f} (confidence: {confidence:.2f})")
            
            return predicted_score, confidence
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return 50.0, 0.0
    
    def partial_fit(self, features: np.ndarray, target: float):
        """
        Incrementally update model with new sample.
        
        Args:
            features: Feature vector
            target: True fatigue score
        """
        try:
            # Add to training buffer
            self.training_buffer.append((features.copy(), target))
            if len(self.training_buffer) > self.max_buffer_size:
                self.training_buffer.pop(0)
            
            self._training_samples_count += 1
            
            # Initialize scaler and models if needed
            if not self._is_initialized:
                if len(self.training_buffer) >= 10:
                    self._initialize_models()
                else:
                    logger.debug(f"Buffering samples: {len(self.training_buffer)}/10")
                    return
            
            # Scale features
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            
            # Update each model
            for name, model in self.models.items():
                try:
                    model.partial_fit(features_scaled, [target])
                except Exception as e:
                    logger.warning(f"Model {name} update failed: {e}")
            
            # Periodic weight adjustment
            if self._training_samples_count % 20 == 0:
                self._update_model_weights()
            
            # Periodic full retrain
            if self._training_samples_count - self._last_retrain_count >= 100:
                self._full_retrain()
            
            logger.debug(f"Incremental update complete (sample #{self._training_samples_count})")
            
        except Exception as e:
            logger.error(f"Partial fit error: {e}")
    
    def add_training_sample(
        self, 
        features: np.ndarray, 
        target: float,
        immediate_update: bool = False
    ):
        """
        Add training sample (optionally update immediately).
        
        Args:
            features: Feature vector
            target: True fatigue score
            immediate_update: Whether to update model immediately
        """
        if immediate_update:
            self.partial_fit(features, target)
        else:
            self.training_buffer.append((features.copy(), target))
            if len(self.training_buffer) > self.max_buffer_size:
                self.training_buffer.pop(0)
    
    def batch_train(
        self,
        features_list: List[np.ndarray],
        targets_list: List[float],
        dataset_source: str = "unknown"
    ):
        """
        Batch training from list of samples.
        
        More efficient than individual partial_fit calls for large datasets.
        
        Args:
            features_list: List of feature vectors
            targets_list: List of target fatigue scores
            dataset_source: Source identifier for tracking
        """
        if len(features_list) != len(targets_list):
            raise ValueError("Features and targets must have same length")
        
        logger.info(f"Batch training with {len(features_list)} samples from {dataset_source}")
        
        # Add all samples to buffer
        for features, target in zip(features_list, targets_list):
            self.training_buffer.append((features.copy(), target))
            self._training_samples_count += 1
        
        # Trim buffer if needed
        if len(self.training_buffer) > self.max_buffer_size:
            self.training_buffer = list(self.training_buffer[-self.max_buffer_size:])
        
        # Initialize if needed
        if not self._is_initialized and len(self.training_buffer) >= 10:
            self._initialize_models()
        
        # Perform full retrain with new data
        if self._is_initialized:
            self._full_retrain()
        
        logger.info(f"Batch training complete: {self._training_samples_count} total samples")
    
    def train_from_psychometric_dataset(self, dataset_path: str) -> Dict:
        """
        Train model from psychometric dataset CSV file.
        
        Args:
            dataset_path: Path to psychometric CSV file
        
        Returns:
            Training statistics dictionary
        """
        try:
            # Import here to avoid circular dependency
            from src.ml.psychometric_loader import PsychometricLoader
            from src.ml.dataset_preprocessor import DatasetPreprocessor
            
            # Load dataset
            loader = PsychometricLoader()
            dataset = loader.load_dataset(dataset_path)
            
            logger.info(f"Loaded {dataset.organization} {dataset.assessment_type} dataset")
            
            # Preprocess based on assessment type
            preprocessor = DatasetPreprocessor()
            
            if 'nasatlx' in dataset.assessment_type.lower():
                features, targets = preprocessor.preprocess_nasa_tlx(dataset)
            elif 'cfq' in dataset.assessment_type.lower():
                features, targets = preprocessor.preprocess_cfq(dataset)
            else:
                raise ValueError(f"Unsupported assessment type: {dataset.assessment_type}")
            
            # Convert to list
            features_list = [features[i] for i in range(len(features))]
            targets_list = list(targets)
            
            # Batch train
            source_id = f"{dataset.organization}_{dataset.assessment_type}"
            self.batch_train(features_list, targets_list, dataset_source=source_id)
            
            # Save model
            self.save_model()
            
            # Return statistics
            stats = loader.get_statistics(dataset)
            stats['training_complete'] = True
            stats['model_samples'] = self._training_samples_count
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to train from psychometric dataset: {e}")
            raise

    
    def record_prediction_error(self, predicted: float, actual: float):
        """
        Record prediction error for performance tracking.
        
        Args:
            predicted: Predicted fatigue score
            actual: Actual fatigue score
        """
        error = abs(predicted - actual)
        self.prediction_errors.append(error)
        
        if len(self.prediction_errors) > self.max_error_history:
            self.prediction_errors.pop(0)
        
        # Check if retraining is needed
        if len(self.prediction_errors) >= 20:
            recent_mae = np.mean(self.prediction_errors[-20:])
            if recent_mae > 15.0:  # High error threshold
                logger.warning(f"High prediction error detected (MAE: {recent_mae:.2f}), triggering retrain")
                self._full_retrain()
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get current model performance metrics"""
        if not self.prediction_errors:
            return {}
        
        return {
            'mae': np.mean(self.prediction_errors),
            'rmse': np.sqrt(np.mean([e**2 for e in self.prediction_errors])),
            'max_error': np.max(self.prediction_errors),
            'samples_count': self._training_samples_count,
            'is_initialized': self._is_initialized
        }
    
    def save_model(self):
        """Save current model state"""
        if not self._is_initialized:
            logger.warning("Cannot save uninitialized model")
            return
        
        model_state = {
            'models': self.models,
            'scaler': self.scaler,
            'model_weights': self.model_weights,
            'training_samples_count': self._training_samples_count,
            'is_initialized': self._is_initialized
        }
        
        metrics = self.get_performance_metrics()
        
        self.model_manager.save_model(model_state, performance_metrics=metrics)
        logger.info("Model saved successfully")
    
    def reset(self):
        """Reset predictor to initial state"""
        # Reset models
        self.models = {
            'sgd': SGDRegressor(
                loss='squared_error',
                penalty='l2',
                alpha=0.0001,
                learning_rate='invscaling',
                eta0=0.01,
                random_state=42
            ),
            'passive_aggressive': PassiveAggressiveRegressor(
                C=1.0,
                epsilon=0.1,
                random_state=42
            )
        }
        
        self.scaler = StandardScaler()
        self.model_weights = {'sgd': 0.5, 'passive_aggressive': 0.5}
        self.training_buffer.clear()
        self.prediction_errors.clear()
        self._is_initialized = False
        self._training_samples_count = 0
        self._last_retrain_count = 0
        
        # Reset model manager
        self.model_manager.reset_model()
        
        logger.info("ML predictor reset")
    
    def _initialize_models(self):
        """Initialize models with buffered data"""
        if len(self.training_buffer) < 10:
            logger.warning("Insufficient samples for initialization")
            return
        
        logger.info(f"Initializing models with {len(self.training_buffer)} samples")
        
        # Extract features and targets
        X = np.array([f for f, _ in self.training_buffer])
        y = np.array([t for _, t in self.training_buffer])
        
        # Fit scaler
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        # Initialize each model
        for name, model in self.models.items():
            try:
                # For incremental learners, use partial_fit
                model.partial_fit(X_scaled, y)
                logger.info(f"Initialized {name} model")
            except Exception as e:
                logger.error(f"Failed to initialize {name}: {e}")
        
        self._is_initialized = True
        self._last_retrain_count = self._training_samples_count
        logger.info("Models initialized successfully")
    
    def _full_retrain(self):
        """Perform full retrain on buffered data"""
        if len(self.training_buffer) < 20:
            logger.warning("Insufficient samples for retraining")
            return
        
        logger.info(f"Performing full retrain with {len(self.training_buffer)} samples")
        
        # Extract data
        X = np.array([f for f, _ in self.training_buffer])
        y = np.array([t for _, t in self.training_buffer])
        
        # Refit scaler
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        
        # Retrain models
        for name, model in self.models.items():
            try:
                # Reset and retrain
                model.partial_fit(X_scaled, y)
                logger.info(f"Retrained {name} model")
            except Exception as e:
                logger.error(f"Failed to retrain {name}: {e}")
        
        self._last_retrain_count = self._training_samples_count
        
        # Update model weights
        self._update_model_weights()
        
        # Save model
        self.save_model()
        
        logger.info("Full retrain complete")
    
    def _update_model_weights(self):
        """Update model weights based on recent performance"""
        if len(self.training_buffer) < 20:
            return
        
        # Use recent samples for validation
        recent_samples = self.training_buffer[-20:]
        X = np.array([f for f, _ in recent_samples])
        y = np.array([t for _, t in recent_samples])
        
        X_scaled = self.scaler.transform(X)
        
        # Calculate error for each model
        errors = {}
        for name, model in self.models.items():
            try:
                predictions = model.predict(X_scaled)
                mae = mean_absolute_error(y, predictions)
                errors[name] = mae
            except:
                errors[name] = float('inf')
        
        # Convert errors to weights (inverse)
        total_inverse = sum(1.0 / (e + 1e-6) for e in errors.values())
        for name in self.model_weights:
            if errors[name] != float('inf'):
                self.model_weights[name] = (1.0 / (errors[name] + 1e-6)) / total_inverse
            else:
                self.model_weights[name] = 0.0
        
        logger.debug(f"Updated model weights: {self.model_weights}")
    
    def _load_model(self):
        """Load saved model if exists"""
        model_state = self.model_manager.load_model()
        
        if model_state is None:
            logger.info("No saved model found, starting fresh")
            return
        
        try:
            self.models = model_state['models']
            self.scaler = model_state['scaler']
            self.model_weights = model_state['model_weights']
            self._training_samples_count = model_state['training_samples_count']
            self._is_initialized = model_state['is_initialized']
            
            logger.info(f"Loaded model with {self._training_samples_count} training samples")
        except Exception as e:
            logger.error(f"Failed to load model state: {e}")
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self._is_initialized:
            return {}
        
        feature_names = self.feature_engineer.get_feature_names()
        
        # Use SGD model coefficients as importance
        try:
            importances = np.abs(self.models['sgd'].coef_)
            
            # Normalize to sum to 1
            importances = importances / importances.sum()
            
            return dict(zip(feature_names, importances))
        except:
            return {}
    
    def get_top_features(self, n: int = 10) -> List[Tuple[str, float]]:
        """
        Get top N most important features.
        
        Args:
            n: Number of features to return
        
        Returns:
            List of (feature_name, importance) tuples
        """
        importance = self.get_feature_importance()
        
        if not importance:
            return []
        
        sorted_features = sorted(
            importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return sorted_features[:n]
