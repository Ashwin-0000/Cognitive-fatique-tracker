"""Statistics Page UI"""
import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox

from src.analysis.statistics import StatisticsManager
from src.utils.logger import default_logger as logger

class StatisticsPage(ctk.CTkFrame):
    """Statistics Dashboard Page"""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent, fg_color="transparent")
        
        self.stats_manager = StatisticsManager(data_manager)
        self._create_widgets()
        self.refresh()
        
    def _create_widgets(self):
        """Create UI layout"""
        # Grid layout: Header, Cards, Charts
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=0) # Cards
        self.grid_rowconfigure(2, weight=1) # Charts

        # --- HEADER ROW ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 0))
        
        ctk.CTkLabel(
            header_frame, 
            text="Statistics Dashboard", 
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header_frame,
            text="⬇️ Export Report",
            command=self.export_report,
            width=120,
            fg_color="#3b82f6", hover_color="#2563eb"
        ).pack(side="right")
        
        # --- CARDS ROW ---
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(10, 20))
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # 1. Productivity Card
        self.prod_card = self._create_metric_card(
            cards_frame, 
            "⚡ Productivity",
            "Focus Score", "0.0",
            "Peak Hour", "--:--"
        )
        self.prod_card.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # 2. Effectiveness Card
        self.effect_card = self._create_metric_card(
            cards_frame,
            "🧘 Effectiveness",
            "Recovery", "0.0",
            "Breaks", "0"
        )
        self.effect_card.grid(row=0, column=1, sticky="ew", padx=5)

        # 3. Screen Time Card
        self.time_card = self._create_metric_card(
            cards_frame,
            "⏱️ Screen Time",
            "Today", "0h 0m",
            "Status", "Active"
        )
        self.time_card.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        
        # --- CHARTS ROW ---
        charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        charts_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        charts_frame.grid_columnconfigure(0, weight=3) # Main chart
        charts_frame.grid_columnconfigure(1, weight=2) # Badges panel (smaller than chart)
        charts_frame.grid_rowconfigure(0, weight=1)

        # Chart 1: Weekly Overview
        self.chart_container = ctk.CTkFrame(
            charts_frame, 
            fg_color="#1e293b",
            corner_radius=14, border_width=1, border_color="#334155"
        )
        self.chart_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ctk.CTkLabel(
            self.chart_container, text="📅 Weekly Overview",
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#3b82f6"
        ).pack(anchor="w", padx=20, pady=15)
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.figure.patch.set_facecolor('#1e293b')
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1e293b')
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Right Panel: Badges & Fatigue Zones
        right_panel = ctk.CTkFrame(charts_frame, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(0, weight=1) # Badges
        right_panel.grid_rowconfigure(1, weight=1) # Pie
        right_panel.grid_columnconfigure(0, weight=1)

        # 1. Badges Panel
        self.badges_container = ctk.CTkFrame(
            right_panel,
            fg_color="#1e293b",
            corner_radius=14, border_width=1, border_color="#334155"
        )
        self.badges_container.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        ctk.CTkLabel(
            self.badges_container, text="🏆 Achievements",
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#facc15"
        ).pack(anchor="w", padx=20, pady=15)
        
        self.badges_frame = ctk.CTkFrame(self.badges_container, fg_color="transparent")
        self.badges_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 2. Fatigue Zones
        self.pie_container = ctk.CTkFrame(
            right_panel,
            fg_color="#1e293b",
            corner_radius=14, border_width=1, border_color="#334155"
        )
        self.pie_container.grid(row=1, column=0, sticky="nsew")

        ctk.CTkLabel(
            self.pie_container, text="📊 Fatigue Zones",
            font=ctk.CTkFont(size=18, weight="bold"), text_color="#f97316"
        ).pack(anchor="w", padx=20, pady=10)

        self.pie_figure = Figure(figsize=(4, 3), dpi=100)
        self.pie_figure.patch.set_facecolor('#1e293b')
        self.pie_ax = self.pie_figure.add_subplot(111)
        
        self.pie_canvas = FigureCanvasTkAgg(self.pie_figure, master=self.pie_container)
        self.pie_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
    def _create_metric_card(self, parent, title, label1, val1, label2, val2):
        """Create a standardized metric card"""
        card = ctk.CTkFrame(parent, corner_radius=14, fg_color="#1e293b", border_width=1, border_color="#334155")
        
        # Title
        ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=16, weight="bold"), text_color="#f97316"
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Content Grid
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=(0, 20))
        content.grid_columnconfigure((0, 1), weight=1)
        
        # Metric 1
        m1 = ctk.CTkFrame(content, fg_color="transparent")
        m1.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(m1, text=label1, font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(anchor="w")
        l1 = ctk.CTkLabel(m1, text=val1, font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        l1.pack(anchor="w")
        
        # Metric 2
        m2 = ctk.CTkFrame(content, fg_color="transparent")
        m2.grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(m2, text=label2, font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(anchor="w")
        l2 = ctk.CTkLabel(m2, text=val2, font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        l2.pack(anchor="w")
        
        # Store references to labels for updating
        card.labels = {label1: l1, label2: l2}
        return card

    def refresh(self):
        """Refresh all data"""
        try:
            # 1. Update Productivity
            prod_stats = self.stats_manager.get_productivity_stats()
            self.prod_card.labels["Focus Score"].configure(text=f"{prod_stats['focus_score']}/min")
            self.prod_card.labels["Peak Hour"].configure(text=prod_stats['peak_hour'])
            
            # 2. Update Effectiveness
            eff_stats = self.stats_manager.get_break_effectiveness()
            self.effect_card.labels["Recovery"].configure(text=f"-{eff_stats['recovery_rate']}")
            self.effect_card.labels["Breaks"].configure(text=str(eff_stats['total_breaks']))
            
            # 3. Update Screen Time
            screen_time = self.stats_manager.get_daily_screen_time()
            self.time_card.labels["Today"].configure(text=screen_time)
            
            # 4. Badges
            self._update_badges()

            # 5. Update Charts
            self._update_chart()
            self._update_pie_chart()
            
        except Exception as e:
            logger.error(f"Error refreshing statistics: {e}")

    def _update_badges(self):
        """Update achievements/badges"""
        # Clear existing
        for widget in self.badges_frame.winfo_children():
            widget.destroy()
            
        badges = self.stats_manager.get_weekly_badges()
        
        for badge in badges:
            b_frame = ctk.CTkFrame(self.badges_frame, fg_color="transparent")
            b_frame.pack(fill="x", pady=5)
            
            # Icon
            ctk.CTkLabel(
                b_frame, text=badge['icon'], 
                font=ctk.CTkFont(size=24)
            ).pack(side="left", padx=10)
            
            # Text
            text_frame = ctk.CTkFrame(b_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(
                text_frame, text=badge['name'],
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=badge.get('color', 'white')
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                text_frame, text=badge['description'],
                font=ctk.CTkFont(size=11),
                text_color="#94a3b8"
            ).pack(anchor="w")

    def _update_chart(self):
        """Draw weekly overview chart"""
        self.ax.clear()
        
        summary = self.stats_manager.get_weekly_summary()
        if not summary:
            return
            
        dates = [d['date'] for d in summary]
        hours = [d['active_hours'] for d in summary]
        fatigue = [d['avg_fatigue'] for d in summary]
        
        # Dual axis
        ax1 = self.ax
        ax2 = ax1.twinx()
        
        # Bar Chart (Hours)
        x = np.arange(len(dates))
        width = 0.5
        bars = ax1.bar(x, hours, width, label='Active Hours', color='#3b82f6', alpha=0.7)
        
        # Line Chart (Fatigue)
        line = ax2.plot(x, fatigue, label='Avg Fatigue', color='#f97316', marker='o', linewidth=2)
        
        # Styling
        ax1.set_ylabel('Active Hours', color='#3b82f6')
        ax2.set_ylabel('Fatigue Score', color='#f97316')
        
        ax1.tick_params(axis='y', colors='#94a3b8')
        ax2.tick_params(axis='y', colors='#94a3b8')
        ax1.tick_params(axis='x', colors='#94a3b8')
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(dates)
        
        # Spines
        for ax in [ax1, ax2]:
            ax.spines['bottom'].set_color('#334155')
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_color('#334155')
            ax.spines['right'].set_visible(False)
            
        self.canvas.draw()
            
    def _update_pie_chart(self):
        """Draw fatigue distribution pie chart"""
        self.pie_ax.clear()
        
        dist = self.stats_manager.get_fatigue_distribution()
        if not dist or sum(dist.values()) == 0:
            self.pie_ax.text(0.5, 0.5, "No Data", ha='center', va='center', color='gray')
            self.pie_canvas.draw()
            return
            
        # Data
        labels = []
        sizes = []
        colors = []
        color_map = {
            'Low': '#22c55e',      # Green
            'Medium': '#eab308',   # Yellow
            'High': '#f97316',     # Orange
            'Critical': '#ef4444'  # Red
        }
        
        for k, v in dist.items():
            if v > 0:
                labels.append(k)
                sizes.append(v)
                colors.append(color_map.get(k, 'gray'))
                
        # Draw Pie
        wedges, _ = self.pie_ax.pie(
            sizes, 
            labels=None, # Hide labels on chart to reduce clutter
            colors=colors,
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor='#1e293b') # Donut style
        )
        
        # Center Text
        self.pie_ax.text(0, 0, f"{len(sizes)}\nZones", ha='center', va='center', color='white', fontweight='bold')
        
        # Legend (Custom using matplotlib)
        self.pie_ax.legend(
            wedges, 
            [f"{l}: {s}%" for l, s in zip(labels, sizes)],
            loc="center",
            bbox_to_anchor=(0.5, -0.1),
            frameon=False,
            labelcolor='white',
            ncol=2,
            fontsize=8
        )
        
        self.pie_canvas.draw()

    def export_report(self):
        """Export statistics to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Statistics Report",
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
            )
            
            if filename:
                self.stats_manager.export_statistics(filename)
                messagebox.showinfo("Export Successful", f"Report saved to:\n{filename}")
                logger.info(f"Statistics exported to {filename}")
                
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            messagebox.showerror("Export Failed", f"An error occurred:\n{e}")
