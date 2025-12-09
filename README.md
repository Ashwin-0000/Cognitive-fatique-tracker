# Cognitive Fatigue Tracker 🧠

A comprehensive Python-based application that monitors your activity and tracks cognitive fatigue levels in real-time to help you maintain productivity and well-being.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

- **Real-time Activity Monitoring**: Tracks keyboard and mouse activity to assess work intensity
- **👁️ Eye Tracking (Optional)**: Monitors blink rate to detect eye strain and screen fatigue
- **Intelligent Fatigue Detection**: Multi-factor algorithm calculates fatigue based on time, activity patterns, breaks, and eye health
- **Visual Dashboard**: Beautiful, modern UI with real-time metrics and charts
- **Break Reminders**: Smart alerts when it's time to take a break
- **Session Tracking**: Complete work session management with break tracking
- **Data Persistence**: SQLite database stores all session history
- **Customizable Settings**: Configure work intervals, break times, and alert preferences
- **Dark/Light Themes**: Choose your preferred appearance

## Screenshots

The application features:
- Large fatigue score gauge with color-coded levels
- Real-time activity rate chart
- Fatigue score history visualization
- Work time and break countdown timers
- Session statistics dashboard

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the repository**

2. **Install dependencies**:
   ```bash
   cd cognitive_fatigue_tracker
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

```bash
python main.py
```

### Using the Tracker

1. **Start a Session**: Click "Start Session" to begin monitoring
2. **Monitor Your Progress**: Watch the fatigue score and activity metrics in real-time
3. **Take Breaks**: Click "Take Break" when alerts suggest, or manually when needed
4. **End Session**: Click "End Session" when you're done working

### Understanding Fatigue Levels

- **Low (0-30)**: ✅ You're fresh and focused
- **Moderate (30-60)**: ⚠️ Consider planning a break soon
- **High (60-80)**: ⚠️ Take a break to avoid burnout
- **Critical (80-100)**: 🚨 Stop immediately and rest

## Configuration

Access settings via the ⚙️ Settings button:

- **Work Interval**: Duration between breaks (default: 50 minutes)
- **Break Interval**: Recommended break length (default: 10 minutes)
- **Activity Monitoring**: Choose what to track (keyboard, mouse, etc.)
- **Alerts**: Enable/disable notifications and set cooldown periods
- **Appearance**: Switch between dark and light themes

## Eye Tracking Setup (Optional)

Eye tracking adds blink rate monitoring to detect eye strain.

**Requirements**:
- Webcam
- Python 3.8, 3.9, 3.10, or 3.11 (MediaPipe not yet compatible with 3.12/3.13)

**Installation**:
```bash
pip install mediapipe
```

**Enable**:
1. Open Settings (⚙️)
2. Scroll to "👁️ Eye Tracking (Optional)"
3. Read privacy notice
4. Enable and accept consent
5. Start session - camera will activate

**Privacy**: No video recorded, only blink counts tracked locally.

See [EYE_TRACKING_SETUP.md](EYE_TRACKING_SETUP.md) for detailed setup and troubleshooting.

## How It Works

### Fatigue Calculation

The application uses a sophisticated multi-factor algorithm:
- Fatigue score timeline
- User settings

## Project Structure

```
cognitive_fatigue_tracker/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── config/                 # Configuration files
│   └── default_settings.json
├── data/                   # Database and exports
├── logs/                   # Application logs
└── src/
    ├── models/            # Data models
    │   ├── activity_data.py
    │   ├── session.py
    │   └── fatigue_score.py
    ├── monitoring/        # Activity tracking
    │   ├── input_monitor.py
    │   └── time_tracker.py
    ├── analysis/          # Fatigue analysis
    │   ├── fatigue_analyzer.py
    │   └── alert_manager.py
    ├── storage/           # Data persistence
    │   ├── data_manager.py
    │   └── config_manager.py
    ├── ui/                # User interface
    │   ├── main_window.py
    │   ├── dashboard.py
    │   ├── charts.py
    │   └── settings_dialog.py
    └── utils/             # Utilities
        ├── logger.py
        └── helpers.py
```

## Technologies Used

- **CustomTkinter**: Modern UI framework
- **pynput**: Keyboard and mouse monitoring
- **matplotlib**: Data visualization
- **pandas**: Data management
- **SQLite**: Local database storage

## Tips for Best Results

1. **Start sessions when you begin work** to get accurate fatigue tracking
2. **Follow break recommendations** - they're calculated based on your activity patterns
3. **Review your history** to identify when you're most productive
4. **Adjust settings** to match your work style (Pomodoro, custom intervals, etc.)
5. **Take the alerts seriously** - they're designed to prevent burnout

## Privacy & Security

- All data is stored **locally** on your computer
- No data is sent to external servers
- Activity monitoring only tracks event counts, not content (keystrokes are not logged)
- You have full control over what is monitored

## Troubleshooting

### Application won't start
- Ensure Python 3.8+ is installed
- Install all dependencies: `pip install -r requirements.txt`
- Check logs in `logs/` directory

### Monitoring not working
- On some systems, you may need to run with administrator privileges
- Check Settings to ensure monitoring options are enabled

### Charts not displaying
- Ensure matplotlib is installed correctly
- Try reinstalling: `pip install --upgrade matplotlib`

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## License

MIT License - feel free to use and modify for your needs.

## Acknowledgments

Built with modern Python tools and designed to help knowledge workers maintain their cognitive health.

---

**Stay focused, take breaks, and work smarter! 🚀**
