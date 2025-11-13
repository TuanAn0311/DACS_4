# screen_battle.py
import tkinter as tk
from base_screen import BaseScreen
from widgets import Board
from theme import *

class BattleScreen(BaseScreen):
    def __init__(self, master, username, back_lobby, show_result):
        super().__init__(master)
        self.username = username
        tk.Label(self.bg, text=f"🚢 Trận đấu — {username}",
                 bg=COL_BG2, fg=COL_ACCENT, font=FONT_H1).place(
            relx=0.5, rely=0.07, anchor="center")

        main = tk.Frame(self.bg, bg=COL_BG2)
        main.place(relx=0.5, rely=0.55, anchor="center")

        # 2 bàn chơi
        self.my_board = Board(main, title="Bàn của bạn", show_ships=True)
        self.my_board.grid(row=0, column=0, padx=12)

        self.enemy_board = Board(main, title="Bàn đối thủ",
                                 show_ships=False,
                                 on_click=self._enemy_click)
        self.enemy_board.grid(row=0, column=1, padx=12)

        # khung chat bên phải
        chat = tk.Frame(main, bg=COL_CARD)
        chat.grid(row=0, column=2, padx=12, sticky="ns")
        tk.Label(chat, text="💬 Chat", bg=COL_CARD, fg=COL_TEXT,
                 font=FONT_H2).pack(anchor="w", padx=8, pady=(6,2))

        self.chat_box = tk.Text(chat, width=28, height=18,
                                bg="#1f3047", fg=COL_TEXT,
                                relief="flat")
        self.chat_box.pack(padx=6, pady=4)
        self.chat_box.insert("end", "Hệ thống: Bắt đầu trận đấu...\n")

        entry_wrap = tk.Frame(chat, bg=COL_CARD)
        entry_wrap.pack(fill="x", padx=6, pady=4)
        self.chat_entry = tk.Entry(entry_wrap, bg="#314863", fg=COL_TEXT,
                                   relief="flat")
        self.chat_entry.pack(side="left", fill="x", expand=True, ipady=3)
        tk.Button(entry_wrap, text="Gửi", bg=COL_ACCENT, fg="#0b132b",
                  relief="flat",
                  command=self._send_chat).pack(side="left", padx=(4,0))

        # nút quay lại + xem kết quả
        tk.Button(self.bg, text="← Quay lại sảnh", bg=COL_BTN,
                  fg=COL_BTN_TEXT, relief="flat",
                  command=back_lobby).place(
            relx=0.42, rely=0.92, anchor="center", width=160, height=36)

        tk.Button(self.bg, text="Xem kết quả", bg="#ff9f1c",
                  fg="#0b132b", relief="flat",
                  command=lambda: show_result(winner=username,
                                              turns=23, hits=12, misses=11)
                  ).place(
            relx=0.58, rely=0.92, anchor="center", width=160, height=36)

    def _enemy_click(self, r, c):
        hit = (r * 7 + c * 5) % 3 == 0
        self.enemy_board.mark(r, c, hit)
        self.chat_box.insert("end", f"Bạn bắn vào ({r},{c}) -> {'TRÚNG' if hit else 'trượt'}\n")
        self.chat_box.see("end")

    def _send_chat(self):
        msg = self.chat_entry.get().strip()
        if not msg:
            return
        self.chat_box.insert("end", f"Bạn: {msg}\n")
        self.chat_box.see("end")
        self.chat_entry.delete(0, "end")
