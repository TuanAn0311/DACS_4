# screen_lobby.py
import tkinter as tk
import random
from base_screen import BaseScreen
from theme import *

class LobbyScreen(BaseScreen):
    def __init__(self, master, username, go_battle, logout, go_admin):
        super().__init__(master)
        self.username = username
        tk.Label(self.bg, text=f"⚓ Sảnh — Xin chào, {username}",
                 bg=COL_BG2, fg=COL_ACCENT, font=FONT_H1).place(
            relx=0.5, rely=0.08, anchor="center")

        self._draw_rooms(go_battle)

        # nút admin + logout
        tk.Button(self.bg, text="Trang Admin", bg=COL_BTN, fg=COL_BTN_TEXT,
                  relief="flat", command=go_admin).place(
            relx=0.35, rely=0.92, anchor="center", width=140, height=36)

        tk.Button(self.bg, text="Đăng xuất", bg=COL_BTN, fg=COL_BTN_TEXT,
                  relief="flat", command=logout).place(
            relx=0.65, rely=0.92, anchor="center", width=140, height=36)

    def _draw_rooms(self, go_battle):
        area = tk.Frame(self.bg, bg=COL_BG2)
        area.place(relx=0.5, rely=0.5, anchor="center")
        for i in range(6):
            cv = tk.Canvas(area, width=220, height=170,
                           bg=COL_CARD, highlightthickness=0, cursor="hand2")
            cv.grid(row=i//3, column=i%3, padx=16, pady=16)
            for y in range(170):
                color = "#334c6b" if y < 70 else "#263b58"
                cv.create_line(0, y, 220, y, fill=color)
            cv.create_text(18, 18, text=f"Phòng #{i+1:02d}",
                           fill=COL_MUTED, anchor="w",
                           font=("Segoe UI", 10, "bold"))
            players = random.randint(1, 2)
            cv.create_text(18, 38, text=f"👤 {players}/2",
                           fill=COL_TEXT, anchor="w", font=("Segoe UI", 11))
            btn = tk.Button(cv, text="Tham gia", bg=COL_ACCENT,
                            fg="#0b132b", relief="flat",
                            command=go_battle)
            cv.create_window(110, 136, window=btn, width=110, height=28)
