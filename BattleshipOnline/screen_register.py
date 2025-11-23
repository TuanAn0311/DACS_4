# screen_register.py
import tkinter as tk
import tkinter.messagebox as messagebox
from base_screen import BaseScreen
from theme import *
from db import register_user


class RegisterScreen(BaseScreen):
    def __init__(self, master, go_login, on_register):
        super().__init__(master)

        self.go_login = go_login
        self.on_register = on_register

        c = self.card()

        tk.Label(c, text="⚓ Battleship — Đăng ký",
                 bg=COL_CARD, fg=COL_ACCENT, font=FONT_H1).pack(pady=(22, 6))

        tk.Label(c, text="Tạo tài khoản mới để bắt đầu chơi",
                 bg=COL_CARD, fg=COL_MUTED, font=FONT_SUB).pack()

        self.user = self._input(c, "Tên đăng nhập")
        self.pw = self._input(c, "Mật khẩu", show="•")
        self.pw2 = self._input(c, "Xác nhận mật khẩu", show="•")

        tk.Button(c, text="Đăng ký",
                  bg=COL_ACCENT, fg="#0b132b",
                  font=FONT_BTN, relief="flat",
                  command=self._on_register).pack(pady=(12, 6), ipadx=10, ipady=4)

        tk.Button(c, text="← Quay lại đăng nhập",
                  bg=COL_CARD, fg=COL_ACCENT,
                  relief="flat", cursor="hand2",
                  command=self.go_login).pack()


    def _input(self, parent, label, show=None):
        wrap = tk.Frame(parent, bg=COL_CARD)
        wrap.pack(fill="x", padx=36, pady=6)

        tk.Label(wrap, text=label,
                 bg=COL_CARD, fg=COL_TEXT).pack(anchor="w")

        e = tk.Entry(wrap,
                     show=show,
                     bg="#314863",
                     fg=COL_TEXT,
                     insertbackground=COL_TEXT,
                     relief="flat")
        e.pack(fill="x", ipady=5)

        return e


    # ================== REGISTER ==================
    def _on_register(self):
        username = self.user.get().strip()
        pw1 = self.pw.get().strip()
        pw2 = self.pw2.get().strip()

        if not username or not pw1 or not pw2:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ!")
            return

        if pw1 != pw2:
            messagebox.showerror("Lỗi", "Mật khẩu xác nhận không trùng khớp!")
            return

        ok, msg = register_user(username, pw1)

        if ok:
            messagebox.showinfo("Thành công", msg)
            self.go_login()
        else:
            messagebox.showerror("Lỗi", msg)
