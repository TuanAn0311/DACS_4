import tkinter as tk
import tkinter.messagebox as messagebox
from base_screen import BaseScreen
from theme import *
from db import login_user, login_admin


class LoginScreen(BaseScreen):
    def __init__(self, master, go_register, on_login):
        super().__init__(master)
        self.master = master
        self.go_register = go_register
        self.on_login = on_login

        c = self.card()

        tk.Label(c, text="⚓ Battleship — Đăng nhập",
                 bg=COL_CARD, fg=COL_ACCENT, font=FONT_H1).pack(pady=(22, 6))

        tk.Label(c, text="Đăng nhập để vào hệ thống",
                 bg=COL_CARD, fg=COL_MUTED, font=FONT_SUB).pack()

        self.user = self._input(c, "Tên đăng nhập")
        self.pw = self._input(c, "Mật khẩu", show="•")

        tk.Button(c, text="Đăng nhập người chơi",
                  bg=COL_BTN, fg=COL_BTN_TEXT,
                  font=FONT_BTN, relief="flat",
                  command=self.login_player
                  ).pack(pady=(12, 6), ipadx=10, ipady=4)

        tk.Button(c, text="Đăng nhập quản trị",
                  bg=COL_ACCENT, fg="#0b132b",
                  font=FONT_BTN, relief="flat",
                  command=self.login_admin
                  ).pack(pady=(0, 4), ipadx=10, ipady=4)

        tk.Button(c, text="Chưa có tài khoản? Đăng ký →",
                  bg=COL_CARD,
                  fg=COL_ACCENT,
                  relief="flat",
                  cursor="hand2",
                  command=self.go_register).pack(pady=(6, 0))


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


    # ================== LOGIN PLAYER ==================
    def login_player(self):
        username = self.user.get().strip()
        password = self.pw.get().strip()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ tài khoản và mật khẩu!")
            return

        ok, result = login_user(username, password)

        if ok:
            self.master.username = username

            # ✅ GỬI TÊN LÊN SERVER
            if hasattr(self.master, "client"):
                self.master.client.set_name(username)

            messagebox.showinfo("Thành công", f"Chào {username}!")
            self.master._show_lobby()
        else:
            messagebox.showerror("Lỗi", result)


    # ================== LOGIN ADMIN ==================
    def login_admin(self):
        username = self.user.get().strip()
        password = self.pw.get().strip()

        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đủ tài khoản và mật khẩu!")
            return

        ok, result = login_admin(username, password)

        if ok:
            self.master.username = username

            if hasattr(self.master, "client"):
                self.master.client.set_name(username)

            messagebox.showinfo("Thành công", f"Xin chào quản trị: {username}")
            self.master._show_admin()
        else:
            messagebox.showerror("Lỗi", result)
