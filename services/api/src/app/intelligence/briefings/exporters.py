from abc import ABC, abstractmethod
from typing import Any

from app.intelligence.briefings.models import BriefingReport


class BriefingExporter(ABC):
    """Abstract interface for exporting executive briefings to different formats."""

    @abstractmethod
    def export(self, report: BriefingReport) -> Any:
        """Processes a BriefingReport and generates formatted output."""

class MarkdownExporter(BriefingExporter):
    """Generates clean, professional markdown strings of the executive briefing."""

    def export(self, report: BriefingReport) -> str:
        """Converts structured Pydantic report details into markdown syntax."""
        md = []
        md.append("# Executive Briefing Report")
        md.append("")
        md.append("## 1. Executive Summary")
        md.append(report.executive_summary)
        md.append("")
        md.append("## 2. Key Metrics")
        for k, v in report.key_metrics.items():
            name = k.replace("_", " ").title()
            md.append(f"* **{name}**: {v}")
        md.append("")
        md.append("## 3. Operational Highlights")
        for h in report.operational_highlights:
            md.append(f"* {h}")
        md.append("")
        md.append("## 4. Major Incidents")
        for i in report.major_incidents:
            md.append(f"* {i}")
        md.append("")
        md.append("## 5. AI Recommendations")
        for r in report.ai_recommendations:
            md.append(f"* {r}")
        md.append("")
        md.append("## 6. Risk Assessment")
        md.append(report.risk_assessment)
        md.append("")
        md.append("## 7. Suggested Next Actions")
        for a in report.suggested_next_actions:
            md.append(f"* {a}")

        return "\n".join(md)

class PDFExporter(BriefingExporter):
    """Generates PDF documents representing the executive briefing."""

    def export(self, report: BriefingReport) -> bytes:
        """Mock PDF compile that prepends standard PDF headers before raw text."""
        md_content = MarkdownExporter().export(report)
        pdf_header = b"%PDF-1.4\n%...\n"
        content_bytes = md_content.encode("utf-8")
        return pdf_header + content_bytes
