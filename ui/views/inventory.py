import tkinter as tk
from tkinter import messagebox, ttk

from ui.components.rounded_shapes import RoundedButton, RoundedEntry, RoundedFrame
from ui.styles import *


class InventoryView(ttk.Frame):
    def __init__(self, parent, inventory_service):
        super().__init__(parent, style="TFrame")
        self.inventory_service = inventory_service
        self.active_filters = {}
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        container = ttk.Frame(self, padding=(20, 0, 20, 20))
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(20, 20))

        title_row = ttk.Frame(header)
        title_row.pack(fill="x")
        ttk.Label(title_row, text="Inventory Management", style="H1.TLabel").pack(side="left")

        actions = ttk.Frame(title_row)
        actions.pack(side="right")
        RoundedButton(actions, text="Add Product", command=self.add_item_dialog, width=130, height=35, radius=12, fg_color=PRIMARY, text_color=PRIMARY_FOREGROUND).pack(side="left", padx=5)
        RoundedButton(actions, text="Edit", command=self.edit_item_dialog, style_type="outline", width=110, height=35, radius=12).pack(side="left", padx=5)
        RoundedButton(actions, text="Delete", command=self.delete_item_action, style_type="outline", width=130, height=35, radius=12).pack(side="left", padx=5)

        stats_frame = ttk.Frame(container)
        stats_frame.pack(fill="x", pady=(0, 20))
        for index in range(4):
            stats_frame.grid_columnconfigure(index, weight=1)

        self.create_stat_card(stats_frame, "Total Products", "0", "Across all categories", 0)
        self.create_stat_card(stats_frame, "Low Stock", "0", "Needs restocking soon", 1)
        self.create_stat_card(stats_frame, "Out of Stock", "0", "Currently unavailable", 2)
        self.create_stat_card(stats_frame, "Categories", "0", "Organized product groups", 3)

        filter_frame = ttk.Frame(container)
        filter_frame.pack(fill="x", pady=(0, 15))
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self.refresh_data())

        RoundedEntry(
            filter_frame,
            textvariable=self.search_var,
            width=280,
            height=35,
            radius=12,
            fg_color="#FFFFFF",
            border_color=BORDER,
            text_color=FOREGROUND,
            placeholder="Search products...",
        ).pack(side="left", padx=(0, 8))

        RoundedButton(filter_frame, text="Category", command=self.filter_category_dialog, width=130, height=35, radius=12, fg_color=BACKGROUND, text_color=FOREGROUND, hover_color=MUTED, style_type="outline").pack(side="left", padx=5)
        RoundedButton(filter_frame, text="Stock", command=self.filter_stock_dialog, width=130, height=35, radius=12, fg_color=BACKGROUND, text_color=FOREGROUND, hover_color=MUTED, style_type="outline").pack(side="left", padx=5)
        RoundedButton(filter_frame, text="Clear Filters", command=self.clear_filters, width=100, height=35, radius=12, fg_color=BACKGROUND, text_color=DESTRUCTIVE, hover_color=MUTED, style_type="outline").pack(side="left", padx=5)

        self.tree = ttk.Treeview(container, columns=("ID", "Name", "Category", "Price", "Stock", "Unit"), show="headings", style="Custom.Treeview")
        for column in ("ID", "Name", "Category", "Price", "Stock", "Unit"):
            self.tree.heading(column, text=column)
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("Name", width=230, anchor="center")
        self.tree.column("Category", width=150, anchor="center")
        self.tree.column("Price", width=100, anchor="center")
        self.tree.column("Stock", width=100, anchor="center")
        self.tree.column("Unit", width=80, anchor="center")
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

        if title == "Total Products":
            self.lbl_total = label_value
        elif title == "Low Stock":
            self.lbl_low = label_value
        elif title == "Out of Stock":
            self.lbl_out = label_value
        elif title == "Categories":
            self.lbl_cats = label_value

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            items = self.inventory_service.list_items(
                search_text=self.search_var.get(),
                category_name=self.active_filters.get("category"),
                stock_filter=self.active_filters.get("stock"),
            )
            stats = self.inventory_service.get_inventory_stats()

            self.lbl_total.config(text=str(stats.total))
            self.lbl_low.config(text=str(stats.low))
            self.lbl_out.config(text=str(stats.out))
            self.lbl_cats.config(text=str(stats.categories))

            for item in items:
                self.tree.insert(
                    "",
                    "end",
                    values=(
                        item.item_id,
                        item.name,
                        item.category_name,
                        f"${item.price:.2f}",
                        item.current_stock,
                        item.unit,
                    ),
                )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def add_item_dialog(self):
        self.show_dialog("Add Product")

    def edit_item_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a product to edit.")
            return
        item_id = self.tree.item(selected[0])["values"][0]
        item = self.inventory_service.get_item(item_id)
        if item:
            self.show_dialog("Edit Product", item)

    def delete_item_action(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a product to delete.")
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this product?"):
            try:
                item_id = self.tree.item(selected[0])["values"][0]
                self.inventory_service.delete_item(item_id)
                self.refresh_data()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

    def show_dialog(self, title, item=None):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("420x420")
        top.configure(bg=BACKGROUND)
        ttk.Label(top, text=title, style="H2.TLabel").pack(pady=20)

        categories = self.inventory_service.list_categories()
        category_map = {category.name: category.category_id for category in categories}

        fields = {
            "Name": item.name if item else "",
            "Category": item.category_name if item and item.category_name != "-" else "",
            "Price": f"{item.price:.2f}" if item else "",
            "Stock": str(item.current_stock) if item else "",
            "Unit": item.unit if item and item.unit != "-" else "",
            "Reorder Level": str(item.reorder_level) if item else "10",
        }
        entries = {}

        for field, value in fields.items():
            frame = ttk.Frame(top, padding=10)
            frame.pack(fill="x")
            ttk.Label(frame, text=field).pack(anchor="w")
            if field == "Category":
                entry = ttk.Combobox(frame, values=list(category_map.keys()))
            else:
                entry = ttk.Entry(frame)
            entry.insert(0, value)
            entry.pack(fill="x")
            entries[field] = entry

        def save():
            try:
                category_name = entries["Category"].get().strip()
                category_id = category_map.get(category_name)
                if not category_id:
                    raise ValueError("Please select a category")
                payload = {
                    "name": entries["Name"].get(),
                    "category_id": category_id,
                    "price": float(entries["Price"].get()),
                    "stock": int(entries["Stock"].get()),
                    "unit": entries["Unit"].get(),
                    "reorder_level": int(entries["Reorder Level"].get()),
                }
                if item:
                    self.inventory_service.update_item(item.item_id, **payload)
                else:
                    self.inventory_service.create_item(**payload)
                top.destroy()
                self.refresh_data()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ttk.Button(top, text="Save", style="Primary.TButton", command=save).pack(pady=20)

    def filter_category_dialog(self):
        categories = self.inventory_service.list_categories()
        category_names = [category.name for category in categories]
        self._show_filter_dialog("Category Filter", category_names, "category")

    def filter_stock_dialog(self):
        self._show_filter_dialog("Stock Filter", ["In Stock", "Low Stock", "Out of Stock"], "stock")

    def _show_filter_dialog(self, title, options, key):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("300x180")
        top.configure(bg=BACKGROUND)
        ttk.Label(top, text=title, style="H2.TLabel").pack(pady=20)
        selected_value = tk.StringVar(value=self.active_filters.get(key, ""))
        ttk.Combobox(top, textvariable=selected_value, values=options).pack(fill="x", padx=20)

        def apply_filter():
            self.active_filters[key] = selected_value.get()
            top.destroy()
            self.refresh_data()

        ttk.Button(top, text="Apply", command=apply_filter).pack(pady=20)

    def clear_filters(self):
        self.active_filters = {}
        self.search_var.set("")
        self.refresh_data()
