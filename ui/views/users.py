import tkinter as tk
from tkinter import messagebox, ttk

from ui.styles import *


class UsersView(ttk.Frame):
    def __init__(self, parent, user_service):
        super().__init__(parent, style="TFrame")
        self.user_service = user_service
        self.setup_ui()
        self.refresh_data()

    def setup_ui(self):
        container = ttk.Frame(self, padding=(20, 0, 20, 20))
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container)
        header.pack(fill="x", pady=(20, 20))
        ttk.Label(header, text="User Management", style="H1.TLabel").pack(side="left")

        actions = ttk.Frame(header)
        actions.pack(side="right")
        ttk.Button(actions, text="Add User", style="Primary.TButton", command=self.add_user_dialog).pack(side="left", padx=5)
        ttk.Button(actions, text="Edit", style="Outline.TButton", command=self.edit_user_dialog).pack(side="left", padx=5)
        ttk.Button(actions, text="Delete", style="Outline.TButton", command=self.delete_user_action).pack(side="left", padx=5)

        self.tree = ttk.Treeview(container, columns=("ID", "Username", "Role", "Last Login", "Created At"), show="headings")
        for column in ("ID", "Username", "Role", "Last Login", "Created At"):
            self.tree.heading(column, text=column, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=(10, 0))

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            for user in self.user_service.list_users():
                last_login = user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
                created_at = user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "N/A"
                self.tree.insert(
                    "",
                    "end",
                    values=(user.user_id, user.username, user.role, last_login, created_at),
                )
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def add_user_dialog(self):
        self.show_dialog("Add User")

    def edit_user_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a user.")
            return
        user_id = self.tree.item(selected[0])["values"][0]
        user = self.user_service.get_user(user_id)
        if user:
            self.show_dialog("Edit User", user)

    def show_dialog(self, title, user=None):
        top = tk.Toplevel(self)
        top.title(title)
        top.geometry("400x400")
        top.configure(bg=BACKGROUND)
        ttk.Label(top, text=title, style="H2.TLabel").pack(pady=20)

        entries = {}
        for field in ["Username", "Password", "Role"]:
            frame = ttk.Frame(top)
            frame.pack(fill="x", pady=5)
            ttk.Label(frame, text=field).pack(anchor="w")

            if field == "Role":
                entry = ttk.Combobox(frame, values=["Admin", "Staff", "Manager"])
                if user:
                    entry.set(user.role)
            else:
                entry = ttk.Entry(frame, show="*" if field == "Password" else "")
                if user and field == "Username":
                    entry.insert(0, user.username)
            entry.pack(fill="x")
            entries[field] = entry

        def save():
            try:
                if user:
                    self.user_service.update_user(
                        user.user_id,
                        entries["Username"].get(),
                        entries["Password"].get(),
                        entries["Role"].get(),
                    )
                else:
                    self.user_service.create_user(
                        entries["Username"].get(),
                        entries["Password"].get(),
                        entries["Role"].get(),
                    )
                top.destroy()
                self.refresh_data()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))

        ttk.Button(top, text="Save", command=save).pack(pady=20)

    def delete_user_action(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select user", "Please select a user.")
            return
        if messagebox.askyesno("Confirm", "Delete user?"):
            try:
                user_id = self.tree.item(selected[0])["values"][0]
                self.user_service.delete_user(user_id)
                self.refresh_data()
            except Exception as exc:
                messagebox.showerror("Error", str(exc))
