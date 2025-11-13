# base_screen.py
import tkinter as tk
from theme import *

def draw_vertical_gradient(canvas, w, h, color_top, color_bottom):
    r1, g1, b1 = canvas.winfo_rgb(color_top)
    r2, g2, b2 = canvas.winfo_rgb(color_bottom)
    for i in range(h):
        t = i / max(1, h-1)
        nr = int(r1 + (r2 - r1) * t) // 256
        ng = int(g1 + (g2 - g1) * t) // 256
        nb = int(b1 + (b2 - b1) * t) // 256
        canvas.create_line(0, i, w, i, fill=f"#{nr:02x}{ng:02x}{nb:02x}", tags="grad")

class BaseScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.bg = tk.Canvas(self, highlightthickness=0)
        self.bg.pack(fill="both", expand=True)
        self.bg.bind("<Configure>", self._redraw_bg)

    def _redraw_bg(self, e=None):
        self.bg.delete("grad")
        w, h = self.bg.winfo_width(), self.bg.winfo_height()
        draw_vertical_gradient(self.bg, w, h, COL_BG1, COL_BG2)

    def card(self, w=520, h=420):
        card = tk.Frame(self.bg, bg=COL_CARD, bd=0, highlightthickness=0)
        card.place(relx=0.5, rely=0.5, anchor="center", width=w, height=h)
        border = tk.Frame(card, bg="#47658a")
        border.place(relx=0, rely=0, relwidth=1, relheight=1)
        inner = tk.Frame(card, bg=COL_CARD)
        inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1, x=-4, y=-4)
        return inner
