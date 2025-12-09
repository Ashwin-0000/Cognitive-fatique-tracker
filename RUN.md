# How to Run the Cognitive Fatigue Tracker

## Simplest Way - Double-Click

**Just double-click this file:**
```
run_app.bat
```

That's it! The script automatically uses the correct Python environment.

---

## Alternative - Command Line

If you prefer command line:

```powershell
# From the project directory
d:\code3\venv311\Scripts\python.exe main.py

# OR activate venv311 first
d:\code3\venv311\Scripts\activate
python main.py
```

---

## Important Notes

### ❌ DON'T Use
```powershell
# This WON'T work (Python 3.13, no MediaPipe)
d:\code3\.venv\Scripts\python.exe main.py

# This WON'T work (might use wrong Python)
python main.py
```

### ✅ DO Use
```powershell
# This WILL work (Python 3.11 with MediaPipe)
d:\code3\venv311\Scripts\python.exe main.py

# OR just double-click run_app.bat
```

---

## Troubleshooting

### "failed to locate pyvenv.cfg"
- You're using the old `.venv` (Python 3.13)
- **Solution:** Use `venv311` instead or run `run_app.bat`

### "python: command not found"
- Python not in PATH
- **Solution:** Use full path or run `run_app.bat`

### Camera doesn't work
- Make sure you enabled eye tracking in Settings
- Check camera permissions in Windows
- Verify webcam is connected

---

**TL;DR: Just double-click `run_app.bat`**
