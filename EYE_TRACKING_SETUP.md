# Eye Tracking Feature - Setup Notes

## Python Version Requirement

**Important**: Eye tracking with MediaPipe currently requires **Python 3.8, 3.9, 3.10, or 3.11**.

MediaPipe does not yet support Python 3.12 or 3.13.

## Installation Options

### Option 1: Use Python 3.8-3.11
If you need eye tracking functionality:
1. Install Python 3.11 (recommended)
2. Create a virtual environment:
   ```bash
   python3.11 -m venv venv
   venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install mediapipe
   ```

### Option 2: Use Without Eye Tracking
The application works perfectly without eye tracking:
- All other features (activity monitoring, fatigue detection, charts, alerts) work normally
- Eye tracking section in dashboard will show "Disabled"
- Fatigue algorithm uses 5 factors instead of 6

## Verifying Eye Tracking

When eye tracking is available and enabled:
- Dashboard shows "Eye Tracking: Active" and  blink rate
- Third chart appears showing blink rate history
- Eye strain alerts trigger when blink rate is low
- Fatigue score includes eye strain factor

## Troubleshooting

### Camera Not Found
- Ensure webcam is connected and not used by another application
- Try different camera_index in settings (0, 1, 2...)
- Check camera permissions in Windows Settings

### MediaPipe Import Error
- Verify Python version: `python --version`
- Must be 3.8, 3.9, 3.10, or 3.11
- Reinstall mediapipe: `pip uninstall mediapipe && pip install mediapipe`

### Low Performance
- Eye tracking uses ~5-10% CPU
- If experiencing lag, disable eye tracking in Settings
- Reduce video resolution in code if needed

## Privacy & Security

- No video is recorded or saved
- Only blink counts are tracked locally
- Camera releases when session ends
- All processing is done on your computer
- No data sent to external servers
