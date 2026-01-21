"""Main application window"""
import customtkinter as ctk
import threading
from datetime import datetime, timedelta
from typing import Optional
from tkinter import messagebox

from src.ui.dashboard import Dashboard
from src.ui.charts import ActivityChart, FatigueChart, BlinkRateChart
from src.ui.settings_dialog import SettingsDialog
from src.ui.keyboard_handler import KeyboardHandler
from src.ui.system_tray import SystemTray
from src.ui.activities.activity_browser import ActivityBrowser
from PIL import Image, ImageTk
import os
from src.storage.config_manager import ConfigManager
from src.storage.data_manager import DataManager
from src.monitoring.input_monitor import InputMonitor
from src.monitoring.time_tracker import TimeTracker
from src.monitoring.eye_tracker import EyeTracker
from src.analysis.fatigue_analyzer import FatigueAnalyzer
from src.analysis.alert_manager import AlertManager
from src.analysis.activity_manager import ActivityManager
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
        self.geometry("1400x900")

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
        self.activity_manager = ActivityManager(data_manager=self.data_manager)

        # Initialize keyboard shortcuts and system tray
        self.keyboard_handler: Optional[KeyboardHandler] = None
        self.system_tray: Optional[SystemTray] = None

        self.current_session: Optional[Session] = None
        self.is_monitoring = False

        # Activity data for charts
        self.activity_history = []
        self.fatigue_history = []
        self.blink_history = []
        self.keystroke_history = []
        self.mouse_history = []

        # Create UI
        self._create_widgets()

        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()

        # Setup system tray (if enabled)
        if self.config_manager.get('ui.enable_system_tray', True):
            self._setup_system_tray()

        # Start update loop
        self.update_interval = self.config_manager.get(
            'ui.update_interval_ms', 1000)
        if self.eye_tracker:
            self._start_update_loop()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        logger.info("Main window initialized")

    def _create_widgets(self):
        """Create UI widgets with sidebar navigation"""

        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ===== LEFT SIDEBAR =====
        sidebar = ctk.CTkFrame(
            self,
            width=200,
            corner_radius=0,
            fg_color="#1e293b")
        sidebar.grid(row=0, column=0, sticky="nswe", padx=0, pady=0)
        sidebar.grid_propagate(False)

        # Logo/Title in sidebar
        logo_frame = ctk.CTkFrame(
            sidebar,
            fg_color="#0f172a",
            corner_radius=0,
            height=100)
        logo_frame.pack(fill="x", padx=0, pady=0)
        logo_frame.pack_propagate(False)

        # Load and display logo image
        try:
            logo_path = os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(__file__))),
                "assets",
                "logo.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((50, 50), Image.Resampling.LANCZOS)
                self.webcam_photo = Image.open("assets/webcam_placeholder.png")  # type: ignore
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ctk.CTkLabel(
                    logo_frame, image=logo_photo, text="")
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(pady=(10, 5))
            else:
                # Fallback to emoji if logo not found
                ctk.CTkLabel(
                    logo_frame,
                    text="🧠",
                    font=ctk.CTkFont(size=32)
                ).pack(pady=(10, 0))
        except Exception as e:
            logger.error(f"Failed to load logo: {e}")
            # Fallback to emoji
            ctk.CTkLabel(
                logo_frame,
                text="🧠",
                font=ctk.CTkFont(size=32)
            ).pack(pady=(10, 0))

        ctk.CTkLabel(
            logo_frame,
            text="Fatigue Tracker",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3b82f6"
        ).pack(pady=(0, 5))

        # Separator
        ctk.CTkFrame(
            sidebar,
            height=2,
            fg_color="#3b82f6").pack(
            fill="x",
            pady=(
                0,
                20))

        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("📊", "Dashboard"),
            ("📈", "Analytics"),
            ("⚡", "Activities"),
            ("🎯", "Statistics"),
            ("⚙️", "Settings")
        ]

        for icon, name in nav_items:
            btn = ctk.CTkButton(
                sidebar,
                text=f"{icon}  {name}",
                command=lambda n=name: self._switch_page(n),
                width=180,
                height=45,
                corner_radius=10,
                fg_color="transparent",
                hover_color="#334155",
                anchor="w",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#94a3b8"
            )
            btn.pack(padx=10, pady=5)
            self.nav_buttons[name] = btn

        # Active page indicator
        self.current_page = "Dashboard"

        # ===== MAIN CONTENT AREA =====
        main_container = ctk.CTkFrame(
            self, fg_color="#0f172a", corner_radius=0)
        main_container.grid(row=0, column=1, sticky="nsew")
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(
            2, weight=1)  # Content row now at index 2

        # Top bar with gradient effect
        top_bar = ctk.CTkFrame(
            main_container,
            height=80,
            corner_radius=0,
            fg_color="#1e293b")
        top_bar.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        top_bar.grid_propagate(False)
        top_bar.grid_columnconfigure(0, weight=1)

        # Page title
        self.page_title = ctk.CTkLabel(
            top_bar,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#3b82f6"
        )
        self.page_title.pack(side="left", padx=30, pady=20)

        # Control buttons with vibrant colors
        button_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        button_frame.pack(side="right", padx=30)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="▶ Start",
            command=self._start_session,
            width=130,
            height=45,
            corner_radius=14,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            text_color="#ffffff",
            font=ctk.CTkFont(size=14, weight="bold"),
            border_width=2,
            border_color="#60a5fa"
        )
        self.start_button.pack(side="left", padx=5)

        self.break_button = ctk.CTkButton(
            button_frame,
            text="☕ Break",
            command=self._toggle_break,
            width=130,
            height=45,
            corner_radius=14,
            state="disabled",
            fg_color="#f97316",
            hover_color="#ea580c",
            text_color="#ffffff",
            font=ctk.CTkFont(size=14, weight="bold"),
            border_width=2,
            border_color="#fb923c"
        )
        self.break_button.pack(side="left", padx=5)

        self.stop_button = ctk.CTkButton(
            button_frame,
            text="■ Stop",
            command=self._stop_session,
            width=130,
            height=45,
            corner_radius=14,
            state="disabled",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            text_color="#ffffff",
            font=ctk.CTkFont(size=14, weight="bold"),
            border_width=2,
            border_color="#f87171"
        )
        self.stop_button.pack(side="left", padx=5)

        # Breadcrumb navigation bar (file explorer style)
        breadcrumb_bar = ctk.CTkFrame(
            main_container,
            height=35,
            corner_radius=0,
            fg_color="#1e293b")
        breadcrumb_bar.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        breadcrumb_bar.grid_propagate(False)

        # Breadcrumb path
        self.breadcrumb_frame = ctk.CTkFrame(
            breadcrumb_bar, fg_color="transparent")
        self.breadcrumb_frame.pack(side="left", padx=15, pady=5)

        # Clickable Home breadcrumb
        breadcrumb_home = ctk.CTkLabel(
            self.breadcrumb_frame,
            text="Home",
            font=ctk.CTkFont(size=12, underline=True),
            text_color="#3b82f6",
            cursor="hand2"
        )
        breadcrumb_home.pack(side="left")
        breadcrumb_home.bind("<Button-1>",
                             lambda e: self._switch_page("Dashboard"))
        breadcrumb_home.bind(
            "<Enter>",
            lambda e: breadcrumb_home.configure(
                text_color="#2563eb"))
        breadcrumb_home.bind(
            "<Leave>",
            lambda e: breadcrumb_home.configure(
                text_color="#3b82f6"))

        # Separator
        ctk.CTkLabel(
            self.breadcrumb_frame,
            text=" > ",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        ).pack(side="left")

        # Current page label
        self.breadcrumb_current = ctk.CTkLabel(
            self.breadcrumb_frame,
            text="Dashboard",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        self.breadcrumb_current.pack(side="left")

        # Content area with pages - fill all available space (no padding for
        # edge-to-edge design)
        self.content_frame = ctk.CTkFrame(
            main_container, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Create all pages
        self.pages = {}
        self._create_dashboard_page()
        self._create_analytics_page()
        self._create_activities_page()
        self._create_statistics_page()
        self._create_settings_page()

        # Show initial page
        self._switch_page("Dashboard")

    def _create_dashboard_page(self):
        """Create Dashboard page"""
        page = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=1)

        # Dashboard metrics with clickable cards that navigate to Analytics
        self.dashboard = Dashboard(
            page, on_navigate=lambda: self._switch_page("Analytics"))
        self.dashboard.grid(row=0, column=0, sticky="nsew")

        self.pages["Dashboard"] = page

    def _create_analytics_page(self):
        """Create Analytics page with charts - 2x2 grid + full-width blink chart"""
        page = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        page.grid_columnconfigure((0, 1), weight=1)
        page.grid_rowconfigure(0, weight=1)  # Top row
        page.grid_rowconfigure(1, weight=1)  # Middle row
        page.grid_rowconfigure(2, weight=1)  # Bottom row for blink

        # Activity chart (top left)
        activity_container = ctk.CTkFrame(
            page,
            fg_color="#1e293b",
            corner_radius=14,
            border_width=1,
            border_color="#334155")
        activity_container.grid(
            row=0, column=0, sticky="nsew", padx=(
                0, 4), pady=(
                0, 4))
        activity_container.grid_columnconfigure(0, weight=1)
        activity_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            activity_container,
            text="📊 Activity Rate Over Time",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3b82f6"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))

        chart_frame = ctk.CTkFrame(activity_container, fg_color="transparent")
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.activity_chart = ActivityChart(chart_frame)
        self.activity_chart.pack(fill="both", expand=True)

        # Fatigue chart (top right)
        fatigue_container = ctk.CTkFrame(
            page,
            fg_color="#1e293b",
            corner_radius=14,
            border_width=1,
            border_color="#334155")
        fatigue_container.grid(
            row=0, column=1, sticky="nsew", padx=(
                4, 0), pady=(
                0, 4))
        fatigue_container.grid_columnconfigure(0, weight=1)
        fatigue_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            fatigue_container,
            text="🎯 Fatigue Score Trend",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f97316"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))

        chart_frame = ctk.CTkFrame(fatigue_container, fg_color="transparent")
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.fatigue_chart = FatigueChart(chart_frame)
        self.fatigue_chart.pack(fill="both", expand=True)

        # Keystroke chart (bottom left)
        keystroke_container = ctk.CTkFrame(
            page,
            fg_color="#1e293b",
            corner_radius=14,
            border_width=1,
            border_color="#334155")
        keystroke_container.grid(
            row=1, column=0, sticky="nsew", padx=(
                0, 4), pady=(
                4, 0))
        keystroke_container.grid_columnconfigure(0, weight=1)
        keystroke_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            keystroke_container,
            text="⌨️ Keystroke Activity",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#10b981"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))

        chart_frame = ctk.CTkFrame(keystroke_container, fg_color="transparent")
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.keystroke_chart = ActivityChart(chart_frame)
        self.keystroke_chart.pack(fill="both", expand=True)

        # Mouse click chart (bottom right)
        mouse_container = ctk.CTkFrame(
            page,
            fg_color="#1e293b",
            corner_radius=14,
            border_width=1,
            border_color="#334155")
        mouse_container.grid(
            row=1, column=1, sticky="nsew", padx=(
                4, 0), pady=(
                4, 0))
        mouse_container.grid_columnconfigure(0, weight=1)
        mouse_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            mouse_container,
            text="🖱️ Mouse Click Activity",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#10b981"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))

        chart_frame = ctk.CTkFrame(mouse_container, fg_color="transparent")
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.mouse_chart = ActivityChart(chart_frame)
        self.mouse_chart.pack(fill="both", expand=True)

        # Eye Blink Rate chart (bottom, spanning full width)
        blink_container = ctk.CTkFrame(
            page,
            fg_color="#1e293b",
            corner_radius=14,
            border_width=1,
            border_color="#334155")
        blink_container.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="nsew",
            pady=(
                8,
                0))
        blink_container.grid_columnconfigure(0, weight=1)
        blink_container.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            blink_container,
            text="👁️ Eye Blink Rate (Eye Tracking)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#8b5cf6"
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))

        chart_frame = ctk.CTkFrame(blink_container, fg_color="transparent")
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.blink_chart = BlinkRateChart(chart_frame)
        self.blink_chart.pack(fill="both", expand=True)
        self.blink_chart_container = blink_container

        # Keep references
        self.pages["Analytics"] = page

    def _create_activities_page(self):
        """Create Activities page with refresh activity browser"""
        # Activity browser widget placed directly (no wrapper needed)
        self.activity_browser = ActivityBrowser(self.content_frame)
        self.activity_browser.grid(row=0, column=0, sticky="nsew")

        # Store reference for page switching
        self.pages["Activities"] = self.activity_browser

    def _create_statistics_page(self):
        """Create Statistics page"""
        page = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(0, weight=1)

        # Placeholder for statistics
        placeholder = ctk.CTkFrame(
            page,
            fg_color="#334155",
            corner_radius=12,
            border_width=1,
            border_color="#475569")
        placeholder.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(
            placeholder,
            text="🎯 Statistics Dashboard",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#8b5cf6"
        ).pack(pady=30)

        ctk.CTkLabel(
            placeholder,
            text="Coming Soon: Weekly/Monthly Statistics, Productivity Analytics, and More!",
            font=ctk.CTkFont(
                size=14),
            text_color="#888888").pack()

        self.pages["Statistics"] = page

    def _create_settings_page(self):
        """Create Settings page with inline settings"""
        page = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        page.grid_columnconfigure((0, 1, 2), weight=1)
        page.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Title at top
        title_frame = ctk.CTkFrame(page, fg_color="transparent")
        title_frame.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=10,
            pady=(
                10,
                5))

        ctk.CTkLabel(
            title_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#f97316"
        ).pack(side="left", padx=10)

        # Work Interval Section (top left)
        work_section = ctk.CTkFrame(
            page,
            fg_color="#334155",
            corner_radius=10,
            border_width=1,
            border_color="#475569")
        work_section.grid(
            row=1, column=0, sticky="nsew", padx=(
                5, 3), pady=(
                2, 2))

        ctk.CTkLabel(
            work_section,
            text="Work Interval",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.work_interval_var = ctk.StringVar(
            value=str(
                self.config_manager.get(
                    'work_interval_minutes',
                    50)))
        work_frame = ctk.CTkFrame(work_section, fg_color="transparent")
        work_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(work_frame, text="Minutes:").pack(side="left")
        self.work_entry = ctk.CTkEntry(
            work_frame,
            textvariable=self.work_interval_var,
            width=100,
            state="normal",
            justify="center"
        )
        self.work_entry.pack(side="left", padx=(10, 0))

        # Break Interval Section (top middle)
        break_section = ctk.CTkFrame(
            page,
            fg_color="#334155",
            corner_radius=10,
            border_width=1,
            border_color="#475569")
        break_section.grid(row=1, column=1, sticky="nsew", padx=3, pady=(2, 2))

        ctk.CTkLabel(
            break_section,
            text="Break Interval",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.break_interval_var = ctk.StringVar(
            value=str(
                self.config_manager.get(
                    'break_interval_minutes',
                    10)))
        break_frame = ctk.CTkFrame(break_section, fg_color="transparent")
        break_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(break_frame, text="Minutes:").pack(side="left")
        self.break_entry = ctk.CTkEntry(
            break_frame,
            textvariable=self.break_interval_var,
            width=100,
            state="normal",
            justify="center"
        )
        self.break_entry.pack(side="left", padx=(10, 0))

        # Monitoring Section (top right)
        monitor_section = ctk.CTkFrame(
            page,
            fg_color="#334155",
            corner_radius=10,
            border_width=1,
            border_color="#475569")
        monitor_section.grid(
            row=1, column=2, sticky="nsew", padx=(
                3, 5), pady=(
                2, 2))

        ctk.CTkLabel(
            monitor_section,
            text="Activity Monitoring",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.track_keyboard_var = ctk.BooleanVar(
            value=self.config_manager.get(
                'monitoring.track_keyboard', True))
        ctk.CTkCheckBox(
            monitor_section,
            text="Track Keyboard",
            variable=self.track_keyboard_var
        ).pack(anchor="w", padx=15, pady=5)

        self.track_mouse_clicks_var = ctk.BooleanVar(
            value=self.config_manager.get(
                'monitoring.track_mouse_clicks', True))
        ctk.CTkCheckBox(
            monitor_section,
            text="Track Mouse Clicks",
            variable=self.track_mouse_clicks_var
        ).pack(anchor="w", padx=15, pady=5)

        self.track_mouse_movement_var = ctk.BooleanVar(
            value=self.config_manager.get(
                'monitoring.track_mouse_movement', False))
        ctk.CTkCheckBox(
            monitor_section,
            text="Track Mouse Movement",
            variable=self.track_mouse_movement_var
        ).pack(anchor="w", padx=15, pady=(5, 15))

        # Alerts Section (middle left)
        alerts_section = ctk.CTkFrame(
            page,
            fg_color="#334155",
            corner_radius=10,
            border_width=1,
            border_color="#475569")
        alerts_section.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=(
                5,
                3),
            pady=2)

        ctk.CTkLabel(
            alerts_section,
            text="Alerts & Notifications",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.break_alerts_var = ctk.BooleanVar(
            value=self.config_manager.get(
                'alerts.enable_break_reminders', True))
        ctk.CTkCheckBox(
            alerts_section,
            text="Enable Break Reminders",
            variable=self.break_alerts_var
        ).pack(anchor="w", padx=15, pady=5)

        self.fatigue_alerts_var = ctk.BooleanVar(
            value=self.config_manager.get(
                'alerts.enable_fatigue_alerts', True))
        ctk.CTkCheckBox(
            alerts_section,
            text="Enable Fatigue Alerts",
            variable=self.fatigue_alerts_var
        ).pack(anchor="w", padx=15, pady=5)

        self.alert_cooldown_var = ctk.StringVar(
            value=str(
                self.config_manager.get(
                    'alerts.alert_cooldown_minutes',
                    10)))
        cooldown_frame = ctk.CTkFrame(alerts_section, fg_color="transparent")
        cooldown_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkLabel(
            cooldown_frame,
            text="Alert Cooldown (minutes):").pack(
            side="left")
        self.cooldown_entry = ctk.CTkEntry(
            cooldown_frame,
            textvariable=self.alert_cooldown_var,
            width=100,
            state="normal",
            justify="center"
        )
        self.cooldown_entry.pack(side="left", padx=(10, 0))

        # Eye Tracking Section (middle middle)
        eye_section = ctk.CTkFrame(
            page,
            fg_color="#334155",
            corner_radius=10,
            border_width=1,
            border_color="#475569")
        eye_section.grid(row=2, column=1, sticky="nsew", padx=3, pady=2)

        ctk.CTkLabel(
            eye_section,
            text="👁️ Eye Tracking (Optional)",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        privacy_label = ctk.CTkLabel(
            eye_section,
            text="⚠️ Privacy: Eye tracking uses your webcam to detect blinks.\nNo video is recorded or stored - only blink counts are tracked.",
            font=ctk.CTkFont(
                size=10),
            text_color="#FFC107",
            justify="left")
        privacy_label.pack(anchor="w", padx=15, pady=5)

        self.eye_tracking_var = ctk.BooleanVar(
            value=self.config_manager.get(
                'eye_tracking.enabled', False))
        ctk.CTkCheckBox(
            eye_section,
            text="Enable Eye Tracking (Blink Rate Monitoring)",
            variable=self.eye_tracking_var,
            command=self._on_eye_tracking_toggle
        ).pack(anchor="w", padx=15, pady=(10, 15))

        # UI Theme Section (middle right)
        theme_section = ctk.CTkFrame(
            page,
            fg_color="#334155",
            corner_radius=10,
            border_width=1,
            border_color="#475569")
        theme_section.grid(row=2, column=2, sticky="nsew", padx=(3, 5), pady=2)

        ctk.CTkLabel(
            theme_section,
            text="Appearance",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.theme_var = ctk.StringVar(
            value=self.config_manager.get(
                'ui.theme', 'dark'))
        theme_frame = ctk.CTkFrame(theme_section, fg_color="transparent")
        theme_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(theme_frame, text="Theme:").pack(side="left")
        ctk.CTkOptionMenu(
            theme_frame,
            variable=self.theme_var,
            values=["dark", "light"]
        ).pack(side="left", padx=(10, 0))

        # Save/Reset Buttons (bottom, centered)
        button_frame = ctk.CTkFrame(page, fg_color="transparent")
        button_frame.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=10,
            pady=(
                5,
                5))

        ctk.CTkButton(
            button_frame,
            text="💾 Save Settings",
            command=self._save_inline_settings,
            width=150,
            height=40,
            corner_radius=10,
            fg_color="#00ff88",
            hover_color="#00cc6a",
            text_color="#000000",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="🔄 Reset to Defaults",
            command=self._reset_settings,
            width=150,
            height=40,
            corner_radius=10,
            fg_color="transparent",
            border_width=2,
            border_color="#ff4757",
            text_color="#ff4757",
            hover_color="#ff4757",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        self.pages["Settings"] = page

    def _create_about_page(self):
        """Create modern About page with financial dashboard styling"""
        # Wrapper frame to force full width
        wrapper = ctk.CTkFrame(self.content_frame, fg_color="#2d2d2d")
        wrapper.grid_columnconfigure(0, weight=1)
        wrapper.grid_rowconfigure(0, weight=1)

        # Scrollable page - fills the wrapper completely
        page = ctk.CTkScrollableFrame(
            wrapper,
            fg_color="#2d2d2d",
            scrollbar_button_color="#4a4a4a",
            scrollbar_button_hover_color="#5a5a5a"
        )
        page.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        page.grid_columnconfigure(0, weight=1)

        # Header section with modern gradient-style card
        header_frame = ctk.CTkFrame(
            page,
            fg_color="#2d3548",
            corner_radius=16,
            border_width=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 25))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="🧠",
            font=ctk.CTkFont(size=60)
        ).grid(row=0, column=0, pady=(30, 10))

        ctk.CTkLabel(
            header_frame,
            text="Cognitive Fatigue Tracker",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#4ade80"  # Green accent like reference
        ).grid(row=1, column=0, pady=(0, 5))

        ctk.CTkLabel(
            header_frame,
            text="Advanced Real-Time Cognitive Performance Monitoring",
            font=ctk.CTkFont(size=14),
            text_color="#9ca3af"  # Muted gray
        ).grid(row=2, column=0, pady=(0, 30))

        # Version info card
        version_frame = ctk.CTkFrame(
            page,
            fg_color="#2d3548",
            corner_radius=16,
            border_width=0)
        version_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            version_frame,
            text="📌 Version Information",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4ade80",  # Green accent
            anchor="w"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        version_text = "Version: 1.0.0\nPython: 3.11+\nBuild: Production"
        ctk.CTkLabel(
            version_frame,
            text=version_text,
            font=ctk.CTkFont(size=13),
            anchor="w",
            justify="left"
        ).pack(anchor="w", padx=25, pady=(5, 20))

        # Features section
        features_frame = ctk.CTkFrame(
            page,
            fg_color="#2d3548",
            corner_radius=16,
            border_width=0)
        features_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=(
                0,
                20))

        ctk.CTkLabel(
            features_frame,
            text="✨ Key Features",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4ade80",
            anchor="w"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        features = [
            "📊 Real-time cognitive fatigue monitoring",
            "🖱️ Smart activity tracking (keyboard & mouse)",
            "👁️ Optional eye tracking with blink rate analysis",
            "🤖 Machine Learning predictions with personalization",
            "📈 Beautiful data visualizations and analytics",
            "⚠️ Intelligent break reminders and fatigue alerts",
            "🔔 Desktop notifications with sound effects",
            "💾 Session history and data export",
            "⚙️ Fully customizable settings",
            "🌙 Dark/Light theme support"
        ]

        for feature in features:
            ctk.CTkLabel(
                features_frame,
                text=feature,
                font=ctk.CTkFont(size=13),
                anchor="w"
            ).pack(anchor="w", padx=25, pady=3)

        ctk.CTkLabel(features_frame, text="").pack(pady=5)  # Spacing

        # Technology stack
        tech_frame = ctk.CTkFrame(
            page,
            fg_color="#334155",
            corner_radius=10,
            border_width=1,
            border_color="#475569")
        tech_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            tech_frame,
            text="🔧 Technology Stack",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        # Technology stack with clickable links
        import webbrowser

        tech_links = [
            ("CustomTkinter - Modern UI framework", "https://github.com/TomSchimansky/CustomTkinter"),
            ("MediaPipe - Eye tracking and facial landmarks", "https://google.github.io/mediapipe/"),
            ("Scikit-learn - Machine learning models", "https://scikit-learn.org/"),
            ("Matplotlib - Data visualization", "https://matplotlib.org/"),
            ("SQLite - Data persistence", "https://www.sqlite.org/"),
            ("Pynput - Input monitoring", "https://pynput.readthedocs.io/"),
            ("Pystray - System tray integration", "https://pystray.readthedocs.io/")
        ]

        for tech_name, url in tech_links:
            link_frame = ctk.CTkFrame(tech_frame, fg_color="transparent")
            link_frame.pack(anchor="w", padx=25, pady=2)

            # Bullet point
            ctk.CTkLabel(
                link_frame,
                text="•",
                font=ctk.CTkFont(size=13),
                anchor="w"
            ).pack(side="left", padx=(0, 5))

            # Clickable link
            link_label = ctk.CTkLabel(
                link_frame,
                text=tech_name,
                font=ctk.CTkFont(size=13, underline=True),
                text_color="#3b82f6",
                anchor="w",
                cursor="hand2"
            )
            link_label.pack(side="left")

            # Make it clickable
            link_label.bind(
                "<Button-1>",
                lambda e,
                link=url: webbrowser.open(link))
            # Hover effect
            link_label.bind(
                "<Enter>",
                lambda e,
                lbl=link_label: lbl.configure(
                    text_color="#2563eb"))
            link_label.bind(
                "<Leave>",
                lambda e,
                lbl=link_label: lbl.configure(
                    text_color="#3b82f6"))

        ctk.CTkLabel(tech_frame, text="").pack(pady=5)  # Spacing

        # Privacy & Data
        privacy_frame = ctk.CTkFrame(
            page,
            fg_color="#334155",
            corner_radius=10,
            border_width=1,
            border_color="#475569")
        privacy_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            privacy_frame,
            text="🔒 Privacy & Data",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        privacy_text = (
            "All data is stored locally on your device. No information is sent to external servers. \n\n"
            "Eye tracking (when enabled) uses your webcam to detect blinks only. No video is \n"
            "recorded, stored, or transmitted. Only blink counts are tracked for fatigue analysis. \n\n"
            "You have full control over all monitoring features and can disable them at any time.")
        ctk.CTkLabel(
            privacy_frame,
            text=privacy_text,
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
            wraplength=700
        ).pack(anchor="w", padx=25, pady=(0, 15))

        # Credits & License
        credits_frame = ctk.CTkFrame(
            page,
            fg_color="#334155",
            corner_radius=10,
            border_width=1,
            border_color="#475569")
        credits_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            credits_frame,
            text="👥 Credits",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        ).pack(anchor="w", padx=20, pady=(15, 10))

        credits_text = (
            "Developed with ❤️ for healthier work habits\n\n"
            "Special thanks to the open-source community for the amazing tools and libraries \n"
            "that made this project possible.")
        ctk.CTkLabel(
            credits_frame,
            text=credits_text,
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
            wraplength=700
        ).pack(anchor="w", padx=25, pady=(0, 15))

        # Footer
        footer_frame = ctk.CTkFrame(page, fg_color="transparent")
        footer_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(15, 30))

        ctk.CTkLabel(
            footer_frame,
            text="Made to help you work smarter, not harder. 🚀",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3b82f6"
        ).pack(pady=10)

        self.pages["About"] = wrapper

    def _switch_page(self, page_name):
        """Switch between pages"""
        # Hide all pages
        for page in self.pages.values():
            page.grid_remove()

        # Show selected page
        if page_name in self.pages:
            self.pages[page_name].grid()
            self.current_page = page_name

            # Update page title and colors
            icons = {
                "Dashboard": "📊",
                "Analytics": "📈",
                "Statistics": "🎯",
                "Settings": "⚙️",
                "About": "ℹ️"}
            colors = {
                "Dashboard": "#3b82f6",
                "Analytics": "#14b8a6",
                "Statistics": "#8b5cf6",
                "Settings": "#f97316",
                "About": "#3b82f6"}

            self.page_title.configure(
                text=f"{icons.get(page_name, '📄')} {page_name}",
                text_color=colors.get(page_name, "#ffffff")
            )

            # Update breadcrumb current page
            self.breadcrumb_current.configure(text=page_name)

            # Update nav button styles
            for name, btn in self.nav_buttons.items():
                if name == page_name:
                    btn.configure(
                        fg_color=colors.get(page_name, "#3b82f6"),
                        text_color="#ffffff",
                        border_width=2,
                        border_color="#60a5fa"
                    )
                else:
                    btn.configure(
                        fg_color="transparent",
                        text_color="#94a3b8",
                        border_width=0
                    )

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
            on_activity=self._on_activity, track_keyboard=config.get(
                'monitoring.track_keyboard', True), track_mouse_clicks=config.get(
                'monitoring.track_mouse_clicks', True), track_mouse_movement=config.get(
                'monitoring.track_mouse_movement', False))

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
        self.alert_manager.update_cooldown(
            config.get('alerts.alert_cooldown_minutes', 10))

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
            self.break_button.configure(text="☕ Break")
            logger.info("Ended break")
        else:
            self.time_tracker.start_break()
            self.break_button.configure(text="⏸️ End Break")
            logger.info("Started break")

            # Navigate to Activities page to help user choose a refresh
            # activity
            self._switch_page("Activities")

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
                        logger.warning(
                            "Camera became unavailable, disabling eye tracker")
                        self.eye_tracker.stop()
                        self.eye_tracker = None
                        # Show notification to user
                        self.after(
                            0,
                            lambda: messagebox.showwarning(
                                "Camera Disconnected",
                                "Eye tracking stopped: Camera is no longer available."))
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
                    time_since_break_minutes=(
                        work_time.total_seconds() / 60) if not is_on_break else 0,
                    is_on_break=is_on_break,
                    blink_rate=blink_rate)
            except Exception as e:
                logger.error(
                    f"Error calculating fatigue score: {e}",
                    exc_info=True)
                # Use a safe default score
                from src.models.fatigue_score import FatigueScore
                fatigue_score = FatigueScore(score=0.0)

            # Save fatigue score periodically
            try:
                if self.current_session and len(
                        self.fatigue_analyzer.history) % 10 == 0:
                    self.data_manager.save_fatigue_score(
                        fatigue_score, self.current_session.session_id)
            except Exception as e:
                logger.error(f"Error saving fatigue score: {e}")

            # Update dashboard with error handling
            try:
                # Get keystroke and mouse counts
                keystroke_count = self.input_monitor.get_keyboard_count() if self.input_monitor else 0
                mouse_count = self.input_monitor.get_mouse_click_count() if self.input_monitor else 0

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
                    eye_tracking_enabled=self.eye_tracker is not None,
                    keystroke_count=keystroke_count,
                    mouse_count=mouse_count
                )

            except Exception as e:
                logger.error(f"Error updating dashboard: {e}")

            # Update charts with error handling
            try:
                now = datetime.now()

                # Activity chart - last hour
                self.activity_history.append((now, activity_rate))
                cutoff = now - timedelta(minutes=60)
                self.activity_history = [
                    (t, v) for t, v in self.activity_history if t >= cutoff]
                self.activity_chart.update_data(self.activity_history)
            except Exception as e:
                logger.error(f"Error updating activity chart: {e}")

            # Fatigue chart - last hour
            try:
                self.fatigue_history.append((now, fatigue_score.score))
                self.fatigue_history = [
                    (t, v) for t, v in self.fatigue_history if t >= cutoff]
                self.fatigue_chart.update_data(self.fatigue_history)

                # Keystroke chart - last hour
                self.keystroke_history.append((now, keystroke_count))
                self.keystroke_history = [
                    (t, v) for t, v in self.keystroke_history if t >= cutoff]
                self.keystroke_chart.update_data(self.keystroke_history)

                # Mouse click chart - last hour
                self.mouse_history.append((now, mouse_count))
                self.mouse_history = [
                    (t, v) for t, v in self.mouse_history if t >= cutoff]
                self.mouse_chart.update_data(self.mouse_history)
            except Exception as e:
                logger.error(f"Error updating fatigue chart: {e}")

            # Blink rate chart (if eye tracking enabled)
            try:
                if self.eye_tracker and blink_rate > 0:
                    self.blink_history.append((now, blink_rate))
                    self.blink_history = [
                        (t, v) for t, v in self.blink_history if t >= cutoff]
                    # Create chart if not exists
                    if self.blink_chart is None:
                        self._create_blink_chart()
                    if self.blink_chart:
                        self.blink_chart.update_data(self.blink_history)
            except Exception as e:
                logger.error(f"Error updating blink chart: {e}")

            # Check alerts with error handling
            try:
                self.alert_manager.check_break_reminder(
                    time_until_break, is_on_break)
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
            self.blink_chart_container.grid(
                row=2,
                column=0,
                columnspan=2,
                sticky="nsew",
                pady=(
                    10,
                    0))

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
        dialog = SettingsDialog(
            self,
            self.config_manager,
            on_save=self._on_settings_saved)

    def _on_settings_saved(self):
        """Handle settings save"""
        try:
            # Apply theme change
            theme = self.config_manager.get('ui.theme', 'dark')
            ctk.set_appearance_mode(theme)

            # Handle eye tracking setting change
            eye_tracking_enabled = self.config_manager.get(
                'eye_tracking.enabled', False)

            # If monitoring is active, dynamically start/stop eye tracking
            if self.is_monitoring:
                if eye_tracking_enabled and not self.eye_tracker:
                    # User enabled eye tracking - start it
                    try:
                        self.eye_tracker = EyeTracker(
                            camera_index=self.config_manager.get(
                                'eye_tracking.camera_index', 0))
                        if self.eye_tracker.start():
                            logger.info("Eye tracking enabled during session")
                            messagebox.showinfo(
                                "Eye Tracking", "Eye tracking enabled! Camera is now active.")
                        else:
                            logger.warning("Eye tracking failed to start")
                            self.eye_tracker = None
                            messagebox.showwarning(
                                "Eye Tracking", "Could not start eye tracking. Check camera availability.")
                    except Exception as e:
                        logger.error(f"Failed to enable eye tracker: {e}")
                        self.eye_tracker = None
                        messagebox.showerror(
                            "Eye Tracking", f"Error enabling eye tracking: {str(e)}")

                elif not eye_tracking_enabled and self.eye_tracker:
                    # User disabled eye tracking - stop it
                    try:
                        self.eye_tracker.stop()
                        self.eye_tracker = None
                        logger.info("Eye tracking disabled during session")
                        messagebox.showinfo(
                            "Eye Tracking", "Eye tracking disabled. Camera stopped.")
                    except Exception as e:
                        logger.error(f"Error disabling eye tracker: {e}")

            # Update components if monitoring
            if self.is_monitoring and self.time_tracker:
                self.time_tracker.update_intervals(
                    self.config_manager.get('work_interval_minutes', 50),
                    self.config_manager.get('break_interval_minutes', 10)
                )

                self.alert_manager.enable_alerts(
                    break_alerts=self.config_manager.get(
                        'alerts.enable_break_reminders', True), fatigue_alerts=self.config_manager.get(
                        'alerts.enable_fatigue_alerts', True))
                self.alert_manager.update_cooldown(
                    self.config_manager.get(
                        'alerts.alert_cooldown_minutes', 10))

            logger.info("Settings updated")
            if not self.is_monitoring:
                # Only show this message if we didn't show eye tracking
                # messages
                messagebox.showinfo("Settings", "Settings saved successfully!")
        except Exception as e:
            logger.error(f"Error applying settings: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error applying settings: {str(e)}")

    def _save_inline_settings(self):
        """Save settings from inline settings page"""
        try:
            # Parse and validate inputs
            work_minutes = int(self.work_interval_var.get())
            break_minutes = int(self.break_interval_var.get())
            cooldown_minutes = int(self.alert_cooldown_var.get())

            if work_minutes < 1 or break_minutes < 1 or cooldown_minutes < 1:
                raise ValueError("Values must be positive")

            # Update config
            self.config_manager.set('work_interval_minutes', work_minutes)
            self.config_manager.set('break_interval_minutes', break_minutes)

            self.config_manager.set(
                'monitoring.track_keyboard',
                self.track_keyboard_var.get())
            self.config_manager.set(
                'monitoring.track_mouse_clicks',
                self.track_mouse_clicks_var.get())
            self.config_manager.set(
                'monitoring.track_mouse_movement',
                self.track_mouse_movement_var.get())

            self.config_manager.set(
                'alerts.enable_break_reminders',
                self.break_alerts_var.get())
            self.config_manager.set(
                'alerts.enable_fatigue_alerts',
                self.fatigue_alerts_var.get())
            self.config_manager.set(
                'alerts.alert_cooldown_minutes',
                cooldown_minutes)

            self.config_manager.set('ui.theme', self.theme_var.get())

            self.config_manager.set(
                'eye_tracking.enabled',
                self.eye_tracking_var.get())

            # Save to file
            self.config_manager.save()

            # Apply settings
            self._on_settings_saved()

        except ValueError as e:
            messagebox.showerror(
                "Invalid Input",
                "Please enter valid positive numbers for all numeric fields.")
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")

    def _reset_settings(self):
        """Reset settings to defaults"""
        if messagebox.askyesno(
            "Reset Settings",
                "Are you sure you want to reset all settings to defaults?"):
            try:
                # Reset to defaults
                self.work_interval_var.set("50")
                self.break_interval_var.set("10")
                self.track_keyboard_var.set(True)
                self.track_mouse_clicks_var.set(True)
                self.track_mouse_movement_var.set(False)
                self.break_alerts_var.set(True)
                self.fatigue_alerts_var.set(True)
                self.alert_cooldown_var.set("10")
                self.eye_tracking_var.set(False)
                self.theme_var.set("dark")

                messagebox.showinfo(
                    "Settings Reset",
                    "Settings have been reset to defaults. Click Save to apply.")
            except Exception as e:
                logger.error(f"Error resetting settings: {e}")
                messagebox.showerror(
                    "Error", f"Error resetting settings: {str(e)}")

    def _on_eye_tracking_toggle(self):
        """Handle eye tracking toggle with consent"""
        if self.eye_tracking_var.get():
            # Show consent dialog
            consent = messagebox.askyesno(
                "Eye Tracking Privacy",
                "Eye tracking will use your webcam to monitor blink rate.\n\n"
                "Privacy Protection:\n"
                "• No video is recorded or saved\n"
                "• Only blink counts are tracked\n"
                "• All processing is done locally\n"
                "• You can disable this anytime\n\n"
                "Do you consent to enable eye tracking?",
                icon='warning'
            )
            if not consent:
                self.eye_tracking_var.set(False)

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.keyboard_handler = KeyboardHandler(self)

        # Register shortcuts
        self.keyboard_handler.register_shortcut(
            "<control-b>",
            self._toggle_break,
            "Take/End Break"
        )
        self.keyboard_handler.register_shortcut(
            "<control-s>",
            self._open_settings,
            "Open Settings"
        )
        self.keyboard_handler.register_shortcut(
            "<control-q>",
            self._on_close,
            "Quit Application"
        )
        self.keyboard_handler.register_shortcut(
            "<f1>",
            self.keyboard_handler.show_shortcuts_dialog,
            "Show Keyboard Shortcuts"
        )

        logger.info("Keyboard shortcuts configured")

    def _setup_system_tray(self):
        """Setup system tray icon"""
        try:
            self.system_tray = SystemTray()

            # Set callbacks
            self.system_tray.set_callback('show', self._show_window)
            self.system_tray.set_callback('hide', self._hide_to_tray)
            self.system_tray.set_callback('start_session', self._start_session)
            self.system_tray.set_callback('stop_session', self._stop_session)
            self.system_tray.set_callback('take_break', self._toggle_break)
            self.system_tray.set_callback('settings', self._open_settings)
            self.system_tray.set_callback('quit', self._quit_app)

            # Start tray
            self.system_tray.start()
            logger.info("System tray configured")
        except Exception as e:
            logger.error(f"Failed to setup system tray: {e}")
            self.system_tray = None

    def _show_window(self):
        """Show main window from tray"""
        self.deiconify()
        self.lift()
        self.focus_force()

    def _hide_to_tray(self):
        """Hide window to system tray"""
        if self.system_tray:
            self.withdraw()
            self.system_tray.show_notification(
                "Minimized to Tray",
                "Cognitive Fatigue Tracker is still running in the background"
            )

    def _quit_app(self):
        """Quit the application"""
        if self.system_tray:
            self.system_tray.stop()
        self.destroy()

    def _on_close(self):
        """Handle window close"""
        # Normal close behavior - no minimize to tray
        if self.is_monitoring:
            if messagebox.askyesno(
                "Confirm Exit",
                    "A session is active. Do you want to end it and exit?"):
                self._stop_session()
                self._quit_app()
        else:
            self._quit_app()
