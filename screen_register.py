# screen_register.py
import tkinter as tk
from base_screen import BaseScreen
from theme import *

class RegisterScreen(BaseScreen):
    def __init__(self, master, go_login, on_register):
        super().__init__(master)
        c = self.card()

        tk.Label(c, text="⚓ Battleship — Đăng ký",
                 bg=COL_CARD, fg=COL_ACCENT, font=FONT_H1).pack(pady=(22,6))
        tk.Label(c, text="Tạo tài khoản mới để bắt đầu chơi",
                 bg=COL_CARD, fg=COL_MUTED, font=FONT_SUB).pack()

        self.user = self._input(c, "Tên đăng nhập")
        self.pw = self._input(c, "Mật khẩu", show="•")
        self.pw2 = self._input(c, "Xác nhận mật khẩu", show="•")

        tk.Button(c, text="Đăng ký", bg=COL_ACCENT, fg="#0b132b",
                  font=FONT_BTN, relief="flat",
                  command=self._on_register).pack(pady=(12,6), ipadx=10, ipady=4)

        tk.Button(c, text="← Quay lại đăng nhập", bg=COL_CARD,
                  fg=COL_ACCENT, relief="flat", cursor="hand2",
                  command=go_login).pack()

        self.on_register = on_register

    def _input(self, parent, label, show=None):
        wrap = tk.Frame(parent, bg=COL_CARD)
        wrap.pack(fill="x", padx=36, pady=6)
        tk.Label(wrap, text=label, bg=COL_CARD, fg=COL_TEXT).pack(anchor="w")
        e = tk.Entry(wrap, show=show, bg="#314863", fg=COL_TEXT,
                     insertbackground=COL_TEXT, relief="flat")
        e.pack(fill="x", ipady=5)
        return e

    def _on_register(self):
        user = self.user.get().strip()
        pw1 = self.pw.get().strip()
        pw2 = self.pw2.get().strip()

        if not user or not pw1 or not pw2:
            tk.messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin!")
            return
        if pw1 != pw2:
            tk.messagebox.showerror("Lỗi", "Mật khẩu xác nhận không khớp!")
            return
        self.on_register(user, pw1)
