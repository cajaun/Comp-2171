import tkinter as tk
from tkinter import ttk

from ui.components.sidebar import Sidebar
from ui.styles import *
from ui.views.categories import CategoriesView
from ui.views.dashboard import DashboardView
from ui.views.damaged_expired import DamagedExpiredView
from ui.views.inventory import InventoryView
from ui.views.login import LoginView
from ui.views.reports import ReportsView
from ui.views.settings import SettingsView
from ui.views.slow_moving import SlowMovingView
from ui.views.stock_adjustments import StockAdjustmentsView
from ui.views.users import UsersView


class App(tk.Tk):
    def __init__(self, services):
        super().__init__()
        self.services = services
        self.title("Braeton Gate Wholesale")

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        self.geometry(f"{int(screen_w * 0.90)}x{int(screen_h * 0.90)}")
        self.minsize(1100, 700)

        self.configure(bg=APP_BACKGROUND)
        setup_styles(self)

        self.current_user = None
        self.views = {}
        self.current_view = None
        self.show_login()

    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.login_view = LoginView(self, self.services.auth, self.on_login_success)
        self.login_view.pack(fill="both", expand=True)

    def on_login_success(self, user):
        self.current_user = user
        self.login_view.destroy()
        self.setup_main_interface()

    def logout(self):
        self.current_user = None
        self.show_login()

    def setup_main_interface(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)

        self.sidebar = Sidebar(self, self.navigate, self.current_user, self.logout)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        sep = tk.Frame(self, bg=MUTED, width=1)
        sep.grid(row=0, column=1, sticky="ns")

        self.content_area = ttk.Frame(self, style="TFrame")
        self.content_area.grid(row=0, column=2, sticky="nsew", padx=20, pady=20)

        self.corner_mask_tl = tk.Canvas(self.content_area, width=20, height=20, bg=APP_BACKGROUND, highlightthickness=0)
        self.corner_mask_tl.place(x=0, y=0)
        self.corner_mask_tl.create_arc(0, 0, 40, 40, start=90, extent=90, fill=BACKGROUND, outline="")

        self.corner_mask_tr = tk.Canvas(self.content_area, width=20, height=20, bg=APP_BACKGROUND, highlightthickness=0)
        self.corner_mask_tr.place(relx=1.0, x=-20, y=0)
        self.corner_mask_tr.create_arc(-20, 0, 20, 40, start=0, extent=90, fill=BACKGROUND, outline="")

        self.corner_mask_bl = tk.Canvas(self.content_area, width=20, height=20, bg=APP_BACKGROUND, highlightthickness=0)
        self.corner_mask_bl.place(x=0, rely=1.0, y=-20)
        self.corner_mask_bl.create_arc(0, -20, 40, 20, start=180, extent=90, fill=BACKGROUND, outline="")

        self.corner_mask_br = tk.Canvas(self.content_area, width=20, height=20, bg=APP_BACKGROUND, highlightthickness=0)
        self.corner_mask_br.place(relx=1.0, x=-20, rely=1.0, y=-20)
        self.corner_mask_br.create_arc(-20, -20, 20, 20, start=270, extent=90, fill=BACKGROUND, outline="")

        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(1, weight=1)

        top_sep = tk.Frame(self.content_area, bg=MUTED, height=1)
        top_sep.grid(row=0, column=0, sticky="ew", pady=(60, 20))

        self.views = {}
        self.navigate("dashboard")

    def navigate(self, view_name):
        if view_name not in self.views:
            if view_name == "dashboard":
                view = DashboardView(self.content_area, self.services.dashboard)
            elif view_name == "users":
                view = UsersView(self.content_area, self.services.users)
            elif view_name == "settings":
                view = SettingsView(self.content_area, self.services.settings)
            elif view_name == "inventory":
                view = InventoryView(self.content_area, self.services.inventory)
            elif view_name == "categories":
                view = CategoriesView(self.content_area, self.services.categories)
            elif view_name == "stock_adjustments":
                view = StockAdjustmentsView(
                    self.content_area,
                    self.services.stock_adjustments,
                    self.current_user,
                )
            elif view_name == "damaged_expired":
                view = DamagedExpiredView(
                    self.content_area,
                    self.services.conditions,
                    self.current_user,
                )
            elif view_name == "reports":
                view = ReportsView(self.content_area, self.services.reports, self.current_user)
            elif view_name == "slow_moving":
                view = SlowMovingView(self.content_area, self.services.slow_moving)
            else:
                return

            self.views[view_name] = view
            self.views[view_name].grid(row=1, column=0, sticky="nsew")

        if hasattr(self.views[view_name], "refresh_data"):
            self.views[view_name].refresh_data()

        self.views[view_name].tkraise()
        self.current_view = self.views[view_name]
        self.raise_masks()

    def raise_masks(self):
        tk.Misc.tkraise(self.corner_mask_tl)
        tk.Misc.tkraise(self.corner_mask_tr)
        tk.Misc.tkraise(self.corner_mask_bl)
        tk.Misc.tkraise(self.corner_mask_br)
