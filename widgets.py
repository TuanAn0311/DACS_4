# widgets.py
import tkinter as tk
from theme import *

class Board(tk.Frame):
    def __init__(self, master, title="", show_ships=False, on_click=None):
        super().__init__(master, bg=COL_BG2)
        self.on_click = on_click
        tk.Label(self, text=title, bg=COL_BG2, fg=COL_TEXT, font=FONT_H2).pack()
        self.canvas = tk.Canvas(self, width=GRID_N*CELL+2, height=GRID_N*CELL+2,
                                bg="#10263f", highlightthickness=0)
        self.canvas.pack(pady=6)
        self.state = [[0]*GRID_N for _ in range(GRID_N)]
        self._draw_grid()
        if show_ships:
            self._place_demo_ships()
        if on_click:
            self.canvas.bind("<Button-1>", self._click)

    def _draw_grid(self):
        for i in range(GRID_N):
            for j in range(GRID_N):
                x0, y0 = j*CELL, i*CELL
                x1, y1 = x0+CELL, y0+CELL
                self.canvas.create_rectangle(x0, y0, x1, y1,
                                             outline="#1f3a56", fill="#0e2236")

    def _place_demo_ships(self):
        ships = [((1,1),(1,5)), ((4,2),(4,5)), ((7,7),(9,7)), ((8,1),(8,2))]
        for (r1,c1),(r2,c2) in ships:
            self._draw_ship(r1, c1, r2, c2)

    def _draw_ship(self, r1, c1, r2, c2):
        x0, y0 = c1*CELL, r1*CELL
        x1, y1 = (c2+1)*CELL, (r2+1)*CELL
        self.canvas.create_rectangle(x0+4, y0+8, x1-4, y1-8,
                                     fill="#9fb3c8", outline="")
        if r1 == r2:
            self.canvas.create_polygon(x1-4, (y0+y1)//2, x1+10, y0+8, x1+10, y1-8,
                                       fill="#bcd0e0", outline="")
        else:
            self.canvas.create_polygon((x0+x1)//2, y0-10, x0+8, y0+4, x1-8, y0+4,
                                       fill="#bcd0e0", outline="")
        self.canvas.create_rectangle(x0+CELL, y0+6, x0+CELL+10, y0+16,
                                     fill="#e3edf7", outline="")

    def _click(self, e):
        c = e.x // CELL
        r = e.y // CELL
        if 0 <= r < GRID_N and 0 <= c < GRID_N:
            if self.on_click:
                self.on_click(r, c)

    def mark(self, r, c, hit):
        if self.state[r][c] != 0:
            return
        self.state[r][c] = 1 if hit else 2
        x = c*CELL + CELL//2
        y = r*CELL + CELL//2
        color = "#ffd166" if hit else "#89c2d9"
        for rad in range(6, CELL//2, 6):
            self.canvas.create_oval(x-rad, y-rad, x+rad, y+rad,
                                    outline=color, width=2)
            self.canvas.update()
        if hit:
            self.canvas.create_text(x, y, text="💥", font=("Segoe UI", 14))
        else:
            self.canvas.create_oval(x-6, y-6, x+6, y+6,
                                    outline="#6aa2c0", width=2)
