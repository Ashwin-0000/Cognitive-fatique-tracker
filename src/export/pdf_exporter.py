"""PDF export functionality with charts and reports"""
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import io

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfgen import canvas

from src.storage.data_manager import DataManager
from src.utils.logger import default_logger as logger


class PDFExporter:
    """Export session data and charts to PDF format"""

    def __init__(self, data_manager: DataManager):
        """
        Initialize PDF exporter.

        Args:
            data_manager: DataManager instance
        """
        self.data_manager = data_manager
        self.styles = getSampleStyleSheet()

        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12
        )

    def export_report(
        self,
        output_file: Path,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_charts: bool = True
    ) -> bool:
        """
        Export comprehensive report to PDF.

        Args:
            output_file: Output PDF file path
            start_date: Start date filter
            end_date: End date filter
            include_charts: Whether to include charts

        Returns:
            True if export successful
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_file),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )

            # Container for PDF elements
            story = []

            # Title
            title = Paragraph(
                "Cognitive Fatigue Tracker Report",
                self.title_style)
            story.append(title)
            story.append(Spacer(1, 12))

            # Date range
            date_range = f"Report Period: {start_date.strftime('%Y-%m-%d') if start_date else 'All Time'} to {end_date.strftime('%Y-%m-%d') if end_date else 'Present'}"
            story.append(Paragraph(date_range, self.styles['Normal']))
            story.append(Spacer(1, 20))

            # Get sessions
            sessions = self.data_manager.get_all_sessions(start_date, end_date)

            if not sessions:
                story.append(
                    Paragraph(
                        "No sessions found in the specified period.",
                        self.styles['Normal']))
            else:
                # Summary statistics
                story.append(
                    Paragraph(
                        "Summary Statistics",
                        self.heading_style))
                story.append(self._create_summary_table(sessions))
                story.append(Spacer(1, 20))

                # Sessions table
                story.append(Paragraph("Session Details", self.heading_style))
                story.append(self._create_sessions_table(sessions))
                story.append(PageBreak())

            # Build PDF
            doc.build(story)

            logger.info(f"Exported PDF report to {output_file}")
            return True

        except Exception as e:
            logger.error(f"Error exporting PDF: {e}")
            return False

    def _create_summary_table(self, sessions: List) -> Table:
        """Create summary statistics table"""
        total_duration = sum(
            s.get_stats()['total_duration_minutes'] for s in sessions)
        total_work = sum(
            s.get_stats()['work_duration_minutes'] for s in sessions)
        total_breaks = sum(s.get_stats()['break_count'] for s in sessions)

        data = [
            ['Metric', 'Value'],
            ['Total Sessions', str(len(sessions))],
            ['Total Time', f"{total_duration/60:.1f} hours"],
            ['Total Work Time', f"{total_work/60:.1f} hours"],
            ['Total Breaks', str(total_breaks)],
            ['Avg Session Length', f"{total_duration/len(sessions):.0f} min"],
            ['Avg Breaks/Session', f"{total_breaks/len(sessions):.1f}"]
        ]

        table = Table(data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        return table

    def _create_sessions_table(self, sessions: List) -> Table:
        """Create detailed sessions table"""
        data = [['Date', 'Duration', 'Work Time', 'Breaks', 'Activities']]

        for session in sessions[:20]:  # Limit to 20 most recent
            stats = session.get_stats()
            data.append([
                session.start_time.strftime('%Y-%m-%d %H:%M'),
                f"{stats['total_duration_minutes']:.0f} min",
                f"{stats['work_duration_minutes']:.0f} min",
                str(stats['break_count']),
                str(stats['total_activity_count'])
            ])

        table = Table(
            data,
            colWidths=[
                1.5 * inch,
                1 * inch,
                1 * inch,
                0.8 * inch,
                1 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        return table
