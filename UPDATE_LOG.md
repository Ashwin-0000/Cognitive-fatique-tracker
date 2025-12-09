# Cognitive Fatigue Tracker - Update Log

## December 8, 2025

### Eye Tracking Feature Implementation

#### Backend Changes

**New Files Created:**
- `src/models/eye_data.py` - EyeData model for blink rate metrics
- `src/monitoring/eye_tracker.py` - Eye tracking with MediaPipe Face Mesh
- `EYE_TRACKING_SETUP.md` - Setup documentation
- `EYE_TRACKING_PYTHON311_SETUP.md` - Python 3.11 specific setup
- `EYE_TRACKING_FIX.md` - Crash fix documentation
- `TROUBLESHOOTING.md` - General troubleshooting guide
- `RUN.md` - Running instructions
- `run_app.bat` - Launcher script

**Modified Files:**
1. `requirements.txt` - Added opencv-python, mediapipe (optional)
2. `config/default_settings.json` - Added eye_tracking configuration section
3. `src/models/__init__.py` - Exported EyeData
4. `src/analysis/fatigue_analyzer.py` - Added 6th factor (blink rate) to fatigue scoring
5. `src/analysis/alert_manager.py` - Added eye strain alerts
6. `src/monitoring/eye_tracker.py` - Comprehensive error handling in capture loop
7. `main.py` - Added global exception handler

#### Frontend Changes

**Modified Files:**
1. `src/ui/dashboard.py` - Added blink rate card and eye tracking status indicator
2. `src/ui/charts.py` - Added BlinkRateChart class, fixed MiniGaugeChart
3. `src/ui/settings_dialog.py` - Added eye tracking section with privacy consent
4. `src/ui/main_window.py` - Multiple enhancements:
   - Eye tracker integration in session start/stop
   - Dynamic eye tracking enable/disable from settings
   - Camera disconnect detection
   - Comprehensive error handling in update loop
   - All chart updates wrapped in try-except
   - All alert checks wrapped in try-except
   - Dashboard update error handling

### Bug Fixes

#### Issue #1: App Crashes Abruptly
**Symptoms:** App closes randomly after a few seconds/minutes with no error message
**Root Cause:** Background threads (eye tracker) crashing silently
**Fix Applied:**
- Added global exception handler in main.py (sys.excepthook)
- Wrapped eye tracker capture loop in try-except-finally
- Added camera availability checks
- Enhanced error logging throughout

**Files Modified:**
- `main.py` - Global exception handler
- `src/monitoring/eye_tracker.py` - Thread-safe capture loop
- `src/ui/main_window.py` - Defensive error handling

#### Issue #2: Settings Don't Apply Immediately
**Symptoms:** Changing eye tracking in settings has no effect until app restart
**Root Cause:** Settings not applied dynamically during active session
**Fix Applied:**
- Modified `_on_settings_saved()` to detect eye tracking toggle
- Start/stop eye tracker immediately when setting changes
- Show confirmation messages to user

**Files Modified:**
- `src/ui/main_window.py` - Dynamic eye tracking control

#### Issue #3: Camera Disconnect Not Detected  
**Symptoms:** If camera turns off, app doesn't notice and continues showing stale data
**Root Cause:** No camera availability monitoring in update loop
**Fix Applied:**
- Added `is_camera_available()` check before getting blink rate
- Auto-disable eye tracker if camera becomes unavailable
- Show warning notification to user

**Files Modified:**
- `src/ui/main_window.py` - Camera monitoring in update loop

#### Issue #4: MediaPipe Import Errors
**Symptoms:** App crashes on startup with "NoneType has no attribute 'solutions'"
**Root Cause:** MediaPipe access before availability check
**Fix Applied:**
- Made all eye tracking imports optional
- Check availability before accessing mp.solutions
- Graceful fallback if dependencies missing

**Files Modified:**
- `src/monitoring/eye_tracker.py` - Optional imports with availability checks

### Environment Setup

**Python 3.11 Installation:**
- Installed Python 3.11.9 via winget
- Created venv311 virtual environment
- Installed all dependencies including MediaPipe

**Virtual Environments:**
- `.venv` (Python 3.13) - Core features only, no MediaPipe
- `venv311` (Python 3.11) - Full features including eye tracking ✓

### Error Handling Improvements

**Global Level:**
- sys.excepthook catches all uncaught exceptions
- Logs errors with full stack traces
- Shows user-friendly error messages

**Update Loop:**
- Activity rate retrieval - try-except
- Blink rate retrieval - try-except with camera check
- Fatigue score calculation - try-except with safe default
- Dashboard updates - try-except
- Chart updates - try-except per chart
- Alert checks - try-except per alert type
- Session auto-save - try-except

**Eye Tracker:**
- Capture loop - nested try-except-finally
- Camera opening - detailed logging
- MediaPipe initialization - separate try-except
- Frame processing - individual error handling

### Known Issues

1. **MediaPipe Python 3.13 Incompatibility**
   - MediaPipe not yet available for Python 3.13
   - Workaround: Use Python 3.11 environment (venv311)
   - Status: External library limitation

2. **MediaPipe Warnings**
   - "NORM_RECT without IMAGE_DIMENSIONS" warning appears
   - Status: Harmless MediaPipe warning, doesn't affect functionality

### Testing Results

✅ App launches successfully
✅ Core features work without eye tracking
✅ Eye tracking works with Python 3.11 + MediaPipe
✅ Settings apply immediately during session
✅ Camera disconnect detected and handled
✅ Crashes now show error messages instead of silent failure
✅ Comprehensive error logging

### Performance

- Eye tracking: ~5-10% CPU usage
- Update interval: 1000ms (1 second)
- Camera: 640x480 @ 30 FPS
- Face mesh: 1 face, refined landmarks

### Privacy

- Eye tracking disabled by default
- Explicit opt-in consent required
- No video recording or storage
- Only blink counts tracked
- All processing local
- Clear privacy notices in UI

---

## Update Log Format

Each update should include:
1. **Date and Time**
2. **Component** (Frontend/Backend/Both)
3. **Type** (Feature/Bug Fix/Enhancement)
4. **Description** of change
5. **Files Modified**
6. **Impact** on users
7. **Testing Status**

---

*Last Updated: December 8, 2025 16:06 IST*
