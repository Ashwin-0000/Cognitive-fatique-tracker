"""Settings dialog for configuration"""
import customtkinter as ctk
from typing import Callable, Optional


class SettingsDialog(ctk.CTkToplevel):
    """Settings configuration dialog"""

    def __init__(
            self,
            master,
            config_manager,
            on_save: Optional[Callable] = None):
        super().__init__(master)

        self.config_manager = config_manager
        self.on_save = on_save

        # Window configuration
        self.title("Settings")
        self.geometry("500x600")
        self.resizable(False, False)

        # Make modal
        self.transient(master)
        self.grab_set()

        self._create_widgets()
        self._load_current_settings()

    def _create_widgets(self):
        """Create settings widgets"""

        # Main container
        container = ctk.CTkScrollableFrame(self)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Work Interval Section
        work_section = ctk.CTkFrame(container)
        work_section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            work_section,
            text="Work Interval",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.work_interval_var = ctk.StringVar(value="50")
        work_frame = ctk.CTkFrame(work_section, fg_color="transparent")
        work_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(work_frame, text="Minutes:").pack(side="left")
        ctk.CTkEntry(
            work_frame,
            textvariable=self.work_interval_var,
            width=100
        ).pack(side="left", padx=(10, 0))

        # Break Interval Section
        break_section = ctk.CTkFrame(container)
        break_section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            break_section,
            text="Break Interval",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.break_interval_var = ctk.StringVar(value="10")
        break_frame = ctk.CTkFrame(break_section, fg_color="transparent")
        break_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(break_frame, text="Minutes:").pack(side="left")
        ctk.CTkEntry(
            break_frame,
            textvariable=self.break_interval_var,
            width=100
        ).pack(side="left", padx=(10, 0))

        # Monitoring Section
        monitor_section = ctk.CTkFrame(container)
        monitor_section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            monitor_section,
            text="Activity Monitoring",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.track_keyboard_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            monitor_section,
            text="Track Keyboard",
            variable=self.track_keyboard_var
        ).pack(anchor="w", padx=15, pady=5)

        self.track_mouse_clicks_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            monitor_section,
            text="Track Mouse Clicks",
            variable=self.track_mouse_clicks_var
        ).pack(anchor="w", padx=15, pady=5)

        self.track_mouse_movement_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            monitor_section,
            text="Track Mouse Movement",
            variable=self.track_mouse_movement_var
        ).pack(anchor="w", padx=15, pady=(5, 15))

        # Alerts Section
        alerts_section = ctk.CTkFrame(container)
        alerts_section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            alerts_section,
            text="Alerts & Notifications",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.break_alerts_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            alerts_section,
            text="Enable Break Reminders",
            variable=self.break_alerts_var
        ).pack(anchor="w", padx=15, pady=5)

        self.fatigue_alerts_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            alerts_section,
            text="Enable Fatigue Alerts",
            variable=self.fatigue_alerts_var
        ).pack(anchor="w", padx=15, pady=5)

        self.alert_cooldown_var = ctk.StringVar(value="10")
        cooldown_frame = ctk.CTkFrame(alerts_section, fg_color="transparent")
        cooldown_frame.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkLabel(
            cooldown_frame,
            text="Alert Cooldown (minutes):").pack(
            side="left")
        ctk.CTkEntry(
            cooldown_frame,
            textvariable=self.alert_cooldown_var,
            width=100
        ).pack(side="left", padx=(10, 0))

        # Eye Tracking Section (NEW)
        eye_section = ctk.CTkFrame(container)
        eye_section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            eye_section,
            text="👁️ Eye Tracking (Optional)",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        # Privacy notice
        privacy_label = ctk.CTkLabel(
            eye_section,
            text="⚠️ Privacy: Eye tracking uses your webcam to detect blinks.\nNo video is recorded or stored - only blink counts are tracked.",
            font=ctk.CTkFont(
                size=10),
            text_color="#FFC107",
            justify="left")
        privacy_label.pack(anchor="w", padx=15, pady=5)

        self.eye_tracking_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            eye_section,
            text="Enable Eye Tracking (Blink Rate Monitoring)",
            variable=self.eye_tracking_var,
            command=self._on_eye_tracking_toggle
        ).pack(anchor="w", padx=15, pady=(10, 15))

        # UI Theme Section
        theme_section = ctk.CTkFrame(container)
        theme_section.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            theme_section,
            text="Appearance",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.theme_var = ctk.StringVar(value="dark")
        theme_frame = ctk.CTkFrame(theme_section, fg_color="transparent")
        theme_frame.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkLabel(theme_frame, text="Theme:").pack(side="left")
        ctk.CTkOptionMenu(
            theme_frame,
            variable=self.theme_var,
            values=["dark", "light"]
        ).pack(side="left", padx=(10, 0))

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            fg_color="transparent",
            border_width=2
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._save_settings
        ).pack(side="right")

    def _load_current_settings(self):
        """Load current settings from config manager"""
        self.work_interval_var.set(
            str(self.config_manager.get('work_interval_minutes', 50)))
        self.break_interval_var.set(
            str(self.config_manager.get('break_interval_minutes', 10)))

        self.track_keyboard_var.set(
            self.config_manager.get(
                'monitoring.track_keyboard', True))
        self.track_mouse_clicks_var.set(
            self.config_manager.get(
                'monitoring.track_mouse_clicks', True))
        self.track_mouse_movement_var.set(
            self.config_manager.get(
                'monitoring.track_mouse_movement', False))

        self.break_alerts_var.set(
            self.config_manager.get(
                'alerts.enable_break_reminders', True))
        self.fatigue_alerts_var.set(
            self.config_manager.get(
                'alerts.enable_fatigue_alerts', True))
        self.alert_cooldown_var.set(
            str(self.config_manager.get('alerts.alert_cooldown_minutes', 10)))

        self.theme_var.set(self.config_manager.get('ui.theme', 'dark'))

        self.eye_tracking_var.set(
            self.config_manager.get(
                'eye_tracking.enabled', False))

    def _on_eye_tracking_toggle(self):
        """Handle eye tracking toggle with consent"""
        if self.eye_tracking_var.get():
            # Show consent dialog
            try:
                from tkinter import messagebox
                consent = messagebox.askyesno(
                    "Eye Tracking Privacy",
                    "Eye tracking will use your webcam to monitor blink rate.\n\n"
                    "Privacy Protection:\n"
                    "• No video is recorded or saved\n"
                    "• Only blink counts are tracked\n"
                    "• All processing is done locally\n"
                    "• You can disable this anytime\n\n"
                    "Do you consent to enable eye tracking?",
                    icon='warning')
                if not consent:
                    self.eye_tracking_var.set(False)
            except Exception as e:
                # If dialog fails, disable and continue
                print(f"Eye tracking consent error: {e}")
                self.eye_tracking_var.set(False)

    def _save_settings(self):
        """Save settings to config manager"""
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

            # Call callback
            if self.on_save:
                try:
                    self.on_save()
                except Exception as e:
                    print(f"Error in settings save callback: {e}")
                    import traceback
                    traceback.print_exc()

            # Close dialog
            self.destroy()

        except ValueError as e:
            # Show error
            error_dialog = ctk.CTkToplevel(self)
            error_dialog.title("Invalid Input")
            error_dialog.geometry("300x150")

            ctk.CTkLabel(
                error_dialog,
                text="Please enter valid positive numbers",
                wraplength=250
            ).pack(expand=True, padx=20, pady=20)

            ctk.CTkButton(
                error_dialog,
                text="OK",
                command=error_dialog.destroy
            ).pack(pady=(0, 20))
