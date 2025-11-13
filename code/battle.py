# Battleship UI — Full Modern UI (Login, Register, Lobby, Battle x2 boards)
# Tkinter thuần, không dùng màu có alpha; mọi hình ảnh tàu/hiệu ứng vẽ bằng Canvas.

import tkinter as tk
from tkinter import messagebox
import random

# ======= Theme =======
COL_BG1 = "#0b132b"
COL_BG2 = "#1c2541"
COL_CARD = "#2a3b57"
COL_ACCENT = "#5bc0be"
COL_TEXT = "#e6f1ff"
COL_MUTED = "#9bb0c9"
COL_BTN = "#3b5f7a"
COL_BTN_TEXT = "#eaf6ff"

FONT_H1 = ("Segoe UI Semibold", 22)
FONT_H2 = ("Segoe UI Semibold", 16)
FONT_SUB = ("Segoe UI", 11)
FONT_BTN = ("Segoe UI", 10, "bold")

GRID_N = 10
CELL = 38

# ======= Helpers =======
def draw_vertical_gradient(canvas, w, h, color_top, color_bottom):
    r1, g1, b1 = canvas.winfo_rgb(color_top)
    r2, g2, b2 = canvas.winfo_rgb(color_bottom)
    for i in range(h):
        t = i / max(1, h-1)
        nr = int(r1 + (r2 - r1) * t) // 256
        ng = int(g1 + (g2 - g1) * t) // 256
        nb = int(b1 + (b2 - b1) * t) // 256
        canvas.create_line(0, i, w, i, fill=f"#{nr:02x}{ng:02x}{nb:02x}")

# ======= Core Base Screen =======
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
        # border line
        border = tk.Frame(card, bg="#47658a")
        border.place(relx=0, rely=0, relwidth=1, relheight=1)
        inner = tk.Frame(card, bg=COL_CARD)
        inner.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1, x=-4, y=-4)
        return inner

# ======= Login =======
class LoginScreen(BaseScreen):
    def __init__(self, master, go_register, on_login):
        super().__init__(master)
        c = self.card()
        tk.Label(c, text="⚓ Battleship — Đăng nhập", bg=COL_CARD, fg=COL_ACCENT, font=FONT_H1).pack(pady=(22,6))
        tk.Label(c, text="Đăng nhập để vào sảnh", bg=COL_CARD, fg=COL_MUTED, font=FONT_SUB).pack()

        self.user = self._input(c, "Tên đăng nhập")
        self.pw = self._input(c, "Mật khẩu", show="•")

        tk.Button(c, text="Đăng nhập", bg=COL_BTN, fg=COL_BTN_TEXT, font=FONT_BTN, relief="flat",
                  activebackground="#2d4a62", command=lambda: on_login(self.user.get().strip() or "Guest")).pack(pady=(10,6), ipadx=10, ipady=4)
        tk.Button(c, text="Chưa có tài khoản? Đăng ký →", bg=COL_CARD, fg=COL_ACCENT, relief="flat",
                  cursor="hand2", command=go_register).pack()

    def _input(self, parent, label, show=None):
        wrap = tk.Frame(parent, bg=COL_CARD)
        wrap.pack(fill="x", padx=36, pady=6)
        tk.Label(wrap, text=label, bg=COL_CARD, fg=COL_TEXT).pack(anchor="w")
        e = tk.Entry(wrap, show=show, bg="#314863", fg=COL_TEXT, insertbackground=COL_TEXT, relief="flat")
        e.pack(fill="x", ipady=5)
        return e

# ======= Register =======
class RegisterScreen(BaseScreen):
    def __init__(self, master, back_login):
        super().__init__(master)
        c = self.card(520, 480)
        tk.Label(c, text="🪶 Tạo tài khoản mới", bg=COL_CARD, fg=COL_ACCENT, font=FONT_H1).pack(pady=(22,6))
        self.user = self._input(c, "Tên đăng nhập")
        self.email = self._input(c, "Email")
        self.pw = self._input(c, "Mật khẩu", show="•")
        self.cf = self._input(c, "Xác nhận mật khẩu", show="•")
        tk.Button(c, text="Đăng ký", bg=COL_BTN, fg=COL_BTN_TEXT, font=FONT_BTN, relief="flat",
                  command=lambda: messagebox.showinfo("Thành công", "Đăng ký thành công! Đăng nhập để tiếp tục.")).pack(pady=(8,6), ipadx=10, ipady=4)
        tk.Button(c, text="← Quay lại đăng nhập", bg=COL_CARD, fg=COL_ACCENT, relief="flat", cursor="hand2",
                  command=back_login).pack()

    def _input(self, parent, label, show=None):
        wrap = tk.Frame(parent, bg=COL_CARD)
        wrap.pack(fill="x", padx=36, pady=6)
        tk.Label(wrap, text=label, bg=COL_CARD, fg=COL_TEXT).pack(anchor="w")
        e = tk.Entry(wrap, show=show, bg="#314863", fg=COL_TEXT, insertbackground=COL_TEXT, relief="flat")
        e.pack(fill="x", ipady=5)
        return e

# ======= Lobby with image-like room cards (Canvas-only) =======
class LobbyScreen(BaseScreen):
    def __init__(self, master, username, go_battle, logout):
        super().__init__(master)
        self.username = username
        self.go_battle = go_battle
        self.logout = logout
        tk.Label(self.bg, text=f"⚓ Sảnh — Xin chào, {username}", bg=COL_BG2, fg=COL_ACCENT, font=FONT_H1).place(relx=0.5, rely=0.08, anchor="center")
        self._draw_gallery()
        tk.Button(self.bg, text="Đăng xuất", bg=COL_BTN, fg=COL_BTN_TEXT, relief="flat",
                  command=self.logout).place(relx=0.5, rely=0.92, anchor="center", width=140, height=36)

    def _draw_gallery(self):
        area = tk.Frame(self.bg, bg=COL_BG2)
        area.place(relx=0.5, rely=0.5, anchor="center")
        self.cards = []
        for i in range(6):
            cv = tk.Canvas(area, width=220, height=170, bg=COL_CARD, highlightthickness=0, cursor="hand2")
            cv.grid(row=i//3, column=i%3, padx=16, pady=16)
            # gradient hợp lệ (không alpha)
            for y in range(170):
                if y < 70:
                    color = "#334c6b"
                elif y < 120:
                    color = "#2d4563"
                else:
                    color = "#263b58"
                cv.create_line(0, y, 220, y, fill=color)
            # vệt sóng nhẹ
            for x in range(0, 220, 22):
                cv.create_arc(x-30, 75, x+30, 115, start=0, extent=180, style="arc", outline="#5b7ea3")
            # tàu minh hoạ
            cv.create_rectangle(60, 98, 140, 110, fill="#9fb3c8", outline="")
            cv.create_polygon(140, 104, 160, 98, 160, 110, fill="#9fb3c8", outline="")
            cv.create_oval(68, 90, 78, 98, fill="#c7d6e6", outline="")
            # text
            cv.create_text(18, 18, text=f"#{i+1:02d}", fill=COL_MUTED, anchor="w", font=("Segoe UI", 10, "bold"))
            players = random.randint(1, 2)
            cv.create_text(18, 38, text=f"👤 {players}/2", fill=COL_TEXT, anchor="w", font=("Segoe UI", 11))
            # nút join
            btn = tk.Button(cv, text="Tham gia", bg=COL_ACCENT, fg="#0b132b", relief="flat",
                             command=self.go_battle)
            cv.create_window(110, 136, window=btn, width=110, height=28)
            # hover sáng nhẹ
            def on_enter(e, canv=cv):
                canv.configure(bg="#355071")
            def on_leave(e, canv=cv):
                canv.configure(bg=COL_CARD)
            cv.bind("<Enter>", on_enter)
            cv.bind("<Leave>", on_leave)
            self.cards.append(cv)

# ======= Battle: two boards; my board shows ships, enemy board empty =======
class BattleScreen(BaseScreen):
    def __init__(self, master, username, back_lobby):
        super().__init__(master)
        self.username = username
        self.back_lobby = back_lobby
        tk.Label(self.bg, text=f"🚢 Trận đấu — {username}", bg=COL_BG2, fg=COL_ACCENT, font=FONT_H1).place(relx=0.5, rely=0.07, anchor="center")

        wrap = tk.Frame(self.bg, bg=COL_BG2)
        wrap.place(relx=0.5, rely=0.55, anchor="center")

        # My board (with ships)
        self.my_board = Board(wrap, title="Bàn của bạn", show_ships=True)
        self.my_board.grid(row=0, column=0, padx=16)
        # Enemy board (no ships)
        self.enemy_board = Board(wrap, title="Bàn đối thủ", show_ships=False)
        self.enemy_board.grid(row=0, column=1, padx=16)
        self.enemy_board.bind_click(self._enemy_click)

        tk.Button(self.bg, text="← Quay lại sảnh", bg=COL_BTN, fg=COL_BTN_TEXT, relief="flat",
                  command=self.back_lobby).place(relx=0.5, rely=0.92, anchor="center", width=160, height=36)

    def _enemy_click(self, r, c):
        # demo: xác suất trúng 1/3
        hit = (r * 7 + c * 5) % 3 == 0
        self.enemy_board.mark(r, c, hit)

class Board(tk.Frame):
    def __init__(self, master, title="", show_ships=False):
        super().__init__(master, bg=COL_BG2)
        tk.Label(self, text=title, bg=COL_BG2, fg=COL_TEXT, font=FONT_H2).pack()
        self.canvas = tk.Canvas(self, width=GRID_N*CELL+2, height=GRID_N*CELL+2, bg="#10263f", highlightthickness=0)
        self.canvas.pack(pady=6)
        self.state = [[0]*GRID_N for _ in range(GRID_N)]  # 0 none, 1 hit, 2 miss
        self._draw_grid()
        if show_ships:
            self._place_demo_ships()

    def _draw_grid(self):
        for i in range(GRID_N):
            for j in range(GRID_N):
                x0, y0 = j*CELL, i*CELL
                x1, y1 = x0+CELL, y0+CELL
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="#1f3a56", fill="#0e2236")

    def _place_demo_ships(self):
        ships = [((1,1),(1,5)), ((4,2),(4,5)), ((7,7),(9,7)), ((8,1),(8,2))]
        for (r1,c1),(r2,c2) in ships:
            self._draw_ship(r1, c1, r2, c2)

    def _draw_ship(self, r1, c1, r2, c2):
        # Vẽ thân tàu kiểu capsule + cabin
        x0, y0 = c1*CELL, r1*CELL
        x1, y1 = (c2+1)*CELL, (r2+1)*CELL
        # thân
        self.canvas.create_rectangle(x0+4, y0+8, x1-4, y1-8, fill="#9fb3c8", outline="")
        # mũi (nếu tàu ngang)
        if r1 == r2:
            self.canvas.create_polygon(x1-4, (y0+y1)//2, x1+10, y0+8, x1+10, y1-8, fill="#bcd0e0", outline="")
        else:
            self.canvas.create_polygon((x0+x1)//2, y0-10, x0+8, y0+4, x1-8, y0+4, fill="#bcd0e0", outline="")
        # cabin
        self.canvas.create_rectangle(x0+CELL, y0+6, x0+CELL+10, y0+16, fill="#e3edf7", outline="")

    def bind_click(self, cb):
        def handler(e):
            c = e.x // CELL
            r = e.y // CELL
            if 0 <= r < GRID_N and 0 <= c < GRID_N:
                cb(r, c)
        self.canvas.bind("<Button-1>", handler)

    def mark(self, r, c, hit):
        # tránh ghi đè quá nhiều
        if self.state[r][c] != 0:
            return
        self.state[r][c] = 1 if hit else 2
        x = c*CELL + CELL//2
        y = r*CELL + CELL//2
        color = "#ffd166" if hit else "#89c2d9"
        # hiệu ứng nổ nhẹ bằng các vòng tròn
        for rad in range(6, CELL//2, 6):
            self.canvas.create_oval(x-rad, y-rad, x+rad, y+rad, outline=color, width=2)
            self.canvas.after(20)
            self.canvas.update()
        if hit:
            self.canvas.create_text(x, y, text="💥", font=("Segoe UI", 14))
        else:
            self.canvas.create_oval(x-6, y-6, x+6, y+6, outline="#6aa2c0", width=2)

# ======= App =======
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

    def _show_login(self):
        self._clear()
        LoginScreen(self, self._show_register, self._on_login)

    def _show_register(self):
        self._clear()
        RegisterScreen(self, self._show_login)

    def _show_lobby(self):
        self._clear()
        LobbyScreen(self, self.username or "Guest", self._show_battle, self._show_login)

    def _show_battle(self):
        self._clear()
        BattleScreen(self, self.username or "Guest", self._show_lobby)

    def _on_login(self, username):
        self.username = username or "Guest"
        self._show_lobby()

if __name__ == "__main__":
    app = App()
    app.mainloop()