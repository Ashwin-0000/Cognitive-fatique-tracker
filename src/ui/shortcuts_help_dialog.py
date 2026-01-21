"""Help dialog showing all keyboard shortcuts"""
import customtkinter as ctk


class ShortcutsHelpDialog(ctk.CTkToplevel):
    """Dialog displaying keyboard shortcuts"""

    def __init__(self, parent, shortcuts_list):
        """
        Initialize shortcuts help dialog.

        Args:
            parent: Parent window
            shortcuts_list: List of (key_combination, description) tuples
        """
        super().__init__(parent)

        self.title("Keyboard Shortcuts")
        self.geometry("500x400")
        self.resizable(False, False)

        # Center on parent
        self.transient(parent)

        self._create_widgets(shortcuts_list)

    def _create_widgets(self, shortcuts_list):
        """Create dialog widgets"""
        # Header
        header = ctk.CTkLabel(
            self,
            text="⌨️ Keyboard Shortcuts",
            font=("Segoe UI", 20, "bold")
        )
        header.pack(pady=20)

        # Scrollable frame for shortcuts
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            width=450,
            height=250
        )
        scroll_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Display shortcuts
        for key, description in shortcuts_list:
            self._create_shortcut_row(scroll_frame, key, description)

        # Close button
        close_btn = ctk.CTkButton(
            self,
            text="Close",
            command=self.destroy,
            width=100
        )
        close_btn.pack(pady=20)

    def _create_shortcut_row(self, parent, key, description):
        """Create a row showing a shortcut"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5, padx=10)

        # Key combination (left)
        key_label = ctk.CTkLabel(
            row,
            text=key,
            font=("Consolas", 12, "bold"),
            width=180,
            anchor="w"
        )
        key_label.pack(side="left", padx=(0, 20))

        # Description (right)
        desc_label = ctk.CTkLabel(
            row,
            text=description,
            font=("Segoe UI", 11),
            anchor="w"
        )
        desc_label.pack(side="left", fill="x", expand=True)
