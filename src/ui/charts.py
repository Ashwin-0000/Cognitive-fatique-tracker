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
        self.ax.set_xlabel('Time', color='#ffffff')
        self.ax.set_ylabel('Events/Min', color='#ffffff')
        self.ax.set_title('Activity Rate', color='#ffffff', fontsize=12, pad=10)
        self.ax.tick_params(colors='#ffffff')
        self.ax.grid(True, alpha=0.2, color='#ffffff')
        
        # Style spines
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#555555')
    
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
        
        # Plot line
        if self.timestamps and self.values:
            self.ax.plot(self.timestamps, self.values, 
                        color='#3b8ed0', linewidth=2, marker='o', 
                        markersize=4, markerfacecolor='#1f6aa5')
            
            # Fill area under curve
            self.ax.fill_between(self.timestamps, self.values, alpha=0.3, color='#3b8ed0')
        
        # Format x-axis for time
        self.ax.tick_params(axis='x', rotation=45)
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
        self.ax.set_xlabel('Time', color='#ffffff')
        self.ax.set_ylabel('Fatigue Score', color='#ffffff')
        self.ax.set_title('Fatigue Level', color='#ffffff', fontsize=12, pad=10)
        self.ax.tick_params(colors='#ffffff')
        self.ax.set_ylim(0, 100)
        self.ax.grid(True, alpha=0.2, color='#ffffff')
        
        # Add threshold lines
        self.ax.axhline(y=30, color='#4CAF50', linestyle='--', alpha=0.5, linewidth=1)
        self.ax.axhline(y=60, color='#FFC107', linestyle='--', alpha=0.5, linewidth=1)
        self.ax.axhline(y=80, color='#F44336', linestyle='--', alpha=0.5, linewidth=1)
        
        # Style spines
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#555555')
    
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
        
        # Plot line with color gradient based on score
        if self.timestamps and self.scores:
            # Determine color based on average score
            avg_score = sum(self.scores) / len(self.scores)
            if avg_score < 30:
                color = '#4CAF50'  # Green
            elif avg_score < 60:
                color = '#FFC107'  # Yellow
            elif avg_score < 80:
                color = '#FF9800'  # Orange
            else:
                color = '#F44336'  # Red
            
            self.ax.plot(self.timestamps, self.scores, 
                        color=color, linewidth=2, marker='o',
                        markersize=4)
            
            # Fill area
            self.ax.fill_between(self.timestamps, self.scores, alpha=0.3, color=color)
        
        # Format x-axis for time
        self.ax.tick_params(axis='x', rotation=45)
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
            font=ctk.CTkFont(size=48, weight="bold")
        )
        self.score_label.pack(pady=(20, 5))
        
        # Level label
        self.level_label = ctk.CTkLabel(
            self,
            text="Low",
            font=ctk.CTkFont(size=18)
        )
        self.level_label.pack(pady=(0, 5))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="Fatigue Score",
            font=ctk.CTkFont(size=12),
            text_color="#999999"
        )
        self.status_label.pack(pady=(0, 20))
    
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


class BlinkRateChart(ctk.CTkFrame):
    """Chart showing blink rate over time"""
    
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
        self.rates = []
        
        self._setup_chart()
    
    def _setup_chart(self):
        """Setup chart appearance"""
        self.ax.set_xlabel('Time', color='#ffffff')
        self.ax.set_ylabel('Blinks/Min', color='#ffffff')
        self.ax.set_title('Blink Rate', color='#ffffff', fontsize=12, pad=10)
        self.ax.tick_params(colors='#ffffff')
        self.ax.set_ylim(0, 30)
        self.ax.grid(True, alpha=0.2, color='#ffffff')
        
        # Add normal range shading
        self.ax.axhspan(15, 20, alpha=0.2, color='#4CAF50', label='Normal Range')
        
        # Add threshold lines
        self.ax.axhline(y=15, color='#FFC107', linestyle='--', alpha=0.5, linewidth=1)
        self.ax.axhline(y=10, color='#F44336', linestyle='--', alpha=0.5, linewidth=1)
        
        # Style spines
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#555555')
    
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
        
        # Plot line
        if self.timestamps and self.rates:
            self.ax.plot(self.timestamps, self.rates, 
                        color='#9C27B0', linewidth=2, marker='o',
                        markersize=4, label='Blink Rate')
            
            # Fill area
            self.ax.fill_between(self.timestamps, self.rates, alpha=0.3, color='#9C27B0')
        
        # Format x-axis for time
        self.ax.tick_params(axis='x', rotation=45)
        self.ax.legend(loc='upper right', fontsize=8)
        self.figure.tight_layout()
        self.canvas.draw()
