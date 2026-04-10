import tkinter as tk
from tkinter import ttk
from ui.styles import *

def create_rounded_rect(canvas, x1, y1, x2, y2, r, **kwargs):
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
    return canvas.create_polygon(points, smooth=True, **kwargs)

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, bg_color=None, fg_color=CARD, radius=32, padding=20, border_width=0, border_color=BORDER, **kwargs):
        # if bg_color is not provided, try to get it from parent
        if bg_color is None:
            try:
                bg_color = parent.cget("bg")
            except:
                bg_color = BACKGROUND
        
        super().__init__(parent, bg=bg_color, highlightthickness=0, **kwargs)
        
        self.fg_color = fg_color
        self.radius = radius
        self.padding = padding
        self.border_width = border_width
        self.border_color = border_color


        
        self.bind("<Configure>", self.on_configure)
        
       
        self.inner_frame = tk.Frame(self, bg=fg_color)
        self.window_item = None

    def on_configure(self, event):
        self.delete("bg_rect")
        w, h = event.width, event.height
        
        if self.border_width > 0:
   
            create_rounded_rect(self, 0, 0, w, h, self.radius, fill=self.border_color, outline="", tags="bg_rect")
   
            create_rounded_rect(self, self.border_width, self.border_width, w-self.border_width, h-self.border_width, self.radius, fill=self.fg_color, outline="", tags="bg_rect")
        else:
           
            create_rounded_rect(self, 0, 0, w, h, self.radius, fill=self.fg_color, outline="", tags="bg_rect")
            
        self.tag_lower("bg_rect")
        
        inner_w = w - (self.padding * 2)
        inner_h = h - (self.padding * 2)
        
        if self.window_item is None:
            self.window_item = self.create_window(
                w/2, h/2, 
                window=self.inner_frame, 
                width=inner_w, 
                height=inner_h,
                anchor="center"
            )
        else:
            self.coords(self.window_item, w/2, h/2)
            self.itemconfig(self.window_item, width=inner_w, height=inner_h)

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=120, height=40, radius=8, 
                 bg_color=None, fg_color=PRIMARY, text_color=PRIMARY_FOREGROUND, 
                 hover_color="#1E293B", style_type="primary", **kwargs):
        
        if bg_color is None:
            try:
                bg_color = parent.cget("bg")
            except:
                bg_color = BACKGROUND
                
        super().__init__(parent, width=width, height=height, bg=bg_color, highlightthickness=0, **kwargs)
        
        self.command = command
        self.text = text
        self.radius = radius
        self.fg_color = fg_color
        self.text_color = text_color
        self.hover_color = hover_color
        
        if style_type == "outline":
            self.fg_color = BACKGROUND
            self.text_color = FOREGROUND
            self.hover_color = MUTED
            self.border_color = BORDER
            self.has_border = True
        else:
            self.has_border = False
            
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
        self.draw()
        
    def draw(self):
        self.delete("all")
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        
        if self.has_border:
         
             create_rounded_rect(self, 0, 0, w, h, self.radius, fill=self.border_color, outline="")
          
             create_rounded_rect(self, 1, 1, w-1, h-1, self.radius, fill=self.fg_color, outline="", tags="shape")
        else:
            create_rounded_rect(self, 0, 0, w, h, self.radius, fill=self.fg_color, outline="", tags="shape")
            
        self.create_text(w/2, h/2, text=self.text, fill=self.text_color, font=(FONT_FAMILY, FONT_SIZE_BASE, "bold"), tags="text")
        
    def on_enter(self, e):
        self.itemconfig("shape", fill=self.hover_color)
        
    def on_leave(self, e):
        self.itemconfig("shape", fill=self.fg_color)
        
    def on_click(self, e):
        if self.command:
            self.command()
            
class RoundedEntry(tk.Canvas):
    def __init__(self, parent, textvariable=None, width=300, height=34, radius=18,
                 bg_color=None, fg_color=SECONDARY, border_color=BORDER, text_color=FOREGROUND,
                 font=(FONT_FAMILY, FONT_SIZE_BASE), **kwargs):
        
        if bg_color is None:
            try:
                bg_color = parent.cget("bg")
            except:
                bg_color = BACKGROUND

        super().__init__(parent, width=width, height=height, bg=bg_color,
                         highlightthickness=0)

        self.radius = radius
        self.fg_color = fg_color
        self.border_color = border_color
        self.text_color = text_color
        self.font = font

        self.entry = tk.Entry(self, textvariable=textvariable, bd=0,
                              bg=fg_color, fg=text_color, font=font, highlightthickness=0,
                              insertbackground=text_color)

        self.bind("<Configure>", self._draw)

    def _draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()

 
        create_rounded_rect(self, 0, 0, w, h, self.radius,
                            fill=self.border_color, outline="")


        create_rounded_rect(self, 1, 1, w-1, h-1, self.radius,
                            fill=self.fg_color, outline="")

        self.entry.place(x=12, y= (h // 2) - 10, width=w-24)
