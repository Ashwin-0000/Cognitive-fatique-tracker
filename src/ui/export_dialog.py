"""Export dialog for exporting session data"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from src.export.csv_exporter import CSVExporter
from src.export.pdf_exporter import PDFExporter
from src.storage.data_manager import DataManager


class ExportDialog(ctk.CTkToplevel):
    """Dialog for exporting session data and reports"""
    
    def __init__(self, parent, data_manager: DataManager):
        """
        Initialize export dialog.
        
        Args:
            parent: Parent window
            data_manager: DataManager instance
        """
        super().__init__(parent)
        
        self.data_manager = data_manager
        self.csv_exporter = CSVExporter(data_manager)
        self.pdf_exporter = PDFExporter(data_manager)
        
        self.title("Export Data")
        self.geometry("500x450")
        self.resizable(False, False)
        self.transient(parent)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets"""
        # Header
        header = ctk.CTkLabel(
            self,
            text="📊 Export Session Data",
            font=("Segoe UI", 20, "bold")
        )
        header.pack(pady=20)
        
        # Export format
        format_frame = ctk.CTkFrame(self)
        format_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            format_frame,
            text="Export Format:",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=10, pady=5)
        
        self.format_var = ctk.StringVar(value="csv")
        
        ctk.CTkRadioButton(
            format_frame,
            text=" CSV (Sessions)",
            variable=self.format_var,
            value="csv"
        ).pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkRadioButton(
            format_frame,
            text="📄 CSV (Statistics)",
            variable=self.format_var,
            value="csv_stats"
        ).pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkRadioButton(
            format_frame,
            text="📕 PDF (Full Report)",
            variable=self.format_var,
            value="pdf"
        ).pack(anchor="w", padx=20, pady=2)
        
        # Date range
        date_frame = ctk.CTkFrame(self)
        date_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            date_frame,
            text="Date Range:",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", padx=10, pady=5)
        
        self.date_range_var = ctk.StringVar(value="all")
        
        ctk.CTkRadioButton(
            date_frame,
            text="🕐 All Time",
            variable=self.date_range_var,
            value="all"
        ).pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkRadioButton(
            date_frame,
            text="📅 Last 7 Days",
            variable=self.date_range_var,
            value="week"
        ).pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkRadioButton(
            date_frame,
            text="📆 Last 30 Days",
            variable=self.date_range_var,
            value="month"
        ).pack(anchor="w", padx=20, pady=2)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        
        ctk.CTkButton(
            button_frame,
            text="Export",
            command=self._export,
            width=120,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=120
        ).pack(side="left", padx=10)
    
    def _get_date_range(self):
        """Get start and end dates based on selection"""
        range_type = self.date_range_var.get()
        
        if range_type == "all":
            return None, None
        elif range_type == "week":
            return datetime.now() - timedelta(days=7), datetime.now()
        elif range_type == "month":
            return datetime.now() - timedelta(days=30), datetime.now()
    
    def _export(self):
        """Perform export"""
        format_type = self.format_var.get()
        start_date, end_date = self._get_date_range()
        
        # Get file path
        if format_type.startswith("csv"):
            filetypes = [("CSV files", "*.csv"), ("All files", "*.*")]
            default_ext = ".csv"
        else:
            filetypes = [("PDF files", "*.pdf"), ("All files", "*.*")]
            default_ext = ".pdf"
        
        filename = filedialog.asksaveasfilename(
            title="Export Data",
            defaultextension=default_ext,
            filetypes=filetypes
        )
        
        if not filename:
            return
        
        output_path = Path(filename)
        
        # Perform export
        try:
            success = False
            
            if format_type == "csv":
                success = self.csv_exporter.export_sessions(output_path, start_date, end_date)
            elif format_type == "csv_stats":
                success = self.csv_exporter.export_statistics(output_path, start_date, end_date)
            elif format_type == "pdf":
                success = self.pdf_exporter.export_report(output_path, start_date, end_date)
            
            if success:
                messagebox.showinfo(
                    "Export Complete",
                    f"Data exported successfully to:\n{output_path}"
                )
                self.destroy()
            else:
                messagebox.showerror(
                    "Export Failed",
                    "Failed to export data. Check logs for details."
                )
        
        except Exception as e:
            messagebox.showerror(
                "Export Error",
                f"Error during export:\n{str(e)}"
            )
