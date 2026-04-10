import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from ui.components.rounded_shapes import RoundedButton, RoundedFrame
from ui.components.scrollable_frame import ScrollableFrame
from ui.styles import *


class DashboardView(ttk.Frame):
    def __init__(self, parent, dashboard_service):
        super().__init__(parent, style="TFrame")
        self.dashboard_service = dashboard_service
        self.snapshot = None

        self.scroll_container = ScrollableFrame(self, bg=BACKGROUND)
        self.scroll_container.pack(fill="both", expand=True)
        self.scrollable_frame = self.scroll_container.scrollable_frame

        self.refresh_data()

    def refresh_data(self):
        self.snapshot = self.dashboard_service.get_snapshot()
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.setup_ui()

    def setup_ui(self):
        header_frame = ttk.Frame(self.scrollable_frame, padding=(20, 20, 30, 10))
        header_frame.pack(fill="x")

        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side="left")
        ttk.Label(title_frame, text="Dashboard", style="H1.TLabel").pack(anchor="w")

        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side="right")

        RoundedButton(
            controls_frame,
            text="28 Oct 2025 - 24 Nov 2025",
            width=200,
            height=35,
            radius=12,
            fg_color=BACKGROUND,
            text_color=FOREGROUND,
            hover_color=MUTED,
            style_type="outline",
        ).pack(side="left", padx=5)

        content = ttk.Frame(self.scrollable_frame, padding=20)
        content.pack(fill="both", expand=True)

        cards_frame = ttk.Frame(content)
        cards_frame.pack(fill="x", pady=(0, 20))
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)
        cards_frame.grid_columnconfigure(3, weight=1)

        self.create_product_card(cards_frame, 0)
        self.create_category_card(cards_frame, 1)
        self.create_low_stock_card(cards_frame, 2)
        self.create_damaged_card(cards_frame, 3)

        bottom_row = ttk.Frame(content)
        bottom_row.pack(fill="both", expand=True)
        bottom_row.grid_columnconfigure(0, weight=1)
        bottom_row.grid_columnconfigure(1, weight=1)
        bottom_row.grid_columnconfigure(2, weight=1)

        self.create_stock_category_chart(bottom_row, 0)
        self.create_monthly_stock_adjustments_chart(bottom_row, 1)
        self.create_condition_summary_chart(bottom_row, 2)

    def create_card_frame(self, parent, row, col):
        card = RoundedFrame(parent, fg_color=CARD, border_width=1, border_color=BORDER, padding=20)
        card.grid(row=row, column=col, sticky="nsew", padx=10)
        return card.inner_frame

    def create_product_card(self, parent, col):
        card = self.create_card_frame(parent, 0, col)

        header = tk.Frame(card, bg=CARD)
        header.pack(fill="x", pady=(0, 15))
        tk.Label(
            header,
            text="Total Products",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
        ).pack(anchor="w")

        total_products = self.snapshot.total_products
        tk.Label(
            card,
            text=f"{total_products}",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_3XL, "bold"),
        ).pack(anchor="w")

        new_products = self.snapshot.new_products
        previous_count = total_products - new_products
        if previous_count > 0:
            growth = (new_products / previous_count) * 100
            trend_text = f"↗ {growth:.1f}%"
            trend_color = SUCCESS
        elif new_products > 0:
            trend_text = "↗ 100%"
            trend_color = SUCCESS
        else:
            trend_text = "- 0%"
            trend_color = MUTED_FOREGROUND

        trend_frame = tk.Frame(card, bg=CARD)
        trend_frame.pack(anchor="w", pady=(5, 20))
        tk.Label(
            trend_frame,
            text=trend_text,
            bg=CARD,
            fg=trend_color,
            font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
        ).pack(side="left")
        tk.Label(
            trend_frame,
            text=" in last 30 days",
            bg=CARD,
            fg=MUTED_FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_SM),
        ).pack(side="left")

    def create_category_card(self, parent, col):
        card = self.create_card_frame(parent, 0, col)

        tk.Label(
            card,
            text="Total Categories",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
        ).pack(anchor="w")

        tk.Label(
            card,
            text=f"{self.snapshot.total_categories}",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_3XL, "bold"),
        ).pack(anchor="w")

        tk.Label(
            card,
            text="Active Categories",
            bg=CARD,
            fg=MUTED_FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_SM),
        ).pack(anchor="w", pady=(35, 0))

    def create_low_stock_card(self, parent, col):
        card = self.create_card_frame(parent, 0, col)

        tk.Label(
            card,
            text="Low Stock Items",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
        ).pack(anchor="w")

        low_stock_count = self.snapshot.low_stock_count
        tk.Label(
            card,
            text=f"{low_stock_count}",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_3XL, "bold"),
        ).pack(anchor="w")

        status_color = DESTRUCTIVE if low_stock_count > 0 else SUCCESS
        status_text = "Action Needed" if low_stock_count > 0 else "Stock Healthy"
        tk.Label(
            card,
            text=status_text,
            bg=CARD,
            fg=status_color,
            font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
        ).pack(anchor="w", pady=(35, 0))

    def create_damaged_card(self, parent, col):
        card = self.create_card_frame(parent, 0, col)

        header = tk.Frame(card, bg=CARD)
        header.pack(fill="x", pady=(0, 15))
        tk.Label(
            header,
            text="Damaged / Expired",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
        ).pack(side="left")

        badge = tk.Label(
            header,
            text=f"{self.snapshot.damaged_recent} new",
            bg="#FEF2F2",
            fg=DESTRUCTIVE,
            font=(FONT_FAMILY, 10),
            padx=8,
            pady=2,
        )
        badge.pack(side="right")

        tk.Label(
            card,
            text=f"{self.snapshot.damaged_total}",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_3XL, "bold"),
        ).pack(anchor="w")

        fig = Figure(figsize=(3, 0.8), dpi=100)
        fig.patch.set_facecolor(CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD)
        data = [2, 1, 4, 3, 5, 2, 4]
        ax.bar(range(len(data)), data, color=CHART_COLORS[0])
        ax.axis("off")

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", pady=(10, 0))

    def create_stock_category_chart(self, parent, col):
        wrapper = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrapper.grid(row=0, column=col, sticky="nsew", padx=10, pady=10)
        frame = tk.Frame(wrapper, bg=CARD, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        header = tk.Frame(frame, bg=CARD)
        header.pack(fill="x", pady=(0, 20))
        tk.Label(
            header,
            text="Stock by Category",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
        ).pack(side="left")
        tk.Label(header, text="↗", bg=CARD, fg=MUTED_FOREGROUND).pack(side="right")

        data = [
            {
                "category": point.category,
                "count": point.count,
                "percentage": point.percentage,
            }
            for point in self.snapshot.stock_by_category
        ]
        if not data:
            data = [{"category": "No Data", "count": 0, "percentage": 0}]

        total_stock = self.snapshot.total_stock_units or sum(item["count"] for item in data)

        tk.Label(
            frame,
            text="Total Stock",
            bg=CARD,
            fg=MUTED_FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_SM),
        ).pack(anchor="w")
        tk.Label(
            frame,
            text=f"{total_stock:,} units",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_3XL, "bold"),
        ).pack(anchor="w", pady=(5, 5))

        trend = tk.Frame(frame, bg=CARD)
        trend.pack(anchor="w", pady=(0, 20))
        trend_color = SUCCESS if self.snapshot.stock_trend_percent >= 0 else DESTRUCTIVE
        trend_symbol = "↗" if self.snapshot.stock_trend_percent >= 0 else "↘"
        tk.Label(
            trend,
            text=f"{trend_symbol} {abs(self.snapshot.stock_trend_percent):.1f}%",
            bg=CARD,
            fg=trend_color,
            font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
        ).pack(side="left")
        tk.Label(
            trend,
            text=" since last month",
            bg=CARD,
            fg=MUTED_FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_SM),
        ).pack(side="left")

        progress_frame = tk.Frame(frame, bg=BORDER, height=8)
        progress_frame.pack(fill="x", pady=(0, 20))

        canvas = tk.Canvas(progress_frame, height=8, bg=BORDER, highlightthickness=0)
        canvas.pack(fill="both")

        colors = CHART_COLORS
        total_width = 300
        start = 0
        for index, source in enumerate(data):
            width = source["percentage"] * total_width
            canvas.create_rectangle(
                start,
                0,
                start + width,
                8,
                fill=colors[index % len(colors)],
                outline="",
            )
            start += width

        for index, source in enumerate(data):
            row = tk.Frame(frame, bg=CARD, pady=8)
            row.pack(fill="x")

            tk.Label(
                row,
                text="●",
                bg=CARD,
                fg=colors[index % len(colors)],
                font=(FONT_FAMILY, 10),
            ).pack(side="left", padx=(0, 10))

            tk.Label(
                row,
                text=source["category"],
                bg=CARD,
                fg=MUTED_FOREGROUND,
                font=(FONT_FAMILY, FONT_SIZE_SM),
            ).pack(side="left")

            tk.Label(
                row,
                text=f"{source['count']} units",
                bg=CARD,
                fg=FOREGROUND,
                font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
            ).pack(side="right")

    def create_monthly_stock_adjustments_chart(self, parent, col):
        wrapper = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrapper.grid(row=0, column=col, sticky="nsew", padx=10, pady=10)
        frame = tk.Frame(wrapper, bg=CARD, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        header = tk.Frame(frame, bg=CARD)
        header.pack(fill="x")

        title_group = tk.Frame(header, bg=CARD)
        title_group.pack(side="left")

        tk.Label(
            title_group,
            text="Monthly Stock Adjustments",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
        ).pack(anchor="w")
        tk.Label(
            title_group,
            text="Last 6 months",
            bg=CARD,
            fg=MUTED_FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_SM),
        ).pack(anchor="w")

        legend_row = tk.Frame(frame, bg=CARD)
        legend_row.pack(fill="x", pady=(10, 10))

        legends = [
            ("Stock In", CHART_COLORS[1]),
            ("Stock Out", CHART_COLORS[2]),
            ("Manual Adj.", CHART_COLORS[4]),
        ]

        for text, color in legends:
            item = tk.Frame(legend_row, bg=CARD)
            item.pack(side="left", padx=15)
            tk.Label(
                item,
                text="●",
                fg=color,
                bg=CARD,
                font=(FONT_FAMILY, 12, "bold"),
            ).pack(side="left")
            tk.Label(
                item,
                text=text,
                fg=MUTED_FOREGROUND,
                bg=CARD,
                font=(FONT_FAMILY, FONT_SIZE_SM),
            ).pack(side="left", padx=5)

        labels = [point.label for point in self.snapshot.monthly_adjustments]
        stock_in = [point.stock_in for point in self.snapshot.monthly_adjustments]
        stock_out = [point.stock_out for point in self.snapshot.monthly_adjustments]
        manual = [point.manual_adjustments for point in self.snapshot.monthly_adjustments]

        fig = Figure(figsize=(4, 3), dpi=100)
        fig.patch.set_facecolor(CARD)
        ax = fig.add_subplot(111)
        ax.set_facecolor(CARD)

        x = range(len(labels))
        width = 0.25
        ax.bar([position - width for position in x], stock_in, width=width, color=CHART_COLORS[0])
        ax.bar(x, stock_out, width=width, color=CHART_COLORS[1])
        ax.bar([position + width for position in x], manual, width=width, color=CHART_COLORS[2])

        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, color=MUTED_FOREGROUND)

        for spine in ["top", "right", "left", "bottom"]:
            ax.spines[spine].set_visible(False)
        ax.get_yaxis().set_visible(False)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

        footer = tk.Frame(frame, bg=CARD)
        footer.pack(fill="x")
        tk.Label(
            footer,
            text="Stock activity stable the past month ↗",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
        ).pack(anchor="w")
        tk.Label(
            footer,
            text="Tracking automated stock in/out + manual adjustments",
            bg=CARD,
            fg=MUTED_FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_SM),
        ).pack(anchor="w")

    def create_condition_summary_chart(self, parent, col):
        wrapper = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        wrapper.grid(row=0, column=col, sticky="nsew", padx=10, pady=10)
        frame = tk.Frame(wrapper, bg=CARD, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(
            frame,
            text="Inventory Condition Summary",
            bg=CARD,
            fg=FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
        ).pack(anchor="w")
        tk.Label(
            frame,
            text="Good vs Damaged vs Expired",
            bg=CARD,
            fg=MUTED_FOREGROUND,
            font=(FONT_FAMILY, FONT_SIZE_SM),
        ).pack(anchor="w", pady=(0, 20))

        labels = [point.label for point in self.snapshot.condition_summary]
        amounts = [point.quantity for point in self.snapshot.condition_summary]
        total = sum(amounts)
        if total > 0:
            values = [(amount / total) * 100 for amount in amounts]
        else:
            values = [100] if amounts else []

        fig = Figure(figsize=(3, 3), dpi=100)
        fig.patch.set_facecolor(CARD)
        ax = fig.add_subplot(111)

        colors = CHART_COLORS[0], CHART_COLORS[1], CHART_COLORS[2], CHART_COLORS[4]
        ax.pie(values, colors=colors, startangle=90, wedgeprops=dict(width=0.4))
        center_text = f"{int(values[0])}% Good" if values else "0% Good"
        ax.text(0, 0, center_text, ha="center", va="center", fontsize=14, fontweight="bold", color=FOREGROUND)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        legend_frame = tk.Frame(frame, bg=CARD)
        legend_frame.pack(fill="x", pady=(20, 0))
        legend_frame.grid_columnconfigure(0, weight=1)
        legend_frame.grid_columnconfigure(1, weight=1)

        for index, label in enumerate(labels):
            item = tk.Frame(legend_frame, bg=SECONDARY, padx=10, pady=8)
            item.grid(row=index // 2, column=index % 2, sticky="nsew", padx=5, pady=5)

            tk.Label(item, text="●", fg=colors[index % len(colors)], bg=SECONDARY).pack(side="left", padx=(0, 5))
            tk.Label(
                item,
                text=label,
                bg=SECONDARY,
                fg=MUTED_FOREGROUND,
                font=(FONT_FAMILY, FONT_SIZE_SM),
            ).pack(side="left")
            tk.Label(
                item,
                text=amounts[index],
                bg=SECONDARY,
                fg=FOREGROUND,
                font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
            ).pack(side="right")
