import tkinter as tk
from tkinter import ttk
from ui.styles import *

class SidebarItem(tk.Canvas):
    def __init__(self, parent, text, command, is_active=False):
        super().__init__(parent, height=40, bg="#F4F4F6", highlightthickness=0)
        self.config(width=250)
        self.command = command
        self.text = text
        self.is_active = is_active
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
        self.draw()

    def draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = 40

        if self.is_active:
            self.create_rounded_rect(5, 2, w-5, h-2, 8, fill="#E4E4E8", outline="")
            fg = "#000000"
            weight = "bold"
        else:
            fg = "#000000"
            weight = "normal"

        self.create_text(
            20, h/2,
            text=self.text,
            fill=fg,
            anchor="w",
            font=(FONT_FAMILY, FONT_SIZE_BASE, weight)
        )

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1,
            x1+r, y1,
            x2-r, y1,
            x2-r, y1,
            x2, y1,
            x2, y1+r,
            x2, y1+r,
            x2, y2-r,
            x2, y2-r,
            x2, y2,
            x2-r, y2,
            x2-r, y2,
            x1+r, y2,
            x1+r, y2,
            x1, y2,
            x1, y2-r,
            x1, y2-r,
            x1, y1+r,
            x1, y1+r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, e):
        if not self.is_active:
            self.create_rounded_rect(5, 2, self.winfo_width()-5, 38, 8, fill=MUTED, outline="", tags="hover")
            self.tag_lower("hover")

    def on_leave(self, e):
        self.delete("hover")

    def on_click(self, e):
        self.command()
        
    def set_active(self, active):
        self.is_active = active
        self.draw()


class Sidebar(tk.Frame):
    def __init__(self, parent, on_navigate, user, on_logout):
        super().__init__(parent, bg="#F4F4F6")
        self.on_navigate = on_navigate
        self.user = user
        self.on_logout = on_logout
        self.configure(width=200)
        self.items = {}
        self.current_key = "dashboard"

        
        style = ttk.Style()
        style.configure("Sidebar.TFrame", background="#F4F4F6")
        style.configure("Sidebar.TLabel", background="#F4F4F6", foreground=FOREGROUND)

      
        self.logo_frame = ttk.Frame(self, style="Sidebar.TFrame", padding=20)
        self.logo_frame.pack(fill="x")

        self.logo_label = ttk.Label(
            self.logo_frame,
            text="Braeton Gate Wholesale",
            style="Sidebar.TLabel",
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold")
        )
        self.logo_label.pack(anchor="w")

 
        self.menu_frame = ttk.Frame(self, style="Sidebar.TFrame", padding=(8, 10))
        self.menu_frame.pack(fill="both", expand=False)

        self.create_section("General", [
            ("Dashboard", "dashboard"),
        ])

        self.create_section("Inventory", [
            ("View Inventory", "inventory"),
            ("Categories", "categories"),
        ])

        self.create_section("Stock Operations", [
            ("Stock Adjustments", "stock_adjustments"),
            ("Damaged / Expired", "damaged_expired"),
        ])

        # Only Admin sees Reports and Slow-Moving
        if self.user and self.user.role == "Admin":
            self.create_section("Reporting", [
                ("Reports", "reports"),
                ("Slow-Moving / Overstock", "slow_moving"),
            ])

            self.create_section("Users", [
                ("User Management", "users"),
            ])

            self.create_section("Settings", [
                ("System Settings", "settings"),
            ])


        self.user_frame = ttk.Frame(self, style="Sidebar.TFrame", padding=8)
        self.user_frame.pack(fill="x", side="bottom")


        logout_btn = SidebarItem(
            self.user_frame,
            "Logout",
            self.on_logout,
            is_active=False
        )
        logout_btn.pack(fill="x", pady=(0, 10))


        info_container = ttk.Frame(self.user_frame, style="Sidebar.TFrame")
        info_container.pack(fill="x", padx=5)

        self.avatar = tk.Canvas(info_container, width=32, height=32, bg=MUTED, highlightthickness=0)
        self.avatar.create_oval(0, 0, 32, 32, fill=PRIMARY)
        self.avatar.pack(side="left", padx=(0, 10))

        self.user_info = ttk.Frame(info_container, style="Sidebar.TFrame")
        self.user_info.pack(side="left")

        username = self.user.username if self.user else "Guest"
        role = self.user.role if self.user else "Unknown"

        ttk.Label(
            self.user_info,
            text=username,
            style="Sidebar.TLabel",
            font=(FONT_FAMILY, FONT_SIZE_BASE, "bold")
        ).pack(anchor="w")

        ttk.Label(
            self.user_info,
            text=role,
            style="Sidebar.TLabel",
            font=(FONT_FAMILY, 10),
            foreground=MUTED_FOREGROUND
        ).pack(anchor="w")

    def create_section(self, title, items):
        ttk.Label(
            self.menu_frame,
            text=title,
            style="Sidebar.TLabel",
            foreground="#656568",
            font=(FONT_FAMILY, 11)
        ).pack(anchor="w", pady=(15, 8), padx=10)

        for label, key in items:
            item = SidebarItem(
                self.menu_frame,
                label,
                lambda k=key: self.handle_click(k),
                is_active=(key == self.current_key)
            )
            item.pack(fill="x", pady=2)
            item.bind("<Configure>", lambda e, i=item: i.draw())
            self.items[key] = item

    def handle_click(self, key):
        if self.current_key in self.items:
            self.items[self.current_key].set_active(False)

        self.current_key = key

        if key in self.items:
            self.items[key].set_active(True)

        self.on_navigate(key)
