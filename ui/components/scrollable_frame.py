import tkinter as tk
from tkinter import ttk
import platform

class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        bg_color = kwargs.pop("bg", "#FFFFFF")
        super().__init__(parent, *args, **kwargs)

       
        self.canvas = tk.Canvas(self, highlightthickness=0, bg=bg_color)
        
  
        
        self.scrollable_frame = ttk.Frame(self.canvas, style="TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind mousewheel events
        self.bind_mouse_scroll(self.canvas)
        self.bind_mouse_scroll(self.scrollable_frame)
        
        # Ensure the frame width matches the canvas width
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def bind_mouse_scroll(self, widget):
    
        widget.bind("<MouseWheel>", self._on_mousewheel)
    
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)
        
        # recursively bind for all children
        for child in widget.winfo_children():
            self.bind_mouse_scroll(child)

    def _on_mousewheel(self, event):
        if platform.system() == "Darwin":
            # macOS event.delta is usually larger, and direction is reversed compared to Windows for some reason in Tkinter
            self.canvas.yview_scroll(-1 * int(event.delta), "units")
        elif platform.system() == "Windows":
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        else:
        
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        
        # prevent propagation to parent if we handled it? 
        # usually returning a break stops propagation, but we might want it to bubble if we are at the edge
        # for now, let us just scroll to infinity I guess 
