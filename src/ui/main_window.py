"""Main application window"""
import customtkinter as ctk
import threading
from datetime import datetime, timedelta
from typing import Optional
from tkinter import messagebox

from src.ui.dashboard import Dashboard
from src.ui.charts import ActivityChart, FatigueChart, BlinkRateChart
from src.ui.settings_dialog import SettingsDialog
from src.storage.config_manager import ConfigManager
from src.storage.data_manager import DataManager
from src.monitoring.input_monitor import InputMonitor
from src.monitoring.time_tracker import TimeTracker
from src.monitoring.eye_tracker import EyeTracker
from src.analysis.fatigue_analyzer import FatigueAnalyzer
from src.analysis.alert_manager import AlertManager
from src.models.session import Session
from src.models.activity_data import ActivityData
from src.utils.logger import default_logger as logger


class MainWindow(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.data_manager = DataManager()
        
        # Configure window
        self.title("Cognitive Fatigue Tracker")
        self.geometry("1200x800")
        
        # Set theme
        theme = self.config_manager.get('ui.theme', 'dark')
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")
        
        # Initialize components
        self.input_monitor: Optional[InputMonitor] = None
        self.time_tracker: Optional[TimeTracker] = None
        self.eye_tracker: Optional[EyeTracker] = None
        self.fatigue_analyzer = FatigueAnalyzer()
        self.alert_manager = AlertManager(on_alert=self._show_alert)
        
        self.current_session: Optional[Session] = None
        self.is_monitoring = False
        
        # Activity data for charts
        self.activity_history = []
        self.fatigue_history = []
        self.blink_history = []
        
        # Create UI
        self._create_widgets()
        
        # Start update loop
        self.update_interval = self.config_manager.get('ui.update_interval_ms', 1000)
        self._start_update_loop()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        logger.info("Main window initialized")
    
    def _create_widgets(self):
        """Create UI widgets"""
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Top bar
        top_bar = ctk.CTkFrame(self, height=60, corner_radius=0)
        top_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        top_bar.grid_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            top_bar,
            text="🧠 Cognitive Fatigue Tracker",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20)
        
        # Control buttons
        button_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        button_frame.pack(side="right", padx=20)
        
        self.start_button = ctk.CTkButton(
            button_frame,
            text="Start Session",
            command=self._start_session,
            width=120
        )
        self.start_button.pack(side="left", padx=5)
        
        self.break_button = ctk.CTkButton(
            button_frame,
            text="Take Break",
            command=self._toggle_break,
            width=120,
            state="disabled"
        )
        self.break_button.pack(side="left", padx=5)
        
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="End Session",
            command=self._stop_session,
            width=120,
            state="disabled",
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        self.stop_button.pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="⚙️ Settings",
            command=self._open_settings,
            width=100
        ).pack(side="left", padx=5)
        
        # Main content area
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure((0, 1), weight=1)
        
        # Dashboard (top)
        self.dashboard = Dashboard(content)
        self.dashboard.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Charts section (bottom)
        charts_frame = ctk.CTkFrame(content, fg_color="transparent")
        charts_frame.grid(row=1, column=0, sticky="nsew")
        charts_frame.grid_columnconfigure((0, 1), weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        
        # Activity chart
        activity_container = ctk.CTkFrame(charts_frame)
        activity_container.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.activity_chart = ActivityChart(activity_container)
        self.activity_chart.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Fatigue chart
        fatigue_container = ctk.CTkFrame(charts_frame)
        fatigue_container.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self.fatigue_chart = FatigueChart(fatigue_container)
        self.fatigue_chart.pack(fill="both", expand=True, padx=10, pady=10)
        
        #  Blink rate chart (initially hidden, shown when eye tracking enabled)
        self.blink_chart_container = None
        self.blink_chart = None
    
    def _start_session(self):
        """Start a new monitoring session"""
        if self.is_monitoring:
            return
        
        # Create new session
        self.current_session = Session()
        self.fatigue_analyzer.start_session()
        
        # Initialize monitors
        config = self.config_manager
        self.input_monitor = InputMonitor(
            on_activity=self._on_activity,
            track_keyboard=config.get('monitoring.track_keyboard', True),
            track_mouse_clicks=config.get('monitoring.track_mouse_clicks', True),
            track_mouse_movement=config.get('monitoring.track_mouse_movement', False)
        )
        
        self.time_tracker = TimeTracker(
            work_interval_minutes=config.get('work_interval_minutes', 50),
            break_interval_minutes=config.get('break_interval_minutes', 10)
        )
        self.time_tracker.start_session(self.current_session)
        
        # Configure alert manager
        self.alert_manager.enable_alerts(
            break_alerts=config.get('alerts.enable_break_reminders', True),
            fatigue_alerts=config.get('alerts.enable_fatigue_alerts', True)
        )
        self.alert_manager.update_cooldown(config.get('alerts.alert_cooldown_minutes', 10))
        
        # Initialize eye tracking if enabled
        if config.get('eye_tracking.enabled', False):
            try:
                self.eye_tracker = EyeTracker(
                    camera_index=config.get('eye_tracking.camera_index', 0)
                )
                if self.eye_tracker.start():
                    logger.info("Eye tracking started")
                else:
                    logger.warning("Eye tracking failed to start")
                    self.eye_tracker = None
            except Exception as e:
                logger.error(f"Failed to initialize eye tracker: {e}")
                self.eye_tracker = None
        
        # Start monitoring
        self.input_monitor.start()
        self.is_monitoring = True
        
        # Update UI
        self.start_button.configure(state="disabled")
        self.break_button.configure(state="normal")
        self.stop_button.configure(state="normal")
        
        # Save session
        self.data_manager.save_session(self.current_session)
        
        logger.info(f"Started session {self.current_session.session_id}")
        self.alert_manager.send_session_start_notification()
    
    def _stop_session(self):
        """Stop current monitoring session"""
        if not self.is_monitoring:
            return
        
        # Stop monitoring
        if self.input_monitor:
            self.input_monitor.stop()
            self.input_monitor = None
        
        if self.eye_tracker:
            self.eye_tracker.stop()
            self.eye_tracker = None
        
        if self.time_tracker:
            self.time_tracker.end_session()
            self.time_tracker = None
        
        # End session
        if self.current_session:
            self.current_session.end_session()
            self.data_manager.save_session(self.current_session)
            logger.info(f"Ended session {self.current_session.session_id}")
            self.current_session = None
        
        self.is_monitoring = False
        
        # Update UI
        self.start_button.configure(state="normal")
        self.break_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")
        
        # Show summary
        self._show_session_summary()
    
    def _toggle_break(self):
        """Toggle break status"""
        if not self.time_tracker:
            return
        
        if self.time_tracker.is_on_break:
            self.time_tracker.end_break()
            self.break_button.configure(text="Take Break")
            logger.info("Ended break")
        else:
            self.time_tracker.start_break()
            self.break_button.configure(text="End Break")
            logger.info("Started break")
    
    def _on_activity(self, activity: ActivityData):
        """Handle activity event"""
        if self.current_session:
            self.current_session.total_activity_count += 1
            # Optionally save to database (batched for performance)
            # self.data_manager.save_activity(activity, self.current_session.session_id)
    
    def _update_ui(self):
        """Update UI with current data"""
        if not self.is_monitoring or not self.time_tracker:
            return
        
        try:
            # Get current metrics with error handling
            try:
                activity_rate = self.input_monitor.get_activity_rate() if self.input_monitor else 0
            except Exception as e:
                logger.error(f"Error getting activity rate: {e}")
                activity_rate = 0
            
            work_time = self.time_tracker.get_work_time()
            session_time = self.time_tracker.get_session_time()
            time_until_break = self.time_tracker.get_time_until_break()
            is_on_break = self.time_tracker.is_on_break
            
            # Get blink rate if eye tracking is enabled - with error handling
            blink_rate = 0.0
            if self.eye_tracker:
                try:
                    # Check if camera is still available
                    if not self.eye_tracker.is_camera_available():
                        logger.warning("Camera became unavailable, disabling eye tracker")
                        self.eye_tracker.stop()
                        self.eye_tracker = None
                        # Show notification to user
                        self.after(0, lambda: messagebox.showwarning(
                            "Camera Disconnected",
                            "Eye tracking stopped: Camera is no longer available."
                        ))
                    else:
                        blink_rate = self.eye_tracker.get_blink_rate()
                except Exception as e:
                    logger.error(f"Error getting blink rate: {e}")
                    # Disable eye tracker if it keeps failing
                    self.eye_tracker.stop()
                    self.eye_tracker = None
            
            # Calculate fatigue score
            try:
                fatigue_score = self.fatigue_analyzer.calculate_score(
                    work_duration_minutes=work_time.total_seconds() / 60,
                    activity_rate=activity_rate,
                    time_since_break_minutes=(work_time.total_seconds() / 60) if not is_on_break else 0,
                    is_on_break=is_on_break,
                    blink_rate=blink_rate
                )
            except Exception as e:
                logger.error(f"Error calculating fatigue score: {e}", exc_info=True)
                # Use a safe default score
                from src.models.fatigue_score import FatigueScore
                fatigue_score = FatigueScore(score=0.0)
            
            # Save fatigue score periodically
            try:
                if self.current_session and len(self.fatigue_analyzer.history) % 10 == 0:
                    self.data_manager.save_fatigue_score(fatigue_score, self.current_session.session_id)
            except Exception as e:
                logger.error(f"Error saving fatigue score: {e}")
            
            # Update dashboard with error handling
            try:
                self.dashboard.update_stats(
                fatigue_score=fatigue_score.score,
                fatigue_level=fatigue_score.get_level(),
                fatigue_color=fatigue_score.get_color(),
                work_time_seconds=work_time.total_seconds(),
                session_time_seconds=session_time.total_seconds(),
                activity_rate=activity_rate,
                time_until_break_seconds=time_until_break.total_seconds(),
                is_on_break=is_on_break,
                blink_rate=blink_rate,
                eye_tracking_enabled=self.eye_tracker is not None
            )
            
            except Exception as e:
                logger.error(f"Error updating dashboard: {e}")
            
            # Update charts with error handling
            try:
                now = datetime.now()
                
                # Activity chart - last hour
                self.activity_history.append((now, activity_rate))
                cutoff = now - timedelta(minutes=60)
                self.activity_history = [(t, v) for t, v in self.activity_history if t >= cutoff]
                self.activity_chart.update_data(self.activity_history)
            except Exception as e:
                logger.error(f"Error updating activity chart: {e}")
            
            # Fatigue chart - last hour
            try:
                self.fatigue_history.append((now, fatigue_score.score))
                self.fatigue_history = [(t, v) for t, v in self.fatigue_history if t >= cutoff]
                self.fatigue_chart.update_data(self.fatigue_history)
            except Exception as e:
                logger.error(f"Error updating fatigue chart: {e}")
            
            # Blink rate chart (if eye tracking enabled)
            try:
                if self.eye_tracker and blink_rate > 0:
                    self.blink_history.append((now, blink_rate))
                    self.blink_history = [(t, v) for t, v in self.blink_history if t >= cutoff]
                    # Create chart if not exists
                    if self.blink_chart is None:
                        self._create_blink_chart()
                    if self.blink_chart:
                        self.blink_chart.update_data(self.blink_history)
            except Exception as e:
                logger.error(f"Error updating blink chart: {e}")
            
            # Check alerts with error handling
            try:
                self.alert_manager.check_break_reminder(time_until_break, is_on_break)
            except Exception as e:
                logger.error(f"Error checking break reminder: {e}")
            
            try:
                self.alert_manager.check_fatigue_level(fatigue_score)
            except Exception as e:
                logger.error(f"Error checking fatigue level: {e}")
            
            try:
                if self.eye_tracker and blink_rate > 0:
                    self.alert_manager.check_eye_strain(blink_rate)
            except Exception as e:
                logger.error(f"Error checking eye strain: {e}")
            
            # Auto-save session periodically
            if self.current_session and session_time.total_seconds() % 60 == 0:
                self.data_manager.save_session(self.current_session)
        
        except Exception as e:
            logger.error(f"Error updating UI: {e}", exc_info=True)
    
    def _start_update_loop(self):
        """Start the UI update loop"""
        self._update_ui()
        self.after(self.update_interval, self._start_update_loop)
    
    def _create_blink_chart(self):
        """Create blink rate chart dynamically"""
        try:
            # Get charts frame
            charts_frame = self.dashboard.master
            charts_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Create blink chart container
            self.blink_chart_container = ctk.CTkFrame(charts_frame.master)
            self.blink_chart_container.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
            
            self.blink_chart = BlinkRateChart(self.blink_chart_container)
            self.blink_chart.pack(fill="both", expand=True, padx=10, pady=10)
            
            logger.info("Created blink rate chart")
        except Exception as e:
            logger.error(f"Failed to create blink chart: {e}")
    
    def _show_alert(self, title: str, message: str):
        """Show alert dialog"""
        # Run in main thread
        self.after(0, lambda: messagebox.showinfo(title, message))
    
    def _show_session_summary(self):
        """Show session summary dialog"""
        if not self.current_session:
            return
        
        stats = self.current_session.get_stats()
        summary = f"""
Session Summary

Duration: {stats['total_duration_minutes']:.1f} minutes
Work Time: {stats['work_duration_minutes']:.1f} minutes
Breaks Taken: {stats['break_count']}
Total Activities: {stats['total_activity_count']}

Great work! Remember to take regular breaks.
        """
        
        messagebox.showinfo("Session Complete", summary.strip())
    
    def _open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self, self.config_manager, on_save=self._on_settings_saved)
    
    def _on_settings_saved(self):
        """Handle settings save"""
        try:
            # Apply theme change
            theme = self.config_manager.get('ui.theme', 'dark')
            ctk.set_appearance_mode(theme)
            
            # Handle eye tracking setting change
            eye_tracking_enabled = self.config_manager.get('eye_tracking.enabled', False)
            
            # If monitoring is active, dynamically start/stop eye tracking
            if self.is_monitoring:
                if eye_tracking_enabled and not self.eye_tracker:
                    # User enabled eye tracking - start it
                    try:
                        self.eye_tracker = EyeTracker(
                            camera_index=self.config_manager.get('eye_tracking.camera_index', 0)
                        )
                        if self.eye_tracker.start():
                            logger.info("Eye tracking enabled during session")
                            messagebox.showinfo("Eye Tracking", "Eye tracking enabled! Camera is now active.")
                        else:
                            logger.warning("Eye tracking failed to start")
                            self.eye_tracker = None
                            messagebox.showwarning("Eye Tracking", "Could not start eye tracking. Check camera availability.")
                    except Exception as e:
                        logger.error(f"Failed to enable eye tracker: {e}")
                        self.eye_tracker = None
                        messagebox.showerror("Eye Tracking", f"Error enabling eye tracking: {str(e)}")
                
                elif not eye_tracking_enabled and self.eye_tracker:
                    # User disabled eye tracking - stop it
                    try:
                        self.eye_tracker.stop()
                        self.eye_tracker = None
                        logger.info("Eye tracking disabled during session")
                        messagebox.showinfo("Eye Tracking", "Eye tracking disabled. Camera stopped.")
                    except Exception as e:
                        logger.error(f"Error disabling eye tracker: {e}")
            
            # Update components if monitoring
            if self.is_monitoring and self.time_tracker:
                self.time_tracker.update_intervals(
                    self.config_manager.get('work_interval_minutes', 50),
                    self.config_manager.get('break_interval_minutes', 10)
                )
                
                self.alert_manager.enable_alerts(
                    break_alerts=self.config_manager.get('alerts.enable_break_reminders', True),
                    fatigue_alerts=self.config_manager.get('alerts.enable_fatigue_alerts', True)
                )
                self.alert_manager.update_cooldown(
                    self.config_manager.get('alerts.alert_cooldown_minutes', 10)
                )
            
            logger.info("Settings updated")
            if not self.is_monitoring:
                # Only show this message if we didn't show eye tracking messages
                messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            logger.error(f"Error applying settings: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error applying settings: {str(e)}")

    
    def _on_close(self):
        """Handle window close"""
        if self.is_monitoring:
            if messagebox.askyesno("Confirm Exit", "A session is active. Do you want to end it and exit?"):
                self._stop_session()
                self.destroy()
        else:
            self.destroy()
