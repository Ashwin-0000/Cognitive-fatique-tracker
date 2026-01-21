"""Eye tracker for monitoring blink rate using webcam"""
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    mp = None

import threading
import time
from datetime import datetime, timedelta
from collections import deque
from typing import Optional, Callable
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

from src.models.eye_data import EyeData
from src.utils.logger import default_logger as logger


class EyeTracker:
    """Tracks eye metrics using webcam and MediaPipe Face Mesh"""

    # Eye Aspect Ratio threshold for blink detection
    EAR_THRESHOLD = 0.25
    EAR_CONSEC_FRAMES = 2  # Consecutive frames below threshold to count as blink

    # MediaPipe face mesh eye landmark indices
    LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

    def __init__(
        self,
        camera_index: int = 0,
        on_blink: Optional[Callable[[], None]] = None
    ):
        """
        Initialize eye tracker.

        Args:
            camera_index: Camera device index
            on_blink: Callback function when blink is detected
        """
        self.camera_index = camera_index
        self.on_blink = on_blink

        # MediaPipe setup - only if available
        if MEDIAPIPE_AVAILABLE and mp is not None:
            self.mp_face_mesh = mp.solutions.face_mesh
        else:
            self.mp_face_mesh = None
        self.face_mesh = None

        # Camera
        self.camera = None
        self.is_running = False
        self._capture_thread: Optional[threading.Thread] = None

        # Blink tracking
        self._blink_counter = 0
        self._frame_counter = 0
        self._total_blinks = 0
        self._blink_timestamps = deque(maxlen=100)  # Store last 100 blinks

        # Performance
        self._last_process_time = time.time()
        self._fps = 0

    def start(self) -> bool:
        """
        Start eye tracking.

        Returns:
            True if started successfully, False otherwise
        """
        # Check dependencies
        if not CV2_AVAILABLE:
            logger.error(
                "OpenCV is not installed. Eye tracking requires opencv-python.")
            logger.info("Install with: pip install opencv-python")
            return False

        if not MEDIAPIPE_AVAILABLE:
            logger.error(
                "MediaPipe is not installed. Eye tracking requires mediapipe.")
            logger.info(
                "Install with: pip install mediapipe (requires Python 3.8-3.11)")
            return False

        if not NUMPY_AVAILABLE:
            logger.error(
                "NumPy is not installed. Eye tracking requires numpy.")
            logger.info("Install with: pip install numpy")
            return False

        if self.is_running:
            logger.warning("Eye tracker already running")
            return True

        try:
            # Initialize camera
            logger.info(f"Attempting to open camera {self.camera_index}")
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                logger.error(f"Failed to open camera {self.camera_index}")
                return False

            # Set camera properties for better performance
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)

            logger.info("Camera opened successfully")

            # Initialize MediaPipe Face Mesh with error handling
            try:
                logger.info("Initializing MediaPipe Face Mesh")
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                logger.info("MediaPipe Face Mesh initialized successfully")
            except Exception as e:
                logger.error(
                    f"Failed to initialize MediaPipe Face Mesh: {e}",
                    exc_info=True)
                self.camera.release()
                self.camera = None
                return False

            # Start capture thread
            self.is_running = True
            self._capture_thread = threading.Thread(
                target=self._capture_loop, daemon=True)
            self._capture_thread.start()

            logger.info("Eye tracker started successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start eye tracker: {e}")
            self.stop()
            return False

    def stop(self):
        """Stop eye tracking and release resources"""
        self.is_running = False

        if self._capture_thread:
            self._capture_thread.join(timeout=2.0)
            self._capture_thread = None

        if self.face_mesh:
            self.face_mesh.close()
            self.face_mesh = None

        if self.camera:
            self.camera.release()
            self.camera = None

        logger.info("Eye tracker stopped")

    def _capture_loop(self):
        """Main capture loop running in background thread"""
        logger.info("Eye tracker capture loop started")
        try:
            while self.is_running:
                try:
                    if not self.camera or not self.camera.isOpened():
                        logger.warning("Camera not available in capture loop")
                        time.sleep(1.0)
                        continue

                    ret, frame = self.camera.read()
                    if not ret:
                        logger.warning("Failed to read frame from camera")
                        time.sleep(0.1)
                        continue

                    # Process frame
                    self._process_frame(frame)

                    # Limit processing rate
                    time.sleep(0.033)  # ~30 FPS

                except Exception as e:
                    logger.error(
                        f"Error in capture loop iteration: {e}",
                        exc_info=True)
                    time.sleep(0.1)
        except Exception as e:
            logger.error(f"Fatal error in capture loop: {e}", exc_info=True)
        finally:
            logger.info("Eye tracker capture loop ended")

    def _process_frame(self, frame):
        """Process frame to detect blinks"""
        try:
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process with MediaPipe
            results = self.face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]

                # Calculate Eye Aspect Ratio
                left_ear = self._calculate_ear(
                    face_landmarks, self.LEFT_EYE_INDICES)
                right_ear = self._calculate_ear(
                    face_landmarks, self.RIGHT_EYE_INDICES)
                avg_ear = (left_ear + right_ear) / 2.0

                # Detect blink
                if avg_ear < self.EAR_THRESHOLD:
                    self._frame_counter += 1
                else:
                    # Check if blink occurred
                    if self._frame_counter >= self.EAR_CONSEC_FRAMES:
                        self._register_blink()
                    self._frame_counter = 0

            # Update FPS
            current_time = time.time()
            self._fps = 1.0 / \
                (current_time - self._last_process_time) if self._last_process_time else 0
            self._last_process_time = current_time

        except Exception as e:
            logger.error(f"Error processing frame: {e}")

    def _calculate_ear(self, landmarks, eye_indices) -> float:
        """
        Calculate Eye Aspect Ratio for blink detection.

        Args:
            landmarks: MediaPipe face landmarks
            eye_indices: Indices of eye landmarks

        Returns:
            Eye aspect ratio value
        """
        try:
            # Get eye landmarks
            points = []
            for idx in eye_indices:
                landmark = landmarks.landmark[idx]
                points.append([landmark.x, landmark.y])

            points = np.array(points)

            # Calculate distances
            # Vertical distances
            v1 = np.linalg.norm(points[1] - points[5])
            v2 = np.linalg.norm(points[2] - points[4])

            # Horizontal distance
            h = np.linalg.norm(points[0] - points[3])

            # Eye Aspect Ratio
            ear = (v1 + v2) / (2.0 * h)
            return ear

        except Exception as e:
            logger.error(f"Error calculating EAR: {e}")
            return 0.5  # Default value

    def _register_blink(self):
        """Register a blink occurrence"""
        self._total_blinks += 1
        self._blink_timestamps.append(datetime.now())

        # Call callback if provided
        if self.on_blink:
            try:
                self.on_blink()
            except Exception as e:
                logger.error(f"Error in blink callback: {e}")

        logger.debug(f"Blink detected (total: {self._total_blinks})")

    def get_blink_rate(self, window_seconds: int = 60) -> float:
        """
        Get current blink rate (blinks per minute).

        Args:
            window_seconds: Time window to calculate rate

        Returns:
            Blinks per minute
        """
        if not self._blink_timestamps:
            return 0.0

        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        recent_blinks = sum(1 for ts in self._blink_timestamps if ts >= cutoff)

        # Calculate rate (blinks per minute)
        rate = (recent_blinks / window_seconds) * 60
        return rate

    def get_total_blinks(self) -> int:
        """Get total number of blinks in current session"""
        return self._total_blinks

    def get_eye_data(self) -> EyeData:
        """
        Get current eye tracking data.

        Returns:
            EyeData object with current metrics
        """
        return EyeData(
            blink_rate=self.get_blink_rate(),
            total_blinks=self._total_blinks,
            timestamp=datetime.now()
        )

    def reset_counters(self):
        """Reset blink counters"""
        self._total_blinks = 0
        self._blink_timestamps.clear()
        logger.debug("Reset blink counters")

    def get_fps(self) -> float:
        """Get current processing FPS"""
        return self._fps

    def is_camera_available(self) -> bool:
        """Check if camera is available"""
        return self.camera is not None and self.camera.isOpened()
