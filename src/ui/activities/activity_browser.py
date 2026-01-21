"""Activity browser widget for selecting and launching refresh activities"""
import customtkinter as ctk
from .activity_definitions import (
    Activity,
    ActivityCategory,
    get_all_activities,
    get_activities_by_category
)
from .activity_demo_window import ActivityDemoWindow


class ActivityBrowser(ctk.CTkFrame):
    """Widget for browsing and selecting cognitive refresh activities"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.current_category = "all"
        self._create_widgets()
    
    def _create_widgets(self):
        """Create all UI widgets"""
        
        # Main container with two columns: Categories sidebar | Activities grid
        self.grid_columnconfigure(0, weight=0)  # Categories sidebar (fixed width)
        self.grid_columnconfigure(1, weight=1)  # Activities grid (fills remaining space)
        self.grid_rowconfigure(0, weight=1)
        
        # ===== CATEGORIES SIDEBAR (LEFT) =====
        categories_sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1e293b", border_width=0)
        categories_sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        categories_sidebar.grid_propagate(False)
        
        # Categories title
        ctk.CTkLabel(
            categories_sidebar,
            text="📂 CATEGORIES",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#3b82f6"
        ).pack(pady=(20, 10), padx=15)
        
        # Separator line
        ctk.CTkFrame(categories_sidebar, height=1, fg_color="#334155").pack(fill="x", padx=10, pady=(0, 15))
        
        # Category buttons
        categories = [
            ("🌟 All Activities", "all", "#3B82F6"),
            ("👁️ Eye Exercises", "eye", "#3B82F6"),
            ("🫁 Breathing", "breathing", "#10B981"),
            ("💪 Physical", "physical", "#F59E0B"),
            ("🧘 Meditation", "meditation", "#8B5CF6"),
            ("⚡ Combos", "combo", "#EC4899")
        ]
        
        self.category_buttons = {}
        for label, cat, color in categories:
            btn_config = {
                "text": label,
                "command": lambda c=cat: self._filter_by_category(c),
                "font": ctk.CTkFont(size=12, weight="bold"),
                "height": 40,
                "corner_radius": 8,
                "fg_color": color if cat == "all" else "transparent",
                "hover_color": "#334155" if cat != "all" else self._darken_color(color),
                "anchor": "w",
                "text_color": "white" if cat == "all" else "#94a3b8",
                "border_width": 2 if cat == "all" else 0,
            }
            
            if cat == "all":
                btn_config["border_color"] = color
            
            btn = ctk.CTkButton(categories_sidebar, **btn_config)
            btn.pack(fill="x", padx=10, pady=3)
            self.category_buttons[cat] = (btn, color)
        
        # Statistics card at bottom
        stats_frame = ctk.CTkFrame(categories_sidebar, fg_color="#0f172a", corner_radius=8, border_width=1, border_color="#334155")
        stats_frame.pack(fill="x", padx=10, pady=15, side="bottom")
        
        total = len(get_all_activities())
        ctk.CTkLabel(
            stats_frame,
            text=f"📊 Total Activities\\n{total}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#3b82f6",
            justify="center"
        ).pack(pady=12)
        
        # ===== ACTIVITIES GRID AREA (RIGHT SIDE - FULL REMAINING SPACE) =====
        # Scrollable container for activities tiles with enhanced color grading
        self.activities_container = ctk.CTkScrollableFrame(
            self,
            fg_color=("#0a0e1a", "#0a0e1a"),  # Deep blue-black for elegant look
            scrollbar_button_color="#5b8dc9",  # Vibrant blue accent
            scrollbar_button_hover_color="#7ba5d4"  # Lighter blue on hover
        )
        self.activities_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        
        # Load all activities initially
        self._load_activities("all")
    
    def _filter_by_category(self, category: str):
        """Filter activities by category"""
        self.current_category = category
        
        # Update button styling (modern dark theme)
        for cat, (btn, color) in self.category_buttons.items():
            if cat == category:
                # Active: colored background with white text
                btn.configure(
                    fg_color=color,
                    text_color="white",
                    border_width=2,
                    border_color=color,
                    hover_color=self._darken_color(color)
                )
            else:
                # Inactive: transparent with muted text
                btn.configure(
                    fg_color="transparent",
                    text_color="#94a3b8",
                    border_width=0,
                    hover_color="#334155"
                )
        
        # Reload activities
        self._load_activities(category)
    
    def _load_activities(self, category: str):
        """Load and display activities"""
        # Clear existing
        for widget in self.activities_container.winfo_children():
            widget.destroy()
        
        # Get activities
        if category == "all":
            activities = get_all_activities()
            header_text = "All Activities"
        else:
            cat_enum = ActivityCategory(category)
            activities = get_activities_by_category(cat_enum)
            category_names = {
                "eye": "Eye Exercises",
                "breathing": "Breathing Exercises",
                "physical": "Physical Exercises",
                "meditation": "Meditation Exercises",
                "combo": "Combination Activities"
            }
            header_text = category_names.get(category, "Activities")
        
        # Create responsive grid with full width expansion
        activities_grid = ctk.CTkFrame(self.activities_container, fg_color="transparent")
        activities_grid.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Configure grid columns to expand evenly with 4 columns to fill full width
        activities_grid.grid_columnconfigure(0, weight=1, uniform="cards", minsize=320)
        activities_grid.grid_columnconfigure(1, weight=1, uniform="cards", minsize=320)
        activities_grid.grid_columnconfigure(2, weight=1, uniform="cards", minsize=320)
        activities_grid.grid_columnconfigure(3, weight=1, uniform="cards", minsize=320)
        
        # Sort by effectiveness
        activities.sort(key=lambda a: a.effectiveness_rating, reverse=True)
        
        # Create cards in 4-column grid for full-width responsive tiles
        for i, activity in enumerate(activities):
            self._create_activity_card(activities_grid, activity, row=i // 4, col=i % 4)
    
    def _create_activity_card(self, parent, activity: Activity, row: int, col: int):
        """Create a card for an activity - matching Analytics container style"""
        # Card with enhanced color grading for modern aesthetic
        card = ctk.CTkFrame(
            parent,
            corner_radius=14,
            fg_color="#1a2332",  # Deeper blue-grey for cards
            border_width=2,  # Increased border width for prominence
            border_color="#3d5a80"  # Vibrant blue accent border
        )
        # Padding between cards: right padding on columns 0-2, no padding on column 3
        padx = (0, 18) if col < 3 else (0, 0)
        card.grid(row=row, column=col, padx=padx, pady=(0, 18), sticky="nsew")
        
        # Configure grid for 4 columns
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)
        parent.grid_columnconfigure(3, weight=1)
        
        # Content with generous padding for breathing room
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Category badge (vibrant accent)
        icons = {
            "eye": "👁️",
            "breathing": "🫁",
            "physical": "💪",
            "meditation": "🧘",
            "combo": "⚡"
        }
        icon = icons.get(activity.category.value, "✨")
        
        badge_frame = ctk.CTkFrame(content, fg_color=activity.color, corner_radius=6, height=26)
        badge_frame.pack(anchor="w")
        badge_frame.pack_propagate(False)
        
        badge = ctk.CTkLabel(
            badge_frame,
            text=f"{icon} {activity.category.value.upper()}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="white"
        )
        badge.pack(padx=10, pady=3)
        
        # Activity name (white text) with more space
        name = ctk.CTkLabel(
            content,
            text=activity.name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white",
            anchor="w"
        )
        name.pack(fill="x", pady=(15, 8))
        
        # Description (muted gray matching Analytics labels) with more space
        desc = ctk.CTkLabel(
            content,
            text=activity.description,
            font=ctk.CTkFont(size=13),
            anchor="w",
            justify="left",
            text_color="#94a3b8"
        )
        desc.pack(fill="x", pady=(0, 15))
        
        # Metadata row with more spacing
        meta_frame = ctk.CTkFrame(content, fg_color="transparent")
        meta_frame.pack(fill="x", pady=(8, 15))
        
        # Duration
        duration_text = f"⏱️ {activity.duration_seconds // 60}m"
        if activity.duration_seconds % 60:
            duration_text += f" {activity.duration_seconds % 60}s"
        
        duration = ctk.CTkLabel(
            meta_frame,
            text=duration_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#94a3b8"
        )
        duration.pack(side="left")
        
        # Separator
        sep = ctk.CTkLabel(
            meta_frame,
            text="  •  ",
            font=ctk.CTkFont(size=12),
            text_color="#475569"
        )
        sep.pack(side="left")
        
        # Effectiveness stars
        stars = "⭐" * int(activity.effectiveness_rating)
        effectiveness = ctk.CTkLabel(
            meta_frame,
            text=stars,
            font=ctk.CTkFont(size=12)
        )
        effectiveness.pack(side="left")
        
        # Try button (matching app button style) with more height
        try_btn = ctk.CTkButton(
            content,
            text="▶️ Try This Activity",
            command=lambda a=activity: self._open_activity_demo(a),
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=activity.color,
            hover_color=self._darken_color(activity.color),
            height=45,
            corner_radius=10,
            border_width=2,
            border_color=self._brighten_color(activity.color)
        )
        try_btn.pack(fill="x", pady=(8, 0))
    
    def _open_activity_demo(self, activity: Activity):
        """Open the activity demo window"""
        top_level = self.winfo_toplevel()
        demo_window = ActivityDemoWindow(top_level, activity)
    
    def _darken_color(self, hex_color: str) -> str:
        """Darken a hex color for hover effect"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * 0.75), int(g * 0.75), int(b * 0.75)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _brighten_color(self, hex_color: str) -> str:
        """Brighten a hex color for border effect"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, int(r * 1.3))
        g = min(255, int(g * 1.3))
        b = min(255, int(b * 1.3))
        return f"#{r:02x}{g:02x}{b:02x}"
