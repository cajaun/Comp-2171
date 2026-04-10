import tkinter as tk
from tkinter import messagebox, ttk

from ui.components.rounded_shapes import RoundedFrame
from ui.styles import *


class DamagedExpiredView(ttk.Frame):
    def __init__(self, parent, condition_service, current_user):
        super().__init__(parent, style="TFrame")
        self.condition_service = condition_service
        self.current_user = current_user
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        container = ttk.Frame(self, padding=(20, 0, 20, 20))
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(20, 20))
        ttk.Label(header, text="Damaged / Expired Items", style="H1.TLabel").pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")
        ttk.Button(actions, text="Record Condition", style="Primary.TButton", command=lambda: self.show_dialog("Record Condition")).pack(side="left", padx=5)

        stats_frame = ttk.Frame(container)
        stats_frame.pack(fill="x", pady=(0, 20))
        for index in range(4):
            stats_frame.grid_columnconfigure(index, weight=1)

        self.create_stat_card(stats_frame, "Total Loss Value", "$0.00", "All-time losses", 0)
        self.create_stat_card(stats_frame, "Total Loss Count", "0", "Total incidents", 1)
        self.create_stat_card(stats_frame, "Top Damage Reason", "-", "Most common cause", 2)
        self.create_stat_card(stats_frame, "Most Frequently Damaged Item", "-", "Highest incidents", 3)

        self.tree = ttk.Treeview(container, columns=("ID", "Item", "Type", "Qty", "Reason", "Cost", "Date"), show="headings")
        for column in ("ID", "Item", "Type", "Qty", "Reason", "Cost", "Date"):
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

        if title == "Total Loss Value":
            self.lbl_loss_value = label_value
        elif title == "Total Loss Count":
            self.lbl_loss_count = label_value
        elif title == "Top Damage Reason":
            self.lbl_top_reason = label_value
        elif title == "Most Frequently Damaged Item":
            self.lbl_most_damaged = label_value

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conditions = self.condition_service.list_conditions()
            stats = self.condition_service.get_condition_stats()
            self.lbl_loss_value.config(text=f"${stats.loss_value:.2f}")
            self.lbl_loss_count.config(text=str(stats.loss_count))
            self.lbl_top_reason.config(text=stats.top_reason)
            self.lbl_most_damaged.config(text=stats.most_damaged)

            for condition in conditions:
                date = condition.recorded_at.strftime("%Y-%m-%d %H:%M") if condition.recorded_at else "N/A"
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        condition.condition_id,
                        condition.item_name,
                        condition.condition_type,
                        condition.quantity,
                        condition.reason,
                        f"${condition.cost_impact:.2f}",
                        date,
                    ),
                )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def show_dialog(self, title):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("400x500")
        top.configure(bg=BACKGROUND)
        ttk.Label(top, text=title, style="H2.TLabel").pack(pady=20)

        items = self.condition_service.list_items()
        item_map = {f"{item.name} (ID: {item.item_id})": item.item_id for item in items}
        item_var = tk.StringVar()
        type_var = tk.StringVar(value="Damaged")

        for label, widget in [
            ("Item", ttk.Combobox(top, textvariable=item_var, values=list(item_map.keys()))),
            ("Condition", ttk.Combobox(top, textvariable=type_var, values=["Damaged", "Expired", "Lost"])),
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
        ttk.Label(reason_frame, text="Reason / Cause").pack(anchor="w")
        reason_entry = ttk.Entry(reason_frame)
        reason_entry.pack(fill="x")

        def save():
            try:
                item_id = item_map.get(item_var.get())
                if not item_id:
                    raise ValueError("Select an item")
                self.condition_service.record_condition(
                    actor_user_id=self.current_user.user_id,
                    item_id=item_id,
                    condition_type=type_var.get(),
                    quantity=int(qty_entry.get()),
                    reason=reason_entry.get(),
                )
                messagebox.showinfo("Success", "Recorded successfully")
                self.refresh_data()
                top.destroy()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ttk.Button(top, text="Save", command=save).pack(pady=20)
