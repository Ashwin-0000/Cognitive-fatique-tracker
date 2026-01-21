"""Dashboard with refined spacing, alignment, and visual hierarchy"""
import customtkinter as ctk
from typing import Optional
from src.ui.charts import MiniGaugeChart
from src.utils.helpers import format_duration


class Dashboard(ctk.CTkFrame):
    """Polished dashboard with perfect spacing and alignment"""

    def __init__(self, master, on_navigate=None, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(fg_color="transparent")
        self.on_navigate = on_navigate

        # Grid with larger minimum sizes for bigger tiles
        self.grid_columnconfigure(
            0, weight=2, minsize=400)  # Fatigue column - larger
        self.grid_columnconfigure(
            1, weight=1, minsize=250)  # Metric tiles - larger
        self.grid_columnconfigure(2, weight=1, minsize=250)
        self.grid_columnconfigure(3, weight=1, minsize=250)
        self.grid_rowconfigure(
            0,
            weight=1,
            uniform="row",
            minsize=220)  # Minimum row height
        self.grid_rowconfigure(1, weight=1, uniform="row", minsize=220)

        # Fatigue Score (large, 2 rows)
        self.fatigue_card = self._create_card(
            title="Fatigue Score",
            icon="🧠",
            row=0, column=0, rowspan=2,
            on_click=on_navigate
        )

        # Fatigue gauge - more padding for larger tile
        gauge_container = ctk.CTkFrame(
            self.fatigue_card, fg_color="transparent")
        gauge_container.pack(fill="both", expand=True, padx=30, pady=30)

        self.fatigue_gauge = MiniGaugeChart(gauge_container)
        self.fatigue_gauge.pack(fill="both", expand=True)
        if on_navigate:
            self.fatigue_gauge.configure(cursor="hand2")
            self.fatigue_gauge.bind("<Button-1>", lambda e: on_navigate())

        # Activity Rate
        self.activity_card = self._create_card(
            title="Activity rate",
            icon="📊",
            row=0, column=1,
            on_click=on_navigate
        )
        self.activity_label, self.activity_subtitle = self._create_metric_content(
            self.activity_card, "0", "events/min")

        # Blink Rate
        self.blink_card = self._create_card(
            title="Blink rate",
            icon="👁️",
            row=0, column=2,
            on_click=on_navigate
        )
        self.blink_label, self.blink_subtitle = self._create_metric_content(
            self.blink_card, "--", "blinks/min"
        )

        # Keystrokes
        self.keystroke_card = self._create_card(
            title="Keystrokes",
            icon="⌨️",
            row=0, column=3,
            on_click=on_navigate
        )
        self.keystroke_label, _ = self._create_metric_content(
            self.keystroke_card, "0", "keys pressed"
        )

        # Mouse Clicks
        self.mouse_card = self._create_card(
            title="Mouse clicks",
            icon="🖱️",
            row=1, column=1,
            on_click=on_navigate
        )
        self.mouse_label, _ = self._create_metric_content(
            self.mouse_card, "0", "clicks"
        )

        # Work Time
        self.work_time_card = self._create_card(
            title="Work time",
            icon="⏱️",
            row=1, column=2
        )
        self.work_time_label, _ = self._create_metric_content(
            self.work_time_card, "0m", ""
        )

        # Session Time
        self.session_time_card = self._create_card(
            title="Session time",
            icon="⏲️",
            row=1, column=3
        )
        self.session_time_label, _ = self._create_metric_content(
            self.session_time_card, "0m", ""
        )

        self.break_label = None
        self.eye_status_label = None

    def _create_card(self, title: str, row: int, column: int,
                     rowspan: int = 1, columnspan: int = 1,
                     icon: str = "", on_click=None) -> ctk.CTkFrame:
        """Create simplified card with only icon and heading"""

        card = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color="#1e293b",
            border_width=1,
            border_color="#334155"
        )
        card.grid(
            row=row,
            column=column,
            rowspan=rowspan,
            columnspan=columnspan,
            padx=8,
            pady=8,
            sticky="nsew")

        # Header: simple icon + title layout
        header = ctk.CTkFrame(card, fg_color="transparent", height=50)
        header.pack(fill="x", padx=25, pady=(25, 0))
        header.pack_propagate(False)

        # Icon + Title in a row, left-aligned
        if icon:
            icon_colors = {
                "🧠": "#8b5cf6",
                "📊": "#f97316",
                "👁️": "#8b5cf6",
                "⌨️": "#10b981",
                "🖱️": "#10b981",
                "⏱️": "#3b82f6",
                "⏲️": "#14b8a6"}
            icon_label = ctk.CTkLabel(
                header, text=icon, font=ctk.CTkFont(size=18),
                fg_color=icon_colors.get(icon, "#475569"),
                corner_radius=10, width=36, height=36
            )
            icon_label.pack(side="left", padx=(0, 12), pady=7)

        # Title aligned with icon
        title_label = ctk.CTkLabel(
            header, text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e2e8f0", anchor="w"
        )
        title_label.pack(side="left", pady=7)

        # Clickable with smooth animations
        if on_click:
            card.configure(cursor="hand2")
            card.bind("<Button-1>", lambda e: on_click())

            # Smooth hover with glow effect
            def on_enter(e):
                card.configure(border_color="#3b82f6", border_width=2)

            def on_leave(e):
                card.configure(border_color="#334155", border_width=1)

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

            def bind_recursive(w):
                try:
                    w.bind("<Button-1>", lambda e: on_click())
                    w.configure(cursor="hand2")
                    for c in w.winfo_children():
                        bind_recursive(c)
                except BaseException:
                    pass
            card.after(100, lambda: bind_recursive(card))

        return card

    def _create_metric_content(self, parent_card, value_text, unit_text):
        """Create centered metric value and unit label"""
        content = ctk.CTkFrame(parent_card, fg_color="transparent")
        content.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(
                0,
                25))  # More padding

        # Value centered - larger font
        value_label = ctk.CTkLabel(
            content, text=value_text,
            font=ctk.CTkFont(size=44, weight="bold"),  # Larger value
            text_color="#ffffff"
        )
        value_label.pack(expand=True, pady=(10, 5))

        # Unit label - larger
        if unit_text:
            unit_label = ctk.CTkLabel(
                content, text=unit_text,
                font=ctk.CTkFont(size=13),  # Larger unit text
                text_color="#94a3b8"
            )
            unit_label.pack(pady=(0, 10))
            return value_label, unit_label

        return value_label, None

    def update_stats(self, fatigue_score=None, work_time=None, session_time=None,
                     activity_rate=None, blink_rate=None, next_break=None,
                     eye_tracking_active=False, keystroke_count=None, mouse_count=None,
                     fatigue_level=None, fatigue_color=None, **kwargs):  # Backward compatibility
        """Update dashboard statistics with flexible parameter handling"""

        # Map legacy parameter names to current names
        if fatigue_level is not None and fatigue_score is None:
            fatigue_score = fatigue_level

        # Handle time parameters in seconds
        if 'work_time_seconds' in kwargs and work_time is None:
            work_time = int(kwargs['work_time_seconds'])
        if 'session_time_seconds' in kwargs and session_time is None:
            session_time = int(kwargs['session_time_seconds'])
        if 'time_until_break_seconds' in kwargs and next_break is None:
            next_break = int(kwargs['time_until_break_seconds'])

        # Map eye tracking parameter variations
        if 'eye_tracking_enabled' in kwargs:
            eye_tracking_active = kwargs['eye_tracking_enabled']

        # Update UI elements
        if fatigue_score is not None:
            self.fatigue_gauge.update_value(fatigue_score)
        if work_time is not None:
            self.work_time_label.configure(text=format_duration(work_time))
        if session_time is not None:
            self.session_time_label.configure(
                text=format_duration(session_time))
        if activity_rate is not None:
            self.activity_label.configure(text=f"{int(activity_rate)}")
        if blink_rate is not None:
            self.blink_label.configure(text=f"{int(blink_rate)}")
        if keystroke_count is not None:
            self.keystroke_label.configure(text=f"{int(keystroke_count)}")
        if mouse_count is not None:
            self.mouse_label.configure(text=f"{int(mouse_count)}")
