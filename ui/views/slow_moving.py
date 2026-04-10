import tkinter as tk
from tkinter import messagebox, ttk

from ui.components.rounded_shapes import RoundedFrame
from ui.styles import *


class SlowMovingView(ttk.Frame):
    def __init__(self, parent, slow_moving_service):
        super().__init__(parent, style="TFrame")
        self.slow_moving_service = slow_moving_service
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        container = ttk.Frame(self, padding=(20, 0, 20, 20))
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(20, 20))
        ttk.Label(header, text="Slow Moving & Overstock", style="H1.TLabel").pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")
        ttk.Button(actions, text="Configure & Scan", style="Primary.TButton", command=self.configure_dialog).pack(side="left", padx=5)

        stats_frame = ttk.Frame(container)
        stats_frame.pack(fill="x", pady=(0, 20))
        for index in range(4):
            stats_frame.grid_columnconfigure(index, weight=1)

        self.create_stat_card(stats_frame, "Total Slow-Moving Items", "0", "Flagged products", 0)
        self.create_stat_card(stats_frame, "Value Locked in Slow Stock", "$0.00", "Capital tied up", 1)
        self.create_stat_card(stats_frame, "Oldest Slow-Moving Product", "-", "Longest unsold", 2)
        self.create_stat_card(stats_frame, "Overstock Count", "0", "Excess inventory", 3)

        self.tree = ttk.Treeview(container, columns=("ID", "Item", "Stock", "Last Sold", "Days Since", "Suggestion"), show="headings")
        for column in ("ID", "Item", "Stock", "Last Sold", "Days Since", "Suggestion"):
            self.tree.heading(column, text=column, anchor="center")
        self.tree.pack(fill="both", expand=True)

    def create_card_frame(self, parent, row, col):
        card = RoundedFrame(parent, fg_color=CARD, border_width=1, border_color=BORDER, padding=20)
        card.grid(row=row, column=col, sticky="nsew", padx=10)
        return card.inner_frame

    def create_stat_card(self, parent, title, value, description, col_index):
        inner = self.create_card_frame(parent, 0, col_index)
        ttk.Label(inner, text=title, style="CardTitle.TLabel").pack(anchor="w")
        label_value = ttk.Label(inner, text=value, style="CardValue.TLabel")
        label_value.pack(anchor="w", pady=(5, 0))
        ttk.Label(inner, text=description, style="CardSub.TLabel").pack(anchor="w")

        if title == "Total Slow-Moving Items":
            self.lbl_total = label_value
        elif title == "Value Locked in Slow Stock":
            self.lbl_value_locked = label_value
        elif title == "Oldest Slow-Moving Product":
            self.lbl_oldest = label_value
        elif title == "Overstock Count":
            self.lbl_overstock = label_value

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            flags = self.slow_moving_service.list_flags()
            stats = self.slow_moving_service.get_stats()
            self.lbl_total.config(text=str(stats.total))
            self.lbl_value_locked.config(text=f"${stats.value_locked:.2f}")
            self.lbl_oldest.config(text=stats.oldest)
            self.lbl_overstock.config(text=str(stats.overstock))

            for flag in flags:
                last = flag.last_sold_date.strftime("%Y-%m-%d") if flag.last_sold_date else "N/A"
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        flag.sm_id,
                        flag.item_name,
                        flag.stock_quantity,
                        last,
                        flag.days_since if flag.days_since is not None else "N/A",
                        flag.suggested_action,
                    ),
                )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def configure_dialog(self):
        self.show_dialog("Scan Configuration")

    def show_dialog(self, title):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("350x350")
        top.configure(bg=BACKGROUND)
        ttk.Label(top, text=title, style="H2.TLabel").pack(pady=20)

        config = self.slow_moving_service.get_configuration()
        days_entry = self._entry_field(top, "Days Threshold (No Sale)", str(config.days_threshold))
        qty_entry = self._entry_field(top, "Overstock Quantity Threshold", str(config.quantity_threshold))

        def run_scan():
            try:
                days = int(days_entry.get())
                qty_threshold = int(qty_entry.get())
                self.slow_moving_service.save_configuration(days, qty_threshold)
                self.slow_moving_service.run_analysis(days, qty_threshold)
                messagebox.showinfo("Success", "Scan complete. Table updated.")
                self.refresh_data()
                top.destroy()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ttk.Button(top, text="Run Scan", style="Primary.TButton", command=run_scan).pack(pady=20)

    def _entry_field(self, parent, label, value):
        frame = ttk.Frame(parent, padding=10)
        frame.pack(fill="x")
        ttk.Label(frame, text=label).pack(anchor="w")
        entry = ttk.Entry(frame)
        entry.insert(0, value)
        entry.pack(fill="x")
        return entry
