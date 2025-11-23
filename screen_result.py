# screen_result.py
import tkinter as tk
from base_screen import BaseScreen
from theme import *


class ResultScreen(BaseScreen):
    def __init__(self, master, winner, turns, hits, misses,
                 back_lobby, play_again):
        super().__init__(master)

        c = self.card(520, 360)

        tk.Label(
            c,
            text="📜 Kết quả trận đấu",
            bg=COL_CARD,
            fg=COL_ACCENT,
            font=FONT_H1
        ).pack(pady=(20, 6))

        tk.Label(
            c,
            text=f"Người thắng: {winner}",
            bg=COL_CARD,
            fg=COL_TEXT,
            font=FONT_H2
        ).pack()

        tk.Label(
            c,
            text=f"Số lượt bắn: {turns}",
            bg=COL_CARD,
            fg=COL_MUTED
        ).pack(pady=2)

        tk.Label(
            c,
            text=f"Trúng: {hits} | Trượt: {misses}",
            bg=COL_CARD,
            fg=COL_MUTED
        ).pack(pady=2)

        btn_frame = tk.Frame(c, bg=COL_CARD)
        btn_frame.pack(pady=18)

        tk.Button(
            btn_frame,
            text="Chơi lại",
            bg=COL_ACCENT,
            fg="#0b132b",
            relief="flat",
            command=play_again
        ).pack(side="left", padx=8, ipadx=10, ipady=4)

        tk.Button(
            btn_frame,
            text="Quay về sảnh",
            bg=COL_BTN,
            fg=COL_BTN_TEXT,
            relief="flat",
            command=back_lobby
        ).pack(side="left", padx=8, ipadx=10, ipady=4)
