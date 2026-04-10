import tkinter as tk
from tkinter import ttk

# Colors
BACKGROUND = "#FFFFFF"
APP_BACKGROUND = "#F4F4F6"
FOREGROUND = "#020817"
MUTED = "#F1F5F9"
MUTED_FOREGROUND = "#64748B"
CARD = "#FFFFFF"
CARD_FOREGROUND = "#020817"
BORDER = "#E4E4E8"
INPUT = "#E2E8F0"
PRIMARY = "#0F172A"
PRIMARY_FOREGROUND = "#F8FAFC"
SECONDARY = "#F1F5F9"
SECONDARY_FOREGROUND = "#0F172A"
ACCENT = "#FCC737"
ACCENT_FOREGROUND = "#0F172A"
DESTRUCTIVE = "#EF4444"
DESTRUCTIVE_FOREGROUND = "#F8FAFC"
SUCCESS = "#22C55E"
SUCCESS_FOREGROUND = "#F8FAFC"
RING = "#94A3B8"

CHART_COLORS = [
    "#09090B",  # black
    "#52525B",  # slate gray
    "#27272B",  # charcoal
    "#9F9FA7",  # muted gray
    "#D4D4DA",  # light gray
]


# Fonts 
FONT_FAMILY = "Segoe UI"
FONT_SIZE_SM = 11
FONT_SIZE_BASE = 13
FONT_SIZE_LG = 15
FONT_SIZE_XL = 18
FONT_SIZE_2XL = 22
FONT_SIZE_3XL = 28

def setup_styles(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    # General Frame
    style.configure("TFrame", background=BACKGROUND)
    style.configure("Card.TFrame", background=CARD, relief="flat") # 
    
    # Labels
    style.configure("TLabel", background=BACKGROUND, foreground=FOREGROUND, font=(FONT_FAMILY, FONT_SIZE_BASE))
    style.configure("CardTitle.TLabel", background=CARD, foreground=MUTED_FOREGROUND, font=(FONT_FAMILY, FONT_SIZE_SM, "bold"))
    style.configure("CardValue.TLabel", background=CARD, foreground=FOREGROUND, font=(FONT_FAMILY, FONT_SIZE_3XL, "bold"))
    style.configure("CardSub.TLabel", background=CARD, foreground=MUTED_FOREGROUND, font=(FONT_FAMILY, FONT_SIZE_SM))
    
    style.configure("H1.TLabel", font=(FONT_FAMILY, FONT_SIZE_3XL, "bold"), foreground=FOREGROUND)
    style.configure("H2.TLabel", font=(FONT_FAMILY, FONT_SIZE_2XL, "bold"), foreground=FOREGROUND)
    style.configure("Sidebar.TLabel", background=BACKGROUND, foreground=FOREGROUND, font=(FONT_FAMILY, FONT_SIZE_BASE))
    
    # Buttons
    style.configure("Primary.TButton", 
                    background=PRIMARY, 
                    foreground=PRIMARY_FOREGROUND, 
                    borderwidth=0, 
                    focuscolor=RING,
                    font=(FONT_FAMILY, FONT_SIZE_BASE, "bold"),
                    padding=(15, 8))
    style.map("Primary.TButton", background=[("active", "#1E293B")])

    style.configure("Outline.TButton", 
                    background=BACKGROUND, 
                    foreground=FOREGROUND, 
                    borderwidth=1, 
                    bordercolor=BORDER,
                    focuscolor=RING,
                    font=(FONT_FAMILY, FONT_SIZE_BASE),
                    padding=(8, 4))
    style.map("Outline.TButton", background=[("active", MUTED)])

    style.configure("Ghost.TButton", 
                    background=BACKGROUND, 
                    foreground=FOREGROUND, 
                    borderwidth=0, 
                    focuscolor=RING,
                    font=(FONT_FAMILY, FONT_SIZE_BASE),
                    padding=(10, 8),
                    anchor="w")
    style.map("Ghost.TButton", background=[("active", MUTED)])

    # Treeview
    style.configure("Treeview", 
                    background=BACKGROUND, 
                    foreground=FOREGROUND, 
                    fieldbackground=BACKGROUND,
                    borderwidth=0,
                    rowheight=45,
                    font=(FONT_FAMILY, FONT_SIZE_BASE))
    style.configure("Treeview.Heading", 
                    background=BACKGROUND, 
                    foreground=MUTED_FOREGROUND, 
                    borderwidth=0,
                    font=(FONT_FAMILY, FONT_SIZE_BASE, "bold"))
    style.map("Treeview", background=[("selected", MUTED)], foreground=[("selected", FOREGROUND)])
    
    # Separator
    style.configure("TSeparator", background=BORDER)
    
    # Scrollbar 
    style.configure("Vertical.TScrollbar", 
                    background=BACKGROUND, 
                    troughcolor=BACKGROUND, 
                    bordercolor=BACKGROUND, 
                    arrowcolor=MUTED_FOREGROUND,
                    relief="flat",
                    width=10)
    style.map("Vertical.TScrollbar", background=[("active", MUTED_FOREGROUND)])

    return style
