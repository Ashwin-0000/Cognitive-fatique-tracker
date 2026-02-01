"""Blink rate chart component"""
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
from datetime import datetime


class BlinkRateChart(ctk.CTkFrame):
    """Chart displaying eye blink rate over time"""

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        # Data storage
        self.max_points = 50
        self.timestamps = deque(maxlen=self.max_points)
        self.blink_rates = deque(maxlen=self.max_points)

        # Create figure with dark theme
        self.fig = Figure(figsize=(8, 3), dpi=100, facecolor='#1a1a2e')
        self.ax = self.fig.add_subplot(111)

        # Style the plot
        self.ax.set_facecolor('#16213e')
        self.ax.spines['bottom'].set_color('#00ff88')
        self.ax.spines['top'].set_color('#00ff88')
        self.ax.spines['left'].set_color('#00ff88')
        self.ax.spines['right'].set_color('#00ff88')
        self.ax.tick_params(colors='#ffffff')

        # Labels
        self.ax.set_xlabel('Time', color='#00ff88', fontsize=10)
        self.ax.set_ylabel('Blinks/min', color='#00ff88', fontsize=10)

        # Grid
        self.ax.grid(True, alpha=0.2, color='#00ff88')

        # Initialize empty line
        self.line, = self.ax.plot(
            [], [], color='#00ff88', linewidth=2, marker='o', markersize=4)

        # Add normal range indicator
        self.ax.axhspan(
            15,
            20,
            alpha=0.1,
            color='#00ff88',
            label='Normal Range')
        self.ax.legend(
            loc='upper right',
            fontsize=8,
            facecolor='#16213e',
            edgecolor='#00ff88',
            labelcolor='#ffffff')

        # Tight layout
        self.fig.tight_layout()

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def add_data_point(self, blink_rate: float):
        """Add a new blink rate data point"""
        self.timestamps.append(datetime.now())
        self.blink_rates.append(blink_rate)
        self.update_plot()

    def update_data(self, history: list):
        """
        Update chart with history data.
        
        Args:
            history: List of (datetime, value) tuples
        """
        self.timestamps.clear()
        self.blink_rates.clear()
        
        for t, v in history:
            self.timestamps.append(t)
            self.blink_rates.append(v)
            
        self.update_plot()

    def update_plot(self):
        """Update the plot with current data"""
        if len(self.blink_rates) == 0:
            return

        # Update line data
        # Use integers for x-axis to keep it simple, or formatted times if needed
        # For blinking chart, simple index is usually fine for scrolling view
        self.line.set_data(range(len(self.blink_rates)), list(self.blink_rates))

        # Auto-scale x-axis
        self.ax.set_xlim(0, max(len(self.blink_rates) - 1, 1))

        # Smart Y-axis scaling
        # We always want to see 0-30 range (including normal range 15-20)
        # But if data goes higher, expand the view
        
        if len(self.blink_rates) > 0:
            max_val = max(self.blink_rates)
        else:
            max_val = 0
            
        # Minimum ceiling of 30, or 20% above max data
        y_max = max(30, max_val * 1.2)
        
        self.ax.set_ylim(0, y_max)

        # Redraw
        self.canvas.draw()
        
    def clear(self):
        """Clear all data"""
        self.timestamps.clear()
        self.blink_rates.clear()
        self.update_plot()
