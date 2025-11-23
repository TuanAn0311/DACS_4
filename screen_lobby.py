import tkinter as tk
import tkinter.messagebox as messagebox
from base_screen import BaseScreen
from theme import *


class LobbyScreen(BaseScreen):
    def __init__(self, master, username, go_battle, logout, go_admin):
        super().__init__(master)

        self.master = master
        self.username = username
        self.go_battle = go_battle

        tk.Label(self.bg, text=f"⚓ Sảnh — Xin chào, {username}",
                 bg=COL_BG2, fg=COL_ACCENT, font=FONT_H1).place(
            relx=0.5, rely=0.08, anchor="center")

        self.area = tk.Frame(self.bg, bg=COL_BG2)
        self.area.place(relx=0.5, rely=0.55, anchor="center")

        tk.Button(self.bg, text="Tạo phòng",
                  bg=COL_ACCENT, fg="#0b132b", relief="flat",
                  command=self._create_room).place(
            relx=0.5, rely=0.18, anchor="center",
            width=150, height=35)

        tk.Button(self.bg, text="🔄 Làm mới",
                  bg=COL_BTN, fg=COL_BTN_TEXT,
                  relief="flat",
                  command=self.refresh_rooms).place(
            relx=0.82, rely=0.18, anchor="center",
            width=120, height=35)

        tk.Button(self.bg, text="Trang Admin", bg=COL_BTN, fg=COL_BTN_TEXT,
                  relief="flat", command=go_admin).place(
            relx=0.35, rely=0.92, anchor="center", width=140, height=36)

        tk.Button(self.bg, text="Đăng xuất", bg=COL_BTN, fg=COL_BTN_TEXT,
                  relief="flat", command=logout).place(
            relx=0.65, rely=0.92, anchor="center", width=140, height=36)

        c = master.client
        c.on("ROOM_LIST", self._on_rooms)
        c.on("JOINED_ROOM", self._joined_room)
        c.on("WELCOME", self._welcome)
        c.on("ERROR", self._show_error)

        # Lấy danh sách phòng lần đầu
        c.send({"type": "GET_ROOMS"})

        # ✅ BẮT ĐẦU REALTIME TỰ ĐỘNG
        self._auto_refresh()

    # ================= REALTIME =================
    def _auto_refresh(self):
        """Tự động cập nhật phòng mỗi 1 giây"""
        try:
            self.master.client.send({"type": "GET_ROOMS"})
        except:
            pass

        # gọi lại sau 1000ms
        self.after(1000, self._auto_refresh)

    # ================= EVENTS =================
    def _welcome(self, msg):
        self.username = msg["username"]

    def refresh_rooms(self):
        self.master.client.send({"type": "GET_ROOMS"})

    def _create_room(self):
        self.master.client.send({"type": "CREATE_ROOM"})

    def _show_error(self, msg):
        messagebox.showwarning("Thông báo", msg["msg"])

    def _joined_room(self, msg):
        room = msg["room"]
        self.go_battle(room)

    def _on_rooms(self, msg):
        for w in self.area.winfo_children():
            w.destroy()

        rooms = msg["rooms"]

        if not rooms:
            tk.Label(self.area, text="(Chưa có phòng)",
                     bg=COL_BG2, fg=COL_MUTED).pack()
            return

        for i, r in enumerate(rooms):
            box = tk.Frame(self.area, width=230, height=140, bg=COL_CARD)
            box.grid(row=i//3, column=i % 3, padx=16, pady=16)

            tk.Label(box, text=f"Phòng {r['id']}",
                     fg=COL_TEXT, bg=COL_CARD, font=FONT_H2).pack(pady=(8, 2))

            tk.Label(box, text=f"👑 Chủ: {r['owner']}",
                     fg=COL_MUTED, bg=COL_CARD).pack()

            tk.Label(box, text=f"👤 {r['players']}/2",
                     fg=COL_MUTED, bg=COL_CARD).pack()

            if r["players"] >= 2:
                tk.Button(box, text="Phòng đầy",
                          bg="gray", fg="white",
                          relief="flat", state="disabled").pack(pady=8)
            else:
                tk.Button(box, text="Tham gia",
                          bg=COL_ACCENT, fg="#0b132b",
                          relief="flat",
                          command=lambda rid=r['id']: self._join(rid)).pack(pady=8)

    def _join(self, room):
        self.master.client.send({"type": "JOIN_ROOM", "room": room})
