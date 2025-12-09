"""Dashboard panel showing current statistics"""
import customtkinter as ctk
from typing import Optional
from src.ui.charts import MiniGaugeChart
from src.utils.helpers import format_duration


class Dashboard(ctk.CTkFrame):
    """Main dashboard showing key metrics"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="transparent")
        
        # Configure grid layout (2x4 now)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        
        # Fatigue Score Card (large, spans 2 rows)
        self.fatigue_card = self._create_card("Fatigue Score", row=0, column=0, rowspan=2)
        self.fatigue_gauge = MiniGaugeChart(self.fatigue_card)
        self.fatigue_gauge.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Work Time Card
        self.work_time_card = self._create_card("Work Time", row=0, column=1)
        self.work_time_label = ctk.CTkLabel(
            self.work_time_card,
            text="0m",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        self.work_time_label.pack(expand=True)
        
        # Session Time Card
        self.session_time_card = self._create_card("Session Time", row=0, column=2)
        self.session_time_label = ctk.CTkLabel(
            self.session_time_card,
            text="0m",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        self.session_time_label.pack(expand=True)
        
        # Blink Rate Card (NEW)
        self.blink_card = self._create_card("Blink Rate", row=0, column=3)
        self.blink_label = ctk.CTkLabel(
            self.blink_card,
            text="--",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        self.blink_label.pack(expand=True)
        self.blink_subtitle = ctk.CTkLabel(
            self.blink_card,
            text="blinks/min",
            font=ctk.CTkFont(size=12),
            text_color="#999999"
        )
        self.blink_subtitle.pack()
        
        # Activity Rate Card
        self.activity_card = self._create_card("Activity Rate", row=1, column=1)
        self.activity_label = ctk.CTkLabel(
            self.activity_card,
            text="0",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        self.activity_label.pack(expand=True)
        self.activity_subtitle = ctk.CTkLabel(
            self.activity_card,
            text="events/min",
            font=ctk.CTkFont(size=12),
            text_color="#999999"
        )
        self.activity_subtitle.pack()
        
        # Next Break Card
        self.break_card = self._create_card("Next Break", row=1, column=2)
        self.break_label = ctk.CTkLabel(
            self.break_card,
            text="--",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        self.break_label.pack(expand=True)
        
        # Eye Tracking Status Card (NEW)
        self.eye_status_card = self._create_card("Eye Tracking", row=1, column=3)
        self.eye_status_label = ctk.CTkLabel(
            self.eye_status_card,
            text="Disabled",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#999999"
        )
        self.eye_status_label.pack(expand=True)
    
    def _create_card(self, title: str, row: int, column: int, rowspan: int = 1) -> ctk.CTkFrame:
        """Create a metric card"""
        card = ctk.CTkFrame(self, corner_radius=10)
        card.grid(row=row, column=column, rowspan=rowspan, padx=10, pady=10, sticky="nsew")
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#999999"
        )
        title_label.pack(pady=(15, 5))
        
        return card
    
    def update_stats(
        self,
        fatigue_score: float = 0,
        fatigue_level: str = "Low",
        fatigue_color: str = "#4CAF50",
        work_time_seconds: float = 0,
        session_time_seconds: float = 0,
        activity_rate: float = 0,
        time_until_break_seconds: float = 0,
        is_on_break: bool = False,
        blink_rate: float = 0,
        eye_tracking_enabled: bool = False
    ):
        """Update all dashboard statistics"""
        
        # Update fatigue gauge
        self.fatigue_gauge.update_score(fatigue_score, fatigue_level, fatigue_color)
        
        # Update work time
        self.work_time_label.configure(text=format_duration(work_time_seconds))
        
        # Update session time
        self.session_time_label.configure(text=format_duration(session_time_seconds))
        
        # Update activity rate
        self.activity_label.configure(text=f"{activity_rate:.0f}")
        
        # Update blink rate
        if eye_tracking_enabled and blink_rate > 0:
            # Color based on blink rate
            if blink_rate >= 15:
                blink_color = "#4CAF50"  # Green - Normal
            elif blink_rate >= 10:
                blink_color = "#FFC107"  # Yellow - Low
            else:
                blink_color = "#F44336"  # Red - Critical
            
            self.blink_label.configure(text=f"{blink_rate:.0f}", text_color=blink_color)
        else:
            self.blink_label.configure(text="--", text_color="#999999")
        
        # Update eye tracking status
        if eye_tracking_enabled:
            self.eye_status_label.configure(text="Active", text_color="#4CAF50")
        else:
            self.eye_status_label.configure(text="Disabled", text_color="#999999")
        
        # Update break timer
        if is_on_break:
            self.break_label.configure(text="On Break", text_color="#4CAF50")
        elif time_until_break_seconds <= 0:
            self.break_label.configure(text="Now!", text_color="#FFC107")
        else:
            self.break_label.configure(
                text=format_duration(time_until_break_seconds),
                text_color="#ffffff"
            )
