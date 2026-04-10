from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

from sqlalchemy.orm import joinedload

from data.models import Category, Item, Report, StockAdjust, User
from services.base import ServiceBase
from services.view_models import ReportDownload, ReportRecord


class ReportService(ServiceBase):
    def list_reports(self) -> list[ReportRecord]:
        with self.session_scope() as session:
            reports = (
                session.query(Report)
                .options(joinedload(Report.user))
                .order_by(Report.generated_at.desc())
                .all()
            )
            return [
                ReportRecord(
                    report_id=report.report_id,
                    report_type=report.report_type,
                    format_type=self._get_format(report),
                    generated_at=report.generated_at,
                    user_name=report.user.username if report.user else "Unknown",
                )
                for report in reports
            ]

    def generate_report(self, report_type: str, format_type: str, actor_user_id: int | None) -> ReportRecord | None:
        format_type = format_type.upper().strip()
        if format_type not in {"CSV", "PDF"}:
            raise ValueError("Format must be CSV or PDF")

        with self.session_scope() as session:
            rows = self._build_rows(session, report_type.strip())
            if len(rows) <= 1:
                return None

            report = Report(
                report_type=report_type.strip(),
                generated_at=datetime.now(timezone.utc),
                user_id=actor_user_id,
                parameters=f"Format: {format_type}",
                report_data=self._format_csv(rows),
            )
            session.add(report)
            session.flush()

            user = session.get(User, actor_user_id) if actor_user_id else None
            return ReportRecord(
                report_id=report.report_id,
                report_type=report.report_type,
                format_type=format_type,
                generated_at=report.generated_at,
                user_name=user.username if user else "Unknown",
            )

    def get_report_download(self, report_id: int) -> ReportDownload:
        with self.session_scope() as session:
            report = session.get(Report, report_id)
            if not report:
                raise ValueError("Report not found")
            format_type = self._get_format(report)
            filename = f"{report.report_type.lower().replace(' ', '_')}_{report.report_id}.{format_type.lower()}"
            if format_type == "CSV":
                return ReportDownload(filename=filename, content=report.report_data or "", is_binary=False)

            reader = csv.reader(io.StringIO(report.report_data or ""))
            rows = list(reader)
            return ReportDownload(
                filename=filename,
                content=self._format_pdf(rows, report.report_type),
                is_binary=True,
            )

    def _build_rows(self, session, report_type: str) -> list[list[object]]:
        if report_type == "Inventory":
            items = session.query(Item).all()
            rows = [["ID", "Name", "Category", "Price", "Stock", "Value"]]
            for item in items:
                category_name = item.category.name if item.category else "-"
                rows.append(
                    [
                        item.item_id,
                        item.name,
                        category_name,
                        item.price,
                        item.current_stock,
                        (item.price or 0) * (item.current_stock or 0),
                    ]
                )
            return rows

        if report_type == "Sales":
            adjustments = session.query(StockAdjust).filter(StockAdjust.adjust_type == "Decrease").all()
            rows = [["ID", "Item", "Qty Sold", "Reason", "Date", "Revenue"]]
            for adjustment in adjustments:
                item_name = adjustment.item.name if adjustment.item else "Unknown"
                price = adjustment.item.price if adjustment.item else 0
                rows.append(
                    [
                        adjustment.adjust_id,
                        item_name,
                        adjustment.quantity,
                        adjustment.reason,
                        adjustment.created_at,
                        (price or 0) * (adjustment.quantity or 0),
                    ]
                )
            return rows

        if report_type == "Low Stock":
            items = session.query(Item).all()
            rows = [["ID", "Name", "Stock", "Reorder Level"]]
            for item in items:
                reorder_level = item.reorder_level or 10
                if (item.current_stock or 0) < reorder_level:
                    rows.append([item.item_id, item.name, item.current_stock, reorder_level])
            return rows

        if report_type == "Category":
            categories = session.query(Category).all()
            rows = [["ID", "Name", "Description", "Items"]]
            for category in categories:
                rows.append(
                    [
                        category.category_id,
                        category.name,
                        category.description,
                        len(category.items),
                    ]
                )
            return rows

        raise ValueError("Invalid report type")

    def _get_format(self, report: Report) -> str:
        return "PDF" if report.parameters and "PDF" in report.parameters else "CSV"

    def _format_csv(self, rows: list[list[object]]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(rows)
        return output.getvalue()

    def _format_pdf(self, rows: list[list[object]], title: str) -> bytes:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages

        buffer = io.BytesIO()
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("tight")
        ax.axis("off")
        ax.set_title(title, fontsize=16, fontweight="bold")

        if len(rows) > 1:
            table = ax.table(cellText=rows[1:], colLabels=rows[0], loc="center", cellLoc="center")
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)
        else:
            ax.text(0.5, 0.5, "No Data", ha="center", va="center")

        with PdfPages(buffer) as pdf:
            pdf.savefig(fig, bbox_inches="tight")

        plt.close(fig)
        buffer.seek(0)
        return buffer.getvalue()
