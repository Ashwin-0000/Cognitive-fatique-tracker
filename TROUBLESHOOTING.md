# Troubleshooting UI Issues

## Common Issues and Solutions

### Issue 1: App Window Freezes/Unresponsive
**Symptoms:** Window appears but can't click anything, UI frozen

**Possible Causes:**
- Eye tracker blocking main thread
- MediaPipe initialization hanging

**Solution:** Start without eye tracking enabled, then enable it later

### Issue 2: Metrics Don't Update
**Symptoms:** Can interact with app, but dashboard numbers never change

**Possible Causes:**
- Update loop not running
- Session not starting properly
- Input monitor not working

**Solution:** Check that you clicked "Start Session" button

### Issue 3: Eye Tracking Shows "--"
**Symptoms:** Everything works but blink rate stays at "--"

**Possible Causes:**
- Eye tracking not enabled in settings
- Camera not accessible
- MediaPipe not initializing

**Solutions:**
1. Enable eye tracking in Settings
2. Accept consent dialog
3. Click "Start Session" (camera activates AFTER session starts)
4. Check camera permissions in Windows

### Issue 4: App Crashes on Start Session
**Symptoms:** Click "Start Session", then app crashes

**Possible Cause:** Eye tracker initialization error

**Solution:** Disable eye tracking in settings first

## Quick Diagnostic Steps

1. **Launch app** - Does window appear? ✓/✗
2. **Click Settings** - Does dialog open? ✓/✗
3. **Start Session** (with eye tracking OFF) - Does it work? ✓/✗
4. **Enable eye tracking** - Does consent dialog appear? ✓/✗
5. **Start Session** (with eye tracking ON) - Does camera light turn on? ✓/✗

## If You're Stuck

**Try this minimal test:**
1. Close app completely
2. Launch with: `d:\code3\venv311\Scripts\python.exe d:\code3\cognitive_fatigue_tracker\main.py`
3. Do NOT enable eye tracking
4. Click "Start Session"
5. Type on keyboard
6. Watch if "Activity Rate" number changes

If step 6 works → problem is with eye tracking
If step 6 doesn't work → problem is with core monitoring

Let me know which scenario matches your issue!
