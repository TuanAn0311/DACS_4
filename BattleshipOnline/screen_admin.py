# screen_admin.py
import tkinter as tk
from base_screen import BaseScreen
from theme import *

class AdminScreen(BaseScreen):
    def __init__(self, master, back_lobby):
        super().__init__(master)
        self.back_lobby = back_lobby

        # ======= Header =======
        header = tk.Frame(self.bg, bg=COL_CARD, height=70)
        header.pack(fill="x", side="top")
        tk.Label(header, text="🛠️ BẢNG ĐIỀU KHIỂN ADMIN",
                 bg=COL_CARD, fg=COL_ACCENT, font=FONT_H1).pack(side="left", padx=30)
        tk.Button(header, text="← Về sảnh", bg=COL_BTN, fg=COL_BTN_TEXT,
                  relief="flat", command=self.back_lobby).pack(side="right", padx=30, pady=10, ipadx=10)

        # ======= Sidebar =======
        sidebar = tk.Frame(self.bg, bg=COL_BG1, width=240)
        sidebar.pack(side="left", fill="y")

        tk.Label(sidebar, text="Chức năng", bg=COL_BG1, fg=COL_MUTED, font=FONT_SUB).pack(anchor="w", padx=16, pady=(20, 6))

        self.menu_buttons = []
        self._add_menu_button(sidebar, "👥  Quản lý người dùng", self.show_users)
        self._add_menu_button(sidebar, "🏠  Quản lý phòng", self.show_rooms)
        self._add_menu_button(sidebar, "📜  Lịch sử trận đấu", self.show_history)

        # ======= Main content =======
        self.main_frame = tk.Frame(self.bg, bg=COL_BG2)
        self.main_frame.pack(side="left", fill="both", expand=True)

        self.show_users()

    def _add_menu_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, bg=COL_BG1, fg=COL_TEXT, font=FONT_SUB,
                        anchor="w", padx=20, pady=10, relief="flat",
                        activebackground=COL_ACCENT, activeforeground="#0b132b",
                        command=lambda b=len(self.menu_buttons): self._switch_panel(b, command))
        btn.pack(fill="x")
        self.menu_buttons.append(btn)

    def _switch_panel(self, index, show_func):
        for i, b in enumerate(self.menu_buttons):
            if i == index:
                b.configure(bg=COL_ACCENT, fg="#0b132b")
            else:
                b.configure(bg=COL_BG1, fg=COL_TEXT)
        self.clear_panel()
        show_func()

    def clear_panel(self):
        for w in self.main_frame.winfo_children():
            w.destroy()

    # =============== USERS PANEL ===============
    def show_users(self):
        title = tk.Label(self.main_frame, text="👥 Danh sách người dùng",
                         bg=COL_BG2, fg=COL_ACCENT, font=FONT_H2)
        title.pack(pady=20)
        card = tk.Frame(self.main_frame, bg=COL_CARD, bd=0)
        card.pack(padx=40, pady=10, fill="both", expand=True)

        lst = tk.Listbox(card, bg="#1f3047", fg=COL_TEXT, font=FONT_SUB,
                         selectbackground=COL_ACCENT, selectforeground="#0b132b",
                         borderwidth=0, highlightthickness=0)
        for u in ["admin", "player01", "player02", "guest"]:
            lst.insert("end", u)
        lst.pack(padx=20, pady=20, fill="both", expand=True)

        btns = tk.Frame(self.main_frame, bg=COL_BG2)
        btns.pack(pady=10)
        tk.Button(btns, text="Khóa", bg=COL_BTN, fg=COL_BTN_TEXT,
                  relief="flat", width=12).pack(side="left", padx=5)
        tk.Button(btns, text="Xóa", bg="#ff595e", fg="white",
                  relief="flat", width=12).pack(side="left", padx=5)

    # =============== ROOMS PANEL ===============
    def show_rooms(self):
        title = tk.Label(self.main_frame, text="🏠 Quản lý phòng đang hoạt động",
                         bg=COL_BG2, fg=COL_ACCENT, font=FONT_H2)
        title.pack(pady=20)
        card = tk.Frame(self.main_frame, bg=COL_CARD)
        card.pack(padx=40, pady=10, fill="both", expand=True)

        self.room_list = tk.Listbox(card, bg="#1f3047", fg=COL_TEXT, font=FONT_SUB,
                                    selectbackground=COL_ACCENT, selectforeground="#0b132b",
                                    borderwidth=0, highlightthickness=0)
        self.rooms = {
            "Phòng #01 (2/2)": ["player01", "player02"],
            "Phòng #02 (1/2)": ["guest"],
            "Phòng #03 (0/2)": []
        }
        for r in self.rooms.keys():
            self.room_list.insert("end", r)
        self.room_list.pack(padx=20, pady=20, fill="both", expand=True)
        self.room_list.bind("<Double-Button-1>", self.show_room_detail)

        tk.Button(self.main_frame, text="Đóng phòng", bg="#ff9f1c", fg="#0b132b",
                  relief="flat", width=15).pack(pady=10)

    def show_room_detail(self, event):
        try:
            idx = self.room_list.curselection()[0]
        except IndexError:
            return
        room_name = self.room_list.get(idx)
        players = self.rooms.get(room_name, [])

        detail = tk.Toplevel(self)
        detail.title(f"Chi tiết {room_name}")
        detail.geometry("360x240")
        detail.configure(bg=COL_BG2)

        tk.Label(detail, text=room_name, bg=COL_BG2, fg=COL_ACCENT,
                 font=FONT_H2).pack(pady=10)
        if not players:
            tk.Label(detail, text="(Phòng trống)", bg=COL_BG2,
                     fg=COL_MUTED, font=FONT_SUB).pack()
        else:
            for p in players:
                tk.Label(detail, text=f"👤 {p}", bg=COL_BG2,
                         fg=COL_TEXT, font=FONT_SUB).pack(anchor="w", padx=40, pady=4)

        tk.Button(detail, text="Đóng", bg=COL_BTN, fg=COL_BTN_TEXT,
                  relief="flat", command=detail.destroy).pack(pady=12)

    # =============== HISTORY PANEL ===============
    def show_history(self):
        title = tk.Label(self.main_frame, text="📜 Lịch sử trận đấu",
                         bg=COL_BG2, fg=COL_ACCENT, font=FONT_H2)
        title.pack(pady=20)
        card = tk.Frame(self.main_frame, bg=COL_CARD)
        card.pack(padx=40, pady=10, fill="both", expand=True)

        self.lst = tk.Listbox(card, bg="#1f3047", fg=COL_TEXT, font=FONT_SUB,
                              selectbackground=COL_ACCENT, selectforeground="#0b132b",
                              borderwidth=0, highlightthickness=0)
        matches = [
            "12:01 player01 vs player02 → player01 thắng",
            "12:05 guest vs player02 → player02 thắng",
            "12:10 player01 vs guest → player01 thắng"
        ]
        for m in matches:
            self.lst.insert("end", m)
        self.lst.pack(padx=20, pady=20, fill="both", expand=True)

        tk.Button(self.main_frame, text="Xem chi tiết", bg=COL_ACCENT, fg="#0b132b",
                  relief="flat", width=15, command=self.show_detail).pack(pady=10)

    def show_detail(self):
        try:
            index = self.lst.curselection()[0]
        except IndexError:
            return
        info = self.lst.get(index)
        detail = tk.Toplevel(self)
        detail.title("Chi tiết trận đấu")
        detail.geometry("400x280")
        detail.configure(bg=COL_BG2)
        tk.Label(detail, text="📋 Chi tiết trận đấu", bg=COL_BG2,
                 fg=COL_ACCENT, font=FONT_H2).pack(pady=8)
        tk.Label(detail, text=info, bg=COL_BG2, fg=COL_TEXT).pack(pady=4)

        stats = [
            ("Số lượt bắn", f"{20 + index}"),
            ("Số lượt trúng", f"{10 + index}"),
            ("Số lượt trượt", f"{10 - index if index < 3 else 7}"),
            ("Thời gian trận", f"{3 + index} phút")
        ]

        frame = tk.Frame(detail, bg=COL_CARD)
        frame.pack(padx=30, pady=10, fill="x")
        for s, v in stats:
            row = tk.Frame(frame, bg=COL_CARD)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=s + ":", bg=COL_CARD, fg=COL_TEXT, width=15, anchor="w").pack(side="left")
            tk.Label(row, text=v, bg=COL_CARD, fg=COL_MUTED, anchor="w").pack(side="left")

        tk.Button(detail, text="Đóng", bg=COL_BTN, fg=COL_BTN_TEXT,
                  relief="flat", command=detail.destroy).pack(pady=10)
