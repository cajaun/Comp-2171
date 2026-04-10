import tkinter as tk
from tkinter import messagebox, ttk

from ui.styles import *


class SettingsView(ttk.Frame):
    def __init__(self, parent, settings_service):
        super().__init__(parent, style="TFrame")
        self.settings_service = settings_service
        self.current_tab = "System"
        self.setup_ui()

    def setup_ui(self):
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 20))

        ttk.Label(header, text="Settings", style="H1.TLabel").pack(anchor="w")
        ttk.Label(header, text="Manage global system parameters.", foreground=MUTED_FOREGROUND).pack(anchor="w")

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        sidebar = ttk.Frame(main_frame, width=200)
        sidebar.pack(side="left", fill="y", padx=(0, 20))

        self.nav_buttons = {}
        for item in ["System", "Logs"]:
            style_name = "Primary.TButton" if item == self.current_tab else "Ghost.TButton"
            button = ttk.Button(sidebar, text=item, style=style_name, command=lambda current=item: self.navigate(current))
            button.pack(fill="x", pady=2)
            self.nav_buttons[item] = button

        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True)
        self.render_system()

    def navigate(self, tab):
        self.nav_buttons[self.current_tab].configure(style="Ghost.TButton")
        self.current_tab = tab
        self.nav_buttons[self.current_tab].configure(style="Primary.TButton")

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if tab == "System":
            self.render_system()
        else:
            self.render_logs()

    def render_system(self):
        ttk.Label(self.content_frame, text="System Configuration", style="H2.TLabel").pack(anchor="w", pady=(0, 20))
        self.entries = {}

        for key, label, value in self.settings_service.get_settings():
            frame = ttk.Frame(self.content_frame)
            frame.pack(fill="x", pady=10)
            ttk.Label(frame, text=label, font=(FONT_FAMILY, FONT_SIZE_BASE, "bold")).pack(anchor="w")
            entry = ttk.Entry(frame)
            entry.insert(0, value)
            entry.pack(fill="x", pady=(5, 0))
            self.entries[key] = entry

        ttk.Button(
            self.content_frame,
            text="Save Changes",
            style="Primary.TButton",
            command=self.save_settings,
        ).pack(anchor="w", pady=20)

    def save_settings(self):
        try:
            self.settings_service.save_settings({key: entry.get() for key, entry in self.entries.items()})
            messagebox.showinfo("Success", "Settings updated successfully.")
        except Exception as exc:
            messagebox.showerror("Error", f"Error saving settings: {exc}")

    def render_logs(self):
        ttk.Label(self.content_frame, text="Configuration Logs", style="H2.TLabel").pack(anchor="w", pady=(0, 20))

        tree = ttk.Treeview(self.content_frame, columns=("Parameter", "Value", "Last Updated"), show="headings")
        tree.heading("Parameter", text="Parameter")
        tree.heading("Value", text="Value")
        tree.heading("Last Updated", text="Last Updated")
        tree.column("Parameter", width=200)
        tree.column("Value", width=200)
        tree.column("Last Updated", width=200)
        tree.pack(fill="both", expand=True)

        try:
            for config in self.settings_service.get_logs():
                updated_at = config.updated_at.strftime("%Y-%m-%d %H:%M") if config.updated_at else "N/A"
                tree.insert(
                    "",
                    "end",
                    values=(config.parameter_name, config.parameter_value, updated_at),
                )
        except Exception as exc:
            messagebox.showerror("Error", f"Error loading logs: {exc}")
