# app.py
import tkinter as tk
from screen_login import LoginScreen
from screen_register import RegisterScreen
from screen_lobby import LobbyScreen
from screen_battle import BattleScreen
from screen_result import ResultScreen
from screen_admin import AdminScreen

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Battleship — Modern UI")
        self.geometry("1200x780")
        self.username = None
        self._show_login()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    # === LOGIN ===
    def _show_login(self):
        self._clear()
        LoginScreen(self, self._show_register, self._on_login)

    # === REGISTER ===
    def _show_register(self):
        self._clear()
        RegisterScreen(self, self._show_login, self._on_register)

    def _on_register(self, username, password):
        tk.messagebox.showinfo("Đăng ký thành công", f"Tài khoản '{username}' đã được tạo!")
        self._show_login()

    # === LOBBY ===
    def _show_lobby(self):
        self._clear()
        LobbyScreen(self, self.username or "Guest",
                    self._show_battle,
                    self._show_login,
                    self._show_admin)

    # === BATTLE ===
    def _show_battle(self):
        self._clear()
        BattleScreen(self, self.username or "Guest",
                     self._show_lobby,
                     self._show_result)

    # === RESULT ===
    def _show_result(self, winner, turns, hits, misses):
        self._clear()
        ResultScreen(self, winner, turns, hits, misses, self._show_lobby)

    # === ADMIN ===
    def _show_admin(self):
        self._clear()
        AdminScreen(self, self._show_lobby)

    # === LOGIN SUCCESS ===
    def _on_login(self, username):
        self.username = username or "Guest"
        self._show_lobby()

if __name__ == "__main__":
    app = App()
    app.mainloop()
