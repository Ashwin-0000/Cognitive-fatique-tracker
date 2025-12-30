"""Chart widgets for visualizing fatigue and activity data"""
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta
from typing import List, Tuple
import matplotlib.pyplot as plt


class ActivityChart(ctk.CTkFrame):
    """Chart showing activity rate over time"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure matplotlib for dark theme
        plt.style.use('dark_background')
        
        # Create figure
        self.figure = Figure(figsize=(8, 3), dpi=80, facecolor='#2b2b2b')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#2b2b2b')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Initialize empty data
        self.timestamps = []
        self.values = []
        
        self._setup_chart()
    
    def _setup_chart(self):
        """Setup chart appearance"""
        self.ax.set_xlabel('Time', color='#94a3b8', fontsize=10)
        self.ax.set_ylabel('Events/Min', color='#94a3b8', fontsize=10)
        self.ax.tick_params(colors='#94a3b8', labelsize=9)
        self.ax.grid(True, alpha=0.1, color='#475569', linestyle='--')
        
        # Style spines
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#334155')
            spine.set_linewidth(1)
    
    def update_data(self, data: List[Tuple[datetime, float]]):
        """
        Update chart with new data.
        
        Args:
            data: List of (timestamp, value) tuples
        """
        if not data:
            return
        
        self.timestamps = [d[0] for d in data]
        self.values = [d[1] for d in data]
        
        self.ax.clear()
        self._setup_chart()
        
        # Plot line with gradient
        if self.timestamps and self.values:
            self.ax.plot(self.timestamps, self.values, 
                        color='#3b82f6', linewidth=2.5, marker='o', 
                        markersize=5, markerfacecolor='#2563eb',
                        markeredgecolor='#60a5fa', markeredgewidth=1.5)
            
            # Fill area under curve with gradient
            self.ax.fill_between(self.timestamps, self.values, alpha=0.4, color='#3b82f6')
        
        # Format x-axis for time
        self.ax.tick_params(axis='x', rotation=45, labelsize=8)
        self.figure.tight_layout()
        self.canvas.draw()


class FatigueChart(ctk.CTkFrame):
    """Chart showing fatigue score over time"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        plt.style.use('dark_background')
        
        # Create figure
        self.figure = Figure(figsize=(8, 3), dpi=80, facecolor='#2b2b2b')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#2b2b2b')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Initialize empty data
        self.timestamps = []
        self.scores = []
        
        self._setup_chart()
    
    def _setup_chart(self):
        """Setup chart appearance"""
        self.ax.set_xlabel('Time', color='#94a3b8', fontsize=10)
        self.ax.set_ylabel('Fatigue Score', color='#94a3b8', fontsize=10)
        self.ax.tick_params(colors='#94a3b8', labelsize=9)
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, alpha=0.1, color='#475569', linestyle='--')
        
        # Add colored threshold zones
        self.ax.axhspan(0, 30, alpha=0.1, color='#10b981', label='Low')
        self.ax.axhspan(30, 60, alpha=0.1, color='#f59e0b', label='Moderate')
        self.ax.axhspan(60, 80, alpha=0.1, color='#f97316', label='High')
        self.ax.axhspan(80, 100, alpha=0.15, color='#ef4444', label='Critical')
        
        # Style spines
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#334155')
            spine.set_linewidth(1)
    
    def update_data(self, data: List[Tuple[datetime, float]]):
        """
        Update chart with new data.
        
        Args:
            data: List of (timestamp, score) tuples
        """
        if not data:
            return
        
        self.timestamps = [d[0] for d in data]
        self.scores = [d[1] for d in data]
        
        self.ax.clear()
        self._setup_chart()
        
        # Plot line with dynamic color
        if self.timestamps and self.scores:
            # Determine color based on average score
            avg_score = sum(self.scores) / len(self.scores)
            if avg_score < 30:
                color = '#10b981'  # Green
            elif avg_score < 60:
                color = '#f59e0b'  # Yellow
            elif avg_score < 80:
                color = '#f97316'  # Orange
            else:
                color = '#ef4444'  # Red
            
            self.ax.plot(self.timestamps, self.scores, 
                        color=color, linewidth=2.5, marker='o',
                        markersize=5, markerfacecolor=color,
                        markeredgecolor='#ffffff', markeredgewidth=1)
            
            # Fill area with gradient
            self.ax.fill_between(self.timestamps, self.scores, alpha=0.3, color=color)
        
        # Format x-axis for time
        self.ax.tick_params(axis='x', rotation=45, labelsize=8)
        self.figure.tight_layout()
        self.canvas.draw()


class MiniGaugeChart(ctk.CTkFrame):
    """Mini gauge chart for showing current fatigue score"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Create label for score
        self.score_label = ctk.CTkLabel(
            self,
            text="0",
            font=ctk.CTkFont(size=72, weight="bold")
        )
        self.score_label.pack(pady=(30, 10))
        
        # Level label
        self.level_label = ctk.CTkLabel(
            self,
            text="Low",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.level_label.pack(pady=(0, 8))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Fatigue Score",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        )
        self.status_label.pack(pady=(0, 30))
    
    def update_score(self, score: float, level: str, color: str):
        """
        Update gauge with new score.
        
        Args:
            score: Fatigue score (0-100)
            level: Fatigue level string
            color: Color for the score
        """
        self.score_label.configure(text=f"{score:.0f}", text_color=color)
        self.level_label.configure(text=level, text_color=color)
    
    def update_value(self, score: float):
        """Update gauge with just a score value (determines level/color automatically)"""
        if score < 30:
            level, color = "Low", "#10b981"
        elif score < 60:
            level, color = "Moderate", "#f59e0b"
        elif score < 80:
            level, color = "High", "#f97316"
        else:
            level, color = "Critical", "#ef4444"
        self.update_score(score, level, color)


class BlinkRateChart(ctk.CTkFrame):
    """Chart showing blink rate over time"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Create figure with new color scheme
        self.figure = Figure(figsize=(8, 3), dpi=80, facecolor='#16213e')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#0f0f1e')
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Initialize empty data
        self.timestamps = []
        self.rates = []
        
        self._setup_chart()
    
    def _setup_chart(self):
        """Setup chart appearance"""
        self.ax.set_xlabel('Time', color='#00ff88', fontweight='bold')
        self.ax.set_ylabel('Blinks/Min', color='#00ff88', fontweight='bold')
        self.ax.tick_params(colors='#ffffff')
        self.ax.set_ylim(0, 30)
        self.ax.grid(True, alpha=0.15, color='#00ff88', linestyle='--')
        
        # Add normal range shading with vibrant green
        self.ax.axhspan(15, 20, alpha=0.2, color='#00ff88', label='Normal Range')
        
        # Add threshold lines with vibrant colors
        self.ax.axhline(y=15, color='#ffaa00', linestyle='--', alpha=0.6, linewidth=1.5)
        self.ax.axhline(y=10, color='#ff4757', linestyle='--', alpha=0.6, linewidth=1.5)
        
        # Style spines with vibrant green
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#00ff88')
            spine.set_linewidth(1.5)
    
    def update_data(self, data: List[Tuple[datetime, float]]):
        """
        Update chart with new data.
        
        Args:
            data: List of (timestamp, blink_rate) tuples
        """
        if not data:
            return
        
        self.timestamps = [d[0] for d in data]
        self.rates = [d[1] for d in data]
        
        self.ax.clear()
        self._setup_chart()
        
        # Plot line with vibrant green
        if self.timestamps and self.rates:
            self.ax.plot(self.timestamps, self.rates, 
                        color='#00ff88', linewidth=2.5, marker='o',
                        markersize=5, markerfacecolor='#00cc6a', 
                        markeredgecolor='#00ff88', markeredgewidth=1.5,
                        label='Blink Rate')
            
            # Fill area with gradient effect
            self.ax.fill_between(self.timestamps, self.rates, alpha=0.3, color='#00ff88')
        
        # Format x-axis for time
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.legend(loc='upper right', fontsize=9, facecolor='#16213e', 
                      edgecolor='#00ff88', labelcolor='#ffffff', framealpha=0.8)
        self.figure.tight_layout()
        self.canvas.draw()
