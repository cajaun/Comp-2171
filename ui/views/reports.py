import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ui.styles import *


class ReportsView(ttk.Frame):
    def __init__(self, parent, report_service, current_user):
        super().__init__(parent, style="TFrame")
        self.report_service = report_service
        self.current_user = current_user
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        container = ttk.Frame(self, padding=(20, 0, 20, 20))
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(20, 20))
        ttk.Label(header, text="Reports", style="H1.TLabel").pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")
        ttk.Button(actions, text="Generate New Report", style="Primary.TButton", command=self.generate_report_dialog).pack(side="left", padx=5)

        self.tree = ttk.Treeview(container, columns=("ID", "Type", "Format", "Generated At", "User"), show="headings")
        for column in ("ID", "Type", "Format", "Generated At", "User"):
            self.tree.heading(column, text=column, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.download_report)

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            for report in self.report_service.list_reports():
                generated_at = report.generated_at.strftime("%Y-%m-%d %H:%M") if report.generated_at else "N/A"
                self.tree.insert(
                    "",
                    "end",
                    values=(report.report_id, report.report_type, report.format_type, generated_at, report.user_name),
                )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def generate_report_dialog(self):
        top = tk.Toplevel(self)
        top.title("Generate Report")
        top.geometry("350x300")
        top.configure(bg=BACKGROUND)
        ttk.Label(top, text="Generate Report", style="H2.TLabel").pack(pady=20)

        type_var = tk.StringVar(value="Inventory")
        format_var = tk.StringVar(value="CSV")

        for label, variable, values in [
            ("Report Type", type_var, ["Inventory", "Sales", "Category", "Low Stock"]),
            ("Format", format_var, ["CSV", "PDF"]),
        ]:
            frame = ttk.Frame(top, padding=10)
            frame.pack(fill="x")
            ttk.Label(frame, text=label).pack(anchor="w")
            ttk.Combobox(frame, textvariable=variable, values=values).pack(fill="x")

        def generate():
            try:
                report = self.report_service.generate_report(
                    type_var.get(),
                    format_var.get(),
                    self.current_user.user_id if self.current_user else None,
                )
                if not report:
                    messagebox.showinfo("Info", "No data available")
                    return
                messagebox.showinfo("Success", "Report generated")
                self.refresh_data()
                top.destroy()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ttk.Button(top, text="Generate", command=generate).pack(pady=10)

    def download_report(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        report_id = self.tree.item(selected[0])["values"][0]

        try:
            download = self.report_service.get_report_download(report_id)
            file_path = filedialog.asksaveasfilename(defaultextension=f".{download.filename.split('.')[-1]}", initialfile=download.filename)
            if not file_path:
                return
            mode = "wb" if download.is_binary else "w"
            with open(file_path, mode) as handle:
                handle.write(download.content)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
