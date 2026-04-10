import tkinter as tk
from tkinter import messagebox

from ui.components.rounded_shapes import RoundedButton, RoundedEntry
from ui.styles import *


class LoginView(tk.Frame):
    def __init__(self, parent, auth_service, on_login_success):
        super().__init__(parent, bg=APP_BACKGROUND)
        self.auth_service = auth_service
        self.on_login_success = on_login_success
        self.setup_ui()

    def setup_ui(self):
        container = tk.Frame(self, bg=CARD, padx=40, pady=40)
        container.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            container,
            text="Login",
            font=(FONT_FAMILY, FONT_SIZE_3XL, "bold"),
            bg=CARD,
            fg=FOREGROUND,
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            container,
            text="Enter your username below to login to your account",
            font=(FONT_FAMILY, FONT_SIZE_SM),
            bg=CARD,
            fg=MUTED_FOREGROUND,
        ).pack(anchor="w", pady=(0, 20))

        tk.Label(
            container,
            text="Username",
            font=(FONT_FAMILY, FONT_SIZE_BASE, "bold"),
            bg=CARD,
            fg=FOREGROUND,
        ).pack(anchor="w", pady=(0, 5))
        self.username_entry = RoundedEntry(container, width=300, height=40)
        self.username_entry.pack(pady=(0, 15))

        tk.Label(
            container,
            text="Password",
            font=(FONT_FAMILY, FONT_SIZE_BASE, "bold"),
            bg=CARD,
            fg=FOREGROUND,
        ).pack(anchor="w", pady=(0, 5))
        self.password_entry = RoundedEntry(container, width=300, height=40, show="*")
        self.password_entry.pack(pady=(0, 20))

        RoundedButton(
            container,
            text="Login",
            width=300,
            height=40,
            radius=8,
            bg_color=CARD,
            fg_color=PRIMARY,
            text_color="#FFFFFF",
            hover_color="#18181B",
            command=self.login,
        ).pack()

        tk.Label(
            container,
            text="Don't have an account? Ask Admin.",
            font=(FONT_FAMILY, FONT_SIZE_SM),
            bg=CARD,
            fg=MUTED_FOREGROUND,
        ).pack(pady=(20, 0))

    def login(self):
        try:
            user = self.auth_service.authenticate(
                self.username_entry.entry.get(),
                self.password_entry.entry.get(),
            )
            if user:
                self.on_login_success(user)
                return
            messagebox.showerror("Error", "Invalid username or password.")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
