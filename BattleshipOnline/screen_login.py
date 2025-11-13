# screen_login.py
import tkinter as tk
from base_screen import BaseScreen
from theme import *

class LoginScreen(BaseScreen):
    def __init__(self, master, go_register, on_login):
        super().__init__(master)
        c = self.card()
        tk.Label(c, text="⚓ Battleship — Đăng nhập",
                 bg=COL_CARD, fg=COL_ACCENT, font=FONT_H1).pack(pady=(22,6))
        tk.Label(c, text="Đăng nhập để vào sảnh",
                 bg=COL_CARD, fg=COL_MUTED, font=FONT_SUB).pack()

        self.user = self._input(c, "Tên đăng nhập")
        self.pw = self._input(c, "Mật khẩu", show="•")

        tk.Button(c, text="Đăng nhập", bg=COL_BTN, fg=COL_BTN_TEXT,
                  font=FONT_BTN, relief="flat",
                  command=lambda: on_login(self.user.get().strip() or "Guest")
                  ).pack(pady=(10,6), ipadx=10, ipady=4)
        tk.Button(c, text="Chưa có tài khoản? Đăng ký →", bg=COL_CARD,
                  fg=COL_ACCENT, relief="flat", cursor="hand2",
                  command=go_register).pack()

    def _input(self, parent, label, show=None):
        wrap = tk.Frame(parent, bg=COL_CARD)
        wrap.pack(fill="x", padx=36, pady=6)
        tk.Label(wrap, text=label, bg=COL_CARD, fg=COL_TEXT).pack(anchor="w")
        e = tk.Entry(wrap, show=show, bg="#314863", fg=COL_TEXT,
                     insertbackground=COL_TEXT, relief="flat")
        e.pack(fill="x", ipady=5)
        return e
