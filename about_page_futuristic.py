"""
Futuristic About Page Design - Complete Replacement

Replace the _create_about_page method in main_window.py (lines ~658-865) with this code:
"""

def _create_about_page(self):
    """Create futuristic About page with gradient hero and modern cards"""
    # Deep space background
    page = ctk.CTkScrollableFrame(
        self.content_frame,
        fg_color="#0a0e1a",
        scrollbar_button_color="#1e3a8a",
        scrollbar_button_hover_color="#2563eb"
    )
    page.grid_columnconfigure(0, weight=1)
    
    # === HERO SECTION with Gradient ===
    hero = ctk.CTkFrame(page, fg_color="#1e1b4b", height=280, corner_radius=0)
    hero.grid(row=0, column=0, sticky="ew")
    hero.grid_columnconfigure(0, weight=1)
    hero.grid_propagate(False)
    
    ctk.CTkLabel(
        hero, text="⚡ COGNITIVE FATIGUE TRACKER",
        font=ctk.CTkFont(size=42, weight="bold"),
        text_color="#60a5fa"
    ).grid(row=0, column=0, pady=(50, 10))
    
    ctk.CTkLabel(
        hero, text="Advanced AI-Powered Cognitive Performance Monitoring",
        font=ctk.CTkFont(size=14), text_color="#94a3b8"
    ).grid(row=1, column=0, pady=(0, 15))
    
    # Version badge
    badge = ctk.CTkFrame(hero, fg_color="#1e3a8a", corner_radius=20)
    badge.grid(row=2, column=0, pady=(0, 40))
    ctk.CTkLabel(
        badge, text="🚀 v1.0.0  |  Python 3.11+  |  Production",
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color="#ffffff"
    ).pack(padx=20, pady=8)
    
    # === FEATURES GRID (2 columns) ===
    features_container = ctk.CTkFrame(page, fg_color="transparent")
    features_container.grid(row=1, column=0, sticky="ew", padx=30, pady=20)
    features_container.grid_columnconfigure((0, 1), weight=1)
    
    features = [
        ("📊", "Real-Time Monitoring", "ML-powered fatigue tracking", "#3b82f6"),
        ("🖱️", "Activity Tracking", "Keyboard & mouse analysis", "#f97316"),
        ("👁️", "Eye Tracking", "Blink rate with MediaPipe", "#8b5cf6"),
        ("🤖", "AI Predictions", "Personalized ML models", "#10b981"),
        ("📈", "Analytics", "Beautiful visualizations", "#0ea5e9"),
        ("⚠️", "Smart Alerts", "Intelligent reminders", "#f59e0b"),
    ]
    
    for idx, (icon, title, desc, color) in enumerate(features):
        card = ctk.CTkFrame(
            features_container, fg_color="#1e293b",
            corner_radius=16, border_width=2, border_color="#334155"
        )
        card.grid(row=idx//2, column=idx%2, padx=8, pady=8, sticky="nsew")
        
        # Colored icon circle
        icon_bg = ctk.CTkFrame(card, fg_color=color, corner_radius=12, width=50, height=50)
        icon_bg.pack(pady=(20, 10))
        icon_bg.pack_propagate(False)
        ctk.CTkLabel(icon_bg, text=icon, font=ctk.CTkFont(size=24)).pack(expand=True)
        
        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=16, weight="bold"), 
                     text_color="#e2e8f0").pack(pady=(0, 5))
        ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=12), 
                     text_color="#94a3b8", wraplength=200).pack(pady=(0, 20))
    
    # === TECH STACK SECTION ===
    tech_section = ctk.CTkFrame(page, fg_color="transparent")
    tech_section.grid(row=2, column=0, sticky="ew", padx=30, pady=(20, 0))
    tech_section.grid_columnconfigure(0, weight=1)
    
    ctk.CTkLabel(
        tech_section, text="🔧 POWERED BY CUTTING-EDGE TECHNOLOGY",
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color="#60a5fa"
    ).grid(row=0, column=0, pady=(0, 20))
    
    tech_grid = ctk.CTkFrame(tech_section, fg_color="transparent")
    tech_grid.grid(row=1, column=0, sticky="ew")
    tech_grid.grid_columnconfigure((0, 1, 2), weight=1)
    
    tech_stack = [
        ("CustomTkinter", "Modern UI Framework", "#3b82f6"),
        ("MediaPipe", "Eye Tracking AI", "#10b981"),
        ("scikit-learn", "Machine Learning", "#f97316"),
        ("Matplotlib", "Data Visualization", "#8b5cf6"),
        ("pynput", "Input Monitoring", "#0ea5e9"),
        ("SQLite", "Data Storage", "#f59e0b"),
    ]
    
    for idx, (name, desc, color) in enumerate(tech_stack):
        card = ctk.CTkFrame(
            tech_grid, fg_color="#1e293b",
            corner_radius=12, border_width=1, border_color=color
        )
        card.grid(row=idx//3, column=idx%3, padx=6, pady=6, sticky="nsew")
        
        # Colored top bar
        ctk.CTkFrame(card, fg_color=color, height=4, corner_radius=2).pack(fill="x")
        ctk.CTkLabel(card, text=name, font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#e2e8f0").pack(pady=(12, 3))
        ctk.CTkLabel(card, text=desc, font=ctk.CTkFont(size=11),
                     text_color="#64748b").pack(pady=(0, 12))
    
    # === FOOTER ===
    footer = ctk.CTkFrame(page, fg_color="#1e293b", corner_radius=16, height=80)
    footer.grid(row=3, column=0, sticky="ew", padx=30, pady=(30, 20))
    footer.grid_columnconfigure(0, weight=1)
    footer.grid_propagate(False)
    
    ctk.CTkLabel(
        footer, text="💡 Built with Python • Designed for Peak Performance",
        font=ctk.CTkFont(size=13, weight="bold"), text_color="#60a5fa"
    ).grid(row=0, column=0, pady=(20, 5))
    
    ctk.CTkLabel(
        footer, text="© 2025 Cognitive Fatigue Tracker • Advanced Productivity Tool",
        font=ctk.CTkFont(size=11), text_color="#64748b"
    ).grid(row=1, column=0, pady=(0, 15))
    
    self.pages["About"] = page
