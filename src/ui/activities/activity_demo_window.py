"""Interactive window for demonstrating refresh activities with enhanced UX"""
import customtkinter as ctk
from .activity_definitions import Activity
import time
import math
from datetime import datetime


class ActivityDemoWindow(ctk.CTkToplevel):
    """Enhanced window for demonstrating activities with breathing animations and better UX"""

    def __init__(self, parent, activity: Activity):
        super().__init__(parent)

        self.activity = activity
        self.time_remaining = activity.duration_seconds
        self.is_running = False
        self.start_time = None
        self.current_cycle = 0
        self.total_cycles = 3  # For breathing exercises

        # Animation properties
        self.breath_phase = 0  # 0-1 for animation
        self.breath_direction = 1  # 1 for inhale, -1 for exhale

        # Window setup
        self.title(f"🧘 {activity.name}")

        # Set window size
        window_width = 900
        window_height = 750

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center the window
        self.update_idletasks()

        try:
            parent_x = parent.winfo_x()
            parent_y = parent.winfo_y()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()

            x = parent_x + (parent_width // 2) - (window_width // 2)
            y = parent_y + (parent_height // 2) - (window_height // 2)
        except BaseException:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)

        x = max(0, x)
        y = max(0, y)

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.resizable(False, False)

        # Set calming background color
        self.configure(fg_color="#0d1117")

        self._create_widgets()

    def _create_widgets(self):
        """Create all UI widgets with modern, calming design"""

        # ===== TOP BAR WITH TIMER AND CYCLE COUNTER =====
        top_bar = ctk.CTkFrame(self, fg_color="transparent", height=60)
        top_bar.pack(fill="x", padx=0, pady=0)
        top_bar.pack_propagate(False)

        # Countdown timer (top-right)
        self.timer_display = ctk.CTkLabel(
            top_bar,
            text=self._format_time(self.time_remaining),
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#10b981"
        )
        self.timer_display.pack(side="right", padx=20, pady=10)

        # Cycle counter for breathing exercises
        self.cycle_label = ctk.CTkLabel(
            top_bar,
            text=f"Cycle {self.current_cycle + 1} of {self.total_cycles}",
            font=ctk.CTkFont(size=16),
            text_color="#888888"
        )
        self.cycle_label.pack(side="left", padx=20, pady=10)

        # ===== TITLE SECTION WITH EMPHASIS =====
        title_frame = ctk.CTkFrame(self, fg_color="transparent", height=110)
        title_frame.pack(fill="x", padx=35, pady=(8, 18))
        title_frame.pack_propagate(False)

        # Activity icon
        icons = {
            "eye": "👁️",
            "breathing": "🫁",
            "physical": "💪",
            "meditation": "🧘",
            "combo": "⚡"
        }
        icon = icons.get(self.activity.category.value, "✨")

        # Large, prominent title with consistent sizing
        title = ctk.CTkLabel(
            title_frame,
            text=f"{icon}  {self.activity.name}",
            font=ctk.CTkFont(size=38, weight="bold"),
            text_color="#ffffff"
        )
        title.pack(pady=(12, 6))

        # Subtitle/description with optimized font
        subtitle = ctk.CTkLabel(
            title_frame,
            text=self.activity.description,
            font=ctk.CTkFont(size=15),
            text_color="#a0a0a0",
            wraplength=800
        )
        subtitle.pack(pady=(0, 8))

        # ===== MAIN CONTENT AREA: LEFT SIDE (INSTRUCTIONS) | RIGHT SIDE (ANIMA
        content_container = ctk.CTkFrame(self, fg_color="transparent")
        content_container.pack(fill="both", expand=True, padx=30, pady=(0, 12))

        content_container.grid_columnconfigure(0, weight=1)
        content_container.grid_columnconfigure(1, weight=1)
        content_container.grid_rowconfigure(0, weight=1)

        # LEFT: Instructions and Benefits
        left_panel = ctk.CTkFrame(content_container, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Instructions Section with better spacing
        inst_frame = ctk.CTkFrame(
            left_panel,
            corner_radius=16,
            fg_color="#161b22",
            border_width=1,
            border_color="#21262d")
        inst_frame.pack(fill="both", expand=True, pady=(0, 15))

        inst_title = ctk.CTkLabel(
            inst_frame,
            text="📋  Instructions",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#58a6ff",
            anchor="w"
        )
        inst_title.pack(anchor="w", padx=22, pady=(16, 10))

        # Scrollable instructions with better readability
        inst_scroll = ctk.CTkScrollableFrame(
            inst_frame,
            fg_color="transparent",
            height=185
        )
        inst_scroll.pack(fill="both", expand=True, padx=22, pady=(0, 16))

        for i, instruction in enumerate(self.activity.instructions, 1):
            inst_label = ctk.CTkLabel(
                inst_scroll,
                text=f"{i}. {instruction}",
                font=ctk.CTkFont(size=14),
                text_color="#c9d1d9",
                anchor="w",
                wraplength=360,
                justify="left"
            )
            inst_label.pack(anchor="w", pady=6, padx=8)

        # Benefits Section (visually separated) with better padding
        benefits_frame = ctk.CTkFrame(
            left_panel,
            corner_radius=16,
            fg_color="#1a1f26",
            border_width=1,
            border_color="#30363d")
        benefits_frame.pack(fill="x", pady=(0, 0))

        benefits_title = ctk.CTkLabel(
            benefits_frame,
            text="✨  Benefits",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#58a6ff",
            anchor="w"
        )
        benefits_title.pack(anchor="w", padx=22, pady=(14, 8))

        benefits_text = ctk.CTkLabel(
            benefits_frame,
            text=self.activity.benefits,
            font=ctk.CTkFont(size=14),
            text_color="#8b949e",
            anchor="w",
            wraplength=390,
            justify="left"
        )
        benefits_text.pack(anchor="w", padx=22, pady=(0, 12))

        # Effectiveness stars with better spacing
        stars = "⭐" * int(self.activity.effectiveness_rating)
        rating_label = ctk.CTkLabel(
            benefits_frame,
            text=f"Effectiveness: {stars} ({self.activity.effectiveness_rating}/5)",
            font=ctk.CTkFont(
                size=13),
            text_color="#58a6ff",
            anchor="w")
        rating_label.pack(anchor="w", padx=22, pady=(0, 14))

        # RIGHT: Breathing Animation Circle
        right_panel = ctk.CTkFrame(content_container, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Animation canvas
        self.animation_frame = ctk.CTkFrame(
            right_panel,
            corner_radius=20,
            fg_color="#161b22",
            border_width=1,
            border_color="#21262d")
        self.animation_frame.pack(fill="both", expand=True)

        # Breathing cue text (centered above circle) with better sizing
        self.breath_cue_label = ctk.CTkLabel(
            self.animation_frame,
            text="Ready to Begin",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#58a6ff"
        )
        self.breath_cue_label.pack(pady=(35, 18))

        # Create canvas for animated circle
        self.canvas = ctk.CTkCanvas(
            self.animation_frame,
            width=280,
            height=280,
            bg="#161b22",
            highlightthickness=0
        )
        self.canvas.pack(pady=(20, 40))

        # Draw initial breathing circle
        self.circle_id = self.canvas.create_oval(
            90, 90, 190, 190,
            fill="#10b981",
            outline="#34d399",
            width=3
        )

        # Breathing instruction below circle with consistent sizing
        self.breath_instruction = ctk.CTkLabel(
            self.animation_frame,
            text="Press Start to begin",
            font=ctk.CTkFont(size=15),
            text_color="#8b949e"
        )
        self.breath_instruction.pack(pady=(0, 22))

        # ===== PROGRESS BAR (DYNAMIC FOR BREATH CYCLES) =====
        progress_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        progress_frame.pack(fill="x", padx=30, pady=(0, 15))
        progress_frame.pack_propagate(False)

        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            height=8,
            corner_radius=4,
            progress_color="#10b981",
            fg_color="#1f2937"
        )
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0)

        # ===== CONTROL BUTTONS (BOTTOM) - LARGER SIZES =====
        button_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        button_frame.pack(fill="x", padx=30, pady=(0, 20))
        button_frame.pack_propagate(False)

        # Start button (prominent, larger)
        self.start_btn = ctk.CTkButton(
            button_frame,
            text="▶  Start Activity",
            command=self._start_activity,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            height=65,
            width=230,
            corner_radius=12
        )
        self.start_btn.pack(side="left", padx=(0, 10))

        # Pause button (larger)
        self.pause_btn = ctk.CTkButton(
            button_frame,
            text="⏸  Pause",
            command=self._pause_activity,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#6b7280",
            hover_color="#4b5563",
            height=65,
            width=160,
            corner_radius=12,
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=5)

        # Reset button (larger)
        self.reset_btn = ctk.CTkButton(
            button_frame,
            text="🔄  Reset",
            command=self._reset_activity,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#f59e0b",
            hover_color="#d97706",
            height=65,
            width=160,
            corner_radius=12
        )
        self.reset_btn.pack(side="left", padx=5)

        # Audio toggle (larger)
        self.audio_btn = ctk.CTkButton(
            button_frame,
            text="🔊  Audio Guide",
            command=self._toggle_audio,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color="#374151",
            border_width=2,
            border_color="#4b5563",
            text_color="#9ca3af",
            height=65,
            width=170,
            corner_radius=12
        )
        self.audio_btn.pack(side="right", padx=0)

    def _start_activity(self):
        """Start the activity with breathing animation"""
        if not self.is_running:
            self.is_running = True
            self.start_time = datetime.now()
            self.start_btn.configure(
                text="▶  Running...",
                state="disabled",
                fg_color="#6b7280")
            self.pause_btn.configure(state="normal", fg_color="#f59e0b")
            self.breath_cue_label.configure(text="Breathe In Deeply...")
            self._update_timer()
            self._animate_breathing()

    def _pause_activity(self):
        """Pause/resume the activity"""
        if self.is_running:
            self.is_running = False
            self.pause_btn.configure(text="▶  Resume", fg_color="#10b981")
            self.start_btn.configure(
                text="⏸  Paused",
                state="normal",
                fg_color="#6b7280")
            self.breath_cue_label.configure(text="Paused")
        else:
            self.is_running = True
            self.pause_btn.configure(text="⏸  Pause", fg_color="#f59e0b")
            self.start_btn.configure(
                text="▶  Running...",
                state="disabled",
                fg_color="#6b7280")
            self._update_timer()
            self._animate_breathing()

    def _reset_activity(self):
        """Reset the activity"""
        self.is_running = False
        self.time_remaining = self.activity.duration_seconds
        self.current_cycle = 0
        self.breath_phase = 0

        self.timer_display.configure(
            text=self._format_time(
                self.time_remaining))
        self.progress_bar.set(0)
        self.cycle_label.configure(
            text=f"Cycle {self.current_cycle + 1} of {self.total_cycles}")
        self.start_btn.configure(
            text="▶  Start Activity",
            state="normal",
            fg_color="#10b981")
        self.pause_btn.configure(
            text="⏸  Pause",
            state="disabled",
            fg_color="#6b7280")
        self.breath_cue_label.configure(text="Ready to Begin")
        self.breath_instruction.configure(text="Press Start to begin")

        # Reset circle
        self.canvas.coords(self.circle_id, 90, 90, 190, 190)
        self.canvas.itemconfig(
            self.circle_id,
            fill="#10b981",
            outline="#34d399")

    def _update_timer(self):
        """Update timer display"""
        if not self.is_running:
            return

        if self.time_remaining <= 0:
            self._on_complete()
            return

        self.time_remaining -= 1
        self.timer_display.configure(
            text=self._format_time(
                self.time_remaining))

        # Update progress bar
        total_duration = self.activity.duration_seconds
        progress = 1 - (self.time_remaining / total_duration)
        self.progress_bar.set(progress)

        # Update cycle every ~60 seconds for breathing (simplified)
        if self.time_remaining % 60 == 0 and self.current_cycle < self.total_cycles - 1:
            self.current_cycle += 1
            self.cycle_label.configure(
                text=f"Cycle {self.current_cycle + 1} of {self.total_cycles}")

        # Schedule next update
        self.after(1000, self._update_timer)

    def _animate_breathing(self):
        """Animate the breathing circle with smooth expansion/contraction - SLOWER for natural breathing"""
        if not self.is_running:
            return

        # Update breath phase (0 to 1 and back) - SLOWED DOWN for 4s inhale / 6s exhale rhythm
        # 0.01 * 60fps = 0.6/sec = ~1.67 seconds per direction = ~3.3s cycle (close to 4s inhale)
        # We'll use 0.01 for inhale and 0.0067 for exhale to get 4s / 6s timing
        speed = 0.01 if self.breath_direction == 1 else 0.0067  # Slower exhale
        self.breath_phase += speed * self.breath_direction

        # Reverse direction at extremes with calming text
        if self.breath_phase >= 1:
            self.breath_phase = 1
            self.breath_direction = -1
            self.breath_cue_label.configure(
                text="Breathe Out Slowly...", text_color="#f59e0b")
            self.breath_instruction.configure(
                text="Exhale gently through your mouth (6 seconds)")
        elif self.breath_phase <= 0:
            self.breath_phase = 0
            self.breath_direction = 1
            self.breath_cue_label.configure(
                text="Breathe In Deeply...", text_color="#10b981")
            self.breath_instruction.configure(
                text="Take a deep breath through your nose (4 seconds)")

        # Calculate circle size (smooth easing)
        # Using smooth ease-in-out function
        t = self.breath_phase
        ease = t * t * (3 - 2 * t)  # Smoothstep function

        min_size = 80
        max_size = 150
        size = min_size + (max_size - min_size) * ease

        # Update circle position and size
        center_x, center_y = 140, 140
        x1 = center_x - size
        y1 = center_y - size
        x2 = center_x + size
        y2 = center_y + size

        self.canvas.coords(self.circle_id, x1, y1, x2, y2)

        # Change color based on breath phase
        if self.breath_direction == 1:  # Inhale
            self.canvas.itemconfig(
                self.circle_id,
                fill="#10b981",
                outline="#34d399")
        else:  # Exhale
            self.canvas.itemconfig(
                self.circle_id,
                fill="#f59e0b",
                outline="#fbbf24")

        # Schedule next frame (60 FPS)
        self.after(16, self._animate_breathing)

    def _toggle_audio(self):
        """Toggle audio guidance (placeholder)"""
        # This would integrate with a text-to-speech system
        # For now, just visual feedback
        current_text = self.audio_btn.cget("text")
        if "🔊" in current_text:
            self.audio_btn.configure(text="🔇  Audio Off", fg_color="#374151")
        else:
            self.audio_btn.configure(
                text="🔊  Audio Guide",
                fg_color="transparent")

    def _on_complete(self):
        """Handle activity completion"""
        self.is_running = False
        self.timer_display.configure(text="✅ Done!", text_color="#10b981")
        self.progress_bar.set(1)
        self.start_btn.configure(
            text="✅ Completed",
            state="disabled",
            fg_color="#10b981")
        self.pause_btn.configure(state="disabled")
        self.breath_cue_label.configure(
            text="Activity Complete! 🎉",
            text_color="#10b981")
        self.breath_instruction.configure(
            text="Great work! You should feel refreshed.")

        # Show completion dialog
        self._show_completion_dialog()

    def _show_completion_dialog(self):
        """Show a calming completion message"""
        completion_window = ctk.CTkToplevel(self)
        completion_window.title("Activity Complete!")
        completion_window.geometry("500x350")
        completion_window.resizable(False, False)
        completion_window.transient(self)
        completion_window.grab_set()
        completion_window.configure(fg_color="#0d1117")

        # Center on parent
        completion_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - 250
        y = self.winfo_y() + (self.winfo_height() // 2) - 175
        completion_window.geometry(f"500x350+{x}+{y}")

        # Success icon with glow effect
        icon_frame = ctk.CTkFrame(completion_window, fg_color="transparent")
        icon_frame.pack(pady=(40, 15))

        success_icon = ctk.CTkLabel(
            icon_frame,
            text="🎉",
            font=ctk.CTkFont(size=90)
        )
        success_icon.pack()

        # Message
        title_label = ctk.CTkLabel(
            completion_window,
            text="Fantastic Work!",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#10b981"
        )
        title_label.pack(pady=(10, 15))

        detail_label = ctk.CTkLabel(
            completion_window,
            text=f"You've completed the {self.activity.name}.\n\nYou should feel refreshed, focused, and energized!",
            font=ctk.CTkFont(
                size=16),
            text_color="#c9d1d9",
            justify="center")
        detail_label.pack(pady=15)

        # Close button
        ok_btn = ctk.CTkButton(
            completion_window,
            text="Awesome! ✨",
            command=completion_window.destroy,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            width=250,
            height=50,
            corner_radius=12
        )
        ok_btn.pack(pady=30)

    def _format_time(self, seconds: int) -> str:
        """Format seconds as MM:SS"""
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"
