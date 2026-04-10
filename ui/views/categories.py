import tkinter as tk
from tkinter import messagebox, ttk

from ui.components.rounded_shapes import RoundedFrame
from ui.styles import *


class CategoriesView(ttk.Frame):
    def __init__(self, parent, category_service):
        super().__init__(parent, style="TFrame")
        self.category_service = category_service
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        container = ttk.Frame(self, padding=(20, 0, 20, 20))
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(20, 20))
        ttk.Label(header, text="Categories", style="H1.TLabel").pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")
        ttk.Button(actions, text="Add Category", style="Primary.TButton", command=self.add_category_dialog).pack(side="left", padx=5)
        ttk.Button(actions, text="Edit", style="Outline.TButton", command=self.edit_category_dialog).pack(side="left", padx=5)
        ttk.Button(actions, text="Delete", style="Outline.TButton", command=self.delete_category_action).pack(side="left", padx=5)

        stats_frame = ttk.Frame(container)
        stats_frame.pack(fill="x", pady=(0, 20))
        for index in range(4):
            stats_frame.grid_columnconfigure(index, weight=1)

        self.create_stat_card(stats_frame, "Total Categories", "0", "All product groups", 0)
        self.create_stat_card(stats_frame, "Category With Most Items", "-", "Largest category", 1)
        self.create_stat_card(stats_frame, "Most Valuable Category", "-", "Highest total value", 2)
        self.create_stat_card(stats_frame, "Low-Stock Items", "0", "Needs restocking", 3)

        self.tree = ttk.Treeview(container, columns=("ID", "Name", "Description", "Items"), show="headings")
        for column in ("ID", "Name", "Description", "Items"):
            self.tree.heading(column, text=column, anchor="center")
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Name", width=150, anchor="center")
        self.tree.column("Description", width=300, anchor="center")
        self.tree.column("Items", width=80, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=(10, 0))

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

        if title == "Total Categories":
            self.lbl_total = label_value
        elif title == "Category With Most Items":
            self.lbl_most_items = label_value
        elif title == "Most Valuable Category":
            self.lbl_most_valuable = label_value
        elif title == "Low-Stock Items":
            self.lbl_low_stock = label_value

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            categories = self.category_service.list_categories()
            stats = self.category_service.get_category_stats()
            self.lbl_total.config(text=str(stats.total))
            self.lbl_most_items.config(text=stats.most_items)
            self.lbl_most_valuable.config(text=stats.most_valuable)
            self.lbl_low_stock.config(text=str(stats.low_stock))

            for category in categories:
                self.tree.insert(
                    "",
                    "end",
                    values=(category.category_id, category.name, category.description, category.item_count),
                )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def add_category_dialog(self):
        self.show_dialog("Add Category")

    def edit_category_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a category to edit.")
            return

        category_id = self.tree.item(selected[0])["values"][0]
        category = self.category_service.get_category(category_id)
        if category:
            self.show_dialog("Edit Category", category)

    def show_dialog(self, title, category=None):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("400x300")
        top.configure(bg=BACKGROUND)
        ttk.Label(top, text=title, style="H2.TLabel").pack(pady=20)

        entries = {}
        for field, value in {
            "Name": category.name if category else "",
            "Description": category.description if category else "",
        }.items():
            frame = ttk.Frame(top, padding=10)
            frame.pack(fill="x")
            ttk.Label(frame, text=field).pack(anchor="w")
            entry = ttk.Entry(frame)
            entry.insert(0, value)
            entry.pack(fill="x")
            entries[field] = entry

        def save():
            try:
                if category:
                    self.category_service.update_category(
                        category.category_id,
                        entries["Name"].get(),
                        entries["Description"].get(),
                    )
                else:
                    self.category_service.create_category(
                        entries["Name"].get(),
                        entries["Description"].get(),
                    )
                top.destroy()
                self.refresh_data()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ttk.Button(top, text="Save", style="Primary.TButton", command=save).pack(pady=20)

    def delete_category_action(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a category to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this category?"):
            try:
                category_id = self.tree.item(selected[0])["values"][0]
                self.category_service.delete_category(category_id)
                self.refresh_data()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))
