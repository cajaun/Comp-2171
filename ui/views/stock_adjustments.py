import tkinter as tk
from tkinter import messagebox, ttk

from ui.components.rounded_shapes import RoundedFrame
from ui.styles import *


class StockAdjustmentsView(ttk.Frame):
    def __init__(self, parent, stock_adjustment_service, current_user):
        super().__init__(parent, style="TFrame")
        self.stock_adjustment_service = stock_adjustment_service
        self.current_user = current_user
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        container = ttk.Frame(self, padding=(20, 0, 20, 20))
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(20, 20))
        ttk.Label(header, text="Stock Adjustments", style="H1.TLabel").pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")
        ttk.Button(actions, text="Record Adjustment", style="Primary.TButton", command=self.add_adjustment_dialog).pack(side="left", padx=5)

        stats_frame = ttk.Frame(container)
        stats_frame.pack(fill="x", pady=(0, 20))
        for index in range(4):
            stats_frame.grid_columnconfigure(index, weight=1)

        self.create_stat_card(stats_frame, "Total Adjustments This Week", "0", "Last 7 days", 0)
        self.create_stat_card(stats_frame, "Stock In vs Stock Out", "-", "Increase vs Decrease", 1)
        self.create_stat_card(stats_frame, "Most Adjusted Product", "-", "Highest activity", 2)
        self.create_stat_card(stats_frame, "Adjustments Today", "0", "Today's changes", 3)

        self.tree = ttk.Treeview(container, columns=("ID", "Item", "Type", "Qty", "Reason", "User", "Date"), show="headings")
        for column in ("ID", "Item", "Type", "Qty", "Reason", "User", "Date"):
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

        if title == "Total Adjustments This Week":
            self.lbl_week = label_value
        elif title == "Stock In vs Stock Out":
            self.lbl_in_out = label_value
        elif title == "Most Adjusted Product":
            self.lbl_most_adjusted = label_value
        elif title == "Adjustments Today":
            self.lbl_today = label_value

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            adjustments = self.stock_adjustment_service.list_adjustments()
            stats = self.stock_adjustment_service.get_adjustment_stats()
            self.lbl_week.config(text=str(stats.week))
            self.lbl_today.config(text=str(stats.today))
            self.lbl_in_out.config(text=f"{stats.increases} / {stats.decreases}")
            self.lbl_most_adjusted.config(text=stats.most_adjusted)

            for adjustment in adjustments:
                date = adjustment.created_at.strftime("%Y-%m-%d %H:%M") if adjustment.created_at else "N/A"
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        adjustment.adjust_id,
                        adjustment.item_name,
                        adjustment.adjust_type,
                        adjustment.quantity,
                        adjustment.reason,
                        adjustment.user_name,
                        date,
                    ),
                )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def add_adjustment_dialog(self):
        self.show_dialog("Record Adjustment")

    def show_dialog(self, title):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("400x450")
        top.configure(bg=BACKGROUND)
        ttk.Label(top, text=title, style="H2.TLabel").pack(pady=20)

        items = self.stock_adjustment_service.list_items()
        item_map = {f"{item.name} (ID: {item.item_id})": item.item_id for item in items}

        item_var = tk.StringVar()
        type_var = tk.StringVar(value="Increase")

        for label, widget in [
            ("Item", ttk.Combobox(top, textvariable=item_var, values=list(item_map.keys()))),
            ("Type", ttk.Combobox(top, textvariable=type_var, values=["Increase", "Decrease"])),
        ]:
            frame = ttk.Frame(top, padding=10)
            frame.pack(fill="x")
            ttk.Label(frame, text=label).pack(anchor="w")
            widget.pack(fill="x")

        qty_frame = ttk.Frame(top, padding=10)
        qty_frame.pack(fill="x")
        ttk.Label(qty_frame, text="Quantity").pack(anchor="w")
        qty_entry = ttk.Entry(qty_frame)
        qty_entry.pack(fill="x")

        reason_frame = ttk.Frame(top, padding=10)
        reason_frame.pack(fill="x")
        ttk.Label(reason_frame, text="Reason").pack(anchor="w")
        reason_entry = ttk.Entry(reason_frame)
        reason_entry.pack(fill="x")

        def save():
            try:
                item_id = item_map.get(item_var.get())
                if not item_id:
                    raise ValueError("Select an item")
                self.stock_adjustment_service.record_adjustment(
                    actor_user_id=self.current_user.user_id,
                    item_id=item_id,
                    adjust_type=type_var.get(),
                    quantity=int(qty_entry.get()),
                    reason=reason_entry.get(),
                )
                messagebox.showinfo("Success", "Recorded successfully")
                self.refresh_data()
                top.destroy()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ttk.Button(top, text="Save", command=save).pack(pady=20)
