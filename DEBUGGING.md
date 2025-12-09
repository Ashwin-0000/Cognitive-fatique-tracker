# Debugging Guide

## Log Files Location

All logs are stored in `logs/` directory:

### Regular Logs
- `logs/app_YYYYMMDD.log` - Main application log (INFO level and above)
- Contains all errors, warnings, and important events

### Debug Logs  
- `logs/debug/state_YYYYMMDD_HHMMSS.json` - State tracking log
- Contains detailed component state changes
- Created when debug mode is enabled

## Reading Logs

### Find Recent Errors
```powershell
# Last 50 lines
Get-Content logs\app_20251208.log | Select-Object -Last 50

# Search for errors
Select-String -Path logs\app_*.log -Pattern "ERROR"

# Search for specific component
Select-String -Path logs\app_*.log -Pattern "EyeTracker"
```

### View State Changes
```powershell
# Pretty print state log
Get-Content logs\debug\state_*.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

## Understanding Log Entries

### Log Format
```
YYYY-MM-DD HH:MM:SS - ComponentName - LEVEL - Message
```

**Levels:**
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages (app continues)
- `ERROR` - Error messages (handled errors)
- `CRITICAL` - Critical errors (app may crash)

### Common Log Messages

**Eye Tracking:**
```
INFO  - Eye tracker started successfully
WARNING - Camera became unavailable, disabling eye tracker
ERROR - Failed to initialize MediaPipe Face Mesh
```

**UI Updates:**
```
DEBUG - Dashboard.update_stats: {"fatigue_score": 25, "blink_rate": 18}
ERROR - Error updating dashboard: ...
```

**Session Management:**
```
INFO - Started session ABC123
INFO - Ended session ABC123
```

## Enabling Debug Mode

To get more detailed logs, edit `src/utils/logger.py`:

```python
default_logger = setup_logger("CognitiveFatigueTracker", debug_mode=True)
```

This will:
- Log DEBUG level messages
- Create state tracking JSON files
- Record all component state changes

## Troubleshooting with Logs

### App Crashes
1. Check last lines of log file
2. Look for ERROR or CRITICAL messages
3. Check stack trace after error message

### Eye Tracking Issues
1. Search for "EyeTracker" in logs
2. Check camera opening messages
3. Look for MediaPipe errors

### UI Not Updating
1. Search for "Error updating" messages
2. Check state log for update frequency
3. Look for exceptions in update loop

### Settings Not Applying
1. Search for "Settings updated"
2. Check for errors in settings save
3. Verify eye tracking enable/disable messages

## Example Debugging Session

```powershell
# 1. Run the app
d:\code3\venv311\Scripts\python.exe d:\code3\cognitive_fatigue_tracker\main.py

# 2. Reproduce the issue

# 3. Check the log
Get-Content logs\app_20251208.log | Select-Object -Last 100

# 4. Search for specific errors
Select-String -Path logs\app_20251208.log -Pattern "ERROR|CRITICAL"

# 5. View state changes
Get-Content logs\debug\state_*.json
```

## Log Rotation

Logs are automatically created per day:
- Old logs are kept indefinitely
- Manual cleanup: Delete old `app_*.log` files
- Debug logs: Delete old `state_*.json` files

## Reporting Issues

When reporting bugs, include:
1. **Log file** - Last 100 lines from app_*.log
2. **Error message** - Exact error text
3. **State log** - If applicable
4. **Steps to reproduce** - What you did before crash
5. **System info** - Python version, OS

---

*For more help, check TROUBLESHOOTING.md*
