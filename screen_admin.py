import tkinter as tk
import tkinter.messagebox as messagebox
from base_screen import BaseScreen
from theme import *

class AdminScreen(BaseScreen):
    def __init__(self, master, back_lobby):
        super().__init__(master)
        self.master = master
        self.back_lobby = back_lobby
        self.current_room_data = [] 
        self.current_user_data = [] 
        self.detail_window = None

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
        self._add_menu_button(sidebar, "👥  Quản lý người dùng", self.req_users)
        self._add_menu_button(sidebar, "🏠  Quản lý phòng", self.req_rooms)
        self._add_menu_button(sidebar, "📜  Lịch sử trận đấu", self.req_history)

        # ======= Main content =======
        self.main_frame = tk.Frame(self.bg, bg=COL_BG2)
        self.main_frame.pack(side="left", fill="both", expand=True)

        # ======= SOCKET LISTENERS =======
        c = self.master.client
        c.on("ADMIN_USER_LIST", self._on_user_list)
        c.on("ADMIN_ROOM_LIST", self._on_room_list)
        c.on("ADMIN_HISTORY_LIST", self._on_history_list)
        c.on("ADMIN_ACTION_OK", self._on_success)
        c.on("ADMIN_ACTION_FAIL", self._on_fail)

        # Mặc định vào tab Users
        self.req_users()

    def _on_success(self, msg):
        messagebox.showinfo("Thành công", msg["msg"])
    
    def _on_fail(self, msg):
        messagebox.showerror("Lỗi", msg["msg"])

    def _add_menu_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, bg=COL_BG1, fg=COL_TEXT, font=FONT_SUB,
                        anchor="w", padx=20, pady=10, relief="flat",
                        activebackground=COL_ACCENT, activeforeground="#0b132b",
                        command=lambda: self._switch_panel(command))
        btn.pack(fill="x")
        self.menu_buttons.append(btn)

    def _switch_panel(self, func):
        self.clear_panel()
        # Hiển thị chữ đang tải để biết app không bị treo
        tk.Label(self.main_frame, text="⏳ Đang tải dữ liệu...", 
                 bg=COL_BG2, fg=COL_MUTED, font=FONT_H2).pack(pady=50)
        func()

    def clear_panel(self):
        try:
            if not self.main_frame.winfo_exists(): return
            for w in self.main_frame.winfo_children():
                w.destroy()
        except:
            pass

    # =============== 1. QUẢN LÝ NGƯỜI DÙNG ===============
    def req_users(self):
        self.master.client.send({"type": "ADMIN_GET_USERS"})

    def _on_user_list(self, msg):
        try:
            if not self.winfo_exists(): return
            self.clear_panel() # Xóa chữ "Đang tải..."
            
            users = msg.get("users", [])
            self.current_user_data = users

            tk.Label(self.main_frame, text="👥 Danh sách người dùng",
                    bg=COL_BG2, fg=COL_ACCENT, font=FONT_H2).pack(pady=20)
            
            card = tk.Frame(self.main_frame, bg=COL_CARD)
            card.pack(padx=40, pady=10, fill="both", expand=True)

            self.lst_users = tk.Listbox(card, bg="#1f3047", fg=COL_TEXT, font=FONT_SUB,
                                        selectbackground=COL_ACCENT, selectforeground="#0b132b",
                                        borderwidth=0, highlightthickness=0)
            self.lst_users.pack(padx=20, pady=20, fill="both", expand=True)

            if not users:
                self.lst_users.insert("end", "(Chưa có người dùng nào)")
            
            for u in users:
                status = u.get("TrangThai", "Active")
                line = f"{u['TenDangNhap']}  -  [{status}]  -  Thắng: {u.get('SoTranThang',0)}"
                self.lst_users.insert("end", line)

            btns = tk.Frame(self.main_frame, bg=COL_BG2)
            btns.pack(pady=10)
            tk.Button(btns, text="🔒 Khóa / Mở khóa", bg="#ff9f1c", fg="#0b132b",
                    relief="flat", command=self._toggle_lock).pack(side="left", padx=5)
            tk.Button(btns, text="❌ Xóa tài khoản", bg="#ff595e", fg="white",
                    relief="flat", command=self._delete_user).pack(side="left", padx=5)
        except Exception as e:
            print("Lỗi vẽ User:", e)

    def _get_selected_user(self):
        try:
            if not self.lst_users.curselection():
                messagebox.showwarning("Chú ý", "Vui lòng chọn một người dùng!")
                return None
            idx = self.lst_users.curselection()[0]
            return self.current_user_data[idx]
        except:
            return None

    def _toggle_lock(self):
        u = self._get_selected_user()
        if not u: return
        new_status = "Locked" if u.get("TrangThai", "Active") == "Active" else "Active"
        self.master.client.send({"type": "ADMIN_LOCK_USER", "username": u["TenDangNhap"], "status": new_status})

    def _delete_user(self):
        u = self._get_selected_user()
        if not u: return
        if messagebox.askyesno("Xác nhận", f"Xóa vĩnh viễn user {u['TenDangNhap']}?"):
            self.master.client.send({"type": "ADMIN_DELETE_USER", "username": u["TenDangNhap"]})

    # =============== 2. QUẢN LÝ PHÒNG ===============
    def req_rooms(self):
        self.master.client.send({"type": "ADMIN_GET_ROOMS"})

    def _on_room_list(self, msg):
        try:
            if not self.winfo_exists(): return
            self.clear_panel()
            rooms = msg.get("rooms", [])
            self.current_room_data = rooms

            tk.Label(self.main_frame, text="🏠 Quản lý phòng đang hoạt động",
                    bg=COL_BG2, fg=COL_ACCENT, font=FONT_H2).pack(pady=20)
            
            card = tk.Frame(self.main_frame, bg=COL_CARD)
            card.pack(padx=40, pady=10, fill="both", expand=True)

            self.lst_rooms = tk.Listbox(card, bg="#1f3047", fg=COL_TEXT, font=FONT_SUB,
                                        selectbackground=COL_ACCENT, selectforeground="#0b132b",
                                        borderwidth=0, highlightthickness=0)
            self.lst_rooms.pack(padx=20, pady=20, fill="both", expand=True)

            if not rooms:
                self.lst_rooms.insert("end", "(Không có phòng nào)")

            for r in rooms:
                line = f"Phòng {r['id']} ({len(r['players'])}/2) - {r['status']}"
                self.lst_rooms.insert("end", line)

            tk.Button(self.main_frame, text="⚠️ Giải tán phòng", bg="#ff595e", fg="white",
                    relief="flat", command=self._kill_room).pack(pady=10)
        except Exception as e:
            print("Lỗi vẽ Room:", e)

    def _kill_room(self):
        try:
            if not self.lst_rooms.curselection(): return
            idx = self.lst_rooms.curselection()[0]
            r = self.current_room_data[idx]
            if messagebox.askyesno("Xác nhận", f"Hủy phòng {r['id']}?"):
                self.master.client.send({"type": "ADMIN_KILL_ROOM", "room_id": r['id']})
        except: pass


    # =============== 3. LỊCH SỬ ĐẤU ===============
    def req_history(self):
        self.master.client.send({"type": "ADMIN_GET_HISTORY"})

    def _on_history_list(self, msg):
        try:
            if not self.winfo_exists(): return
            self.clear_panel()
            
            self.history_data = msg.get("history", []) # Lưu lại dữ liệu để dùng khi click

            tk.Label(self.main_frame, text="📜 Lịch sử trận đấu",
                    bg=COL_BG2, fg=COL_ACCENT, font=FONT_H2).pack(pady=20)
            
            card = tk.Frame(self.main_frame, bg=COL_CARD)
            card.pack(padx=40, pady=10, fill="both", expand=True)

            # Scrollbar cho danh sách nếu quá dài
            scrollbar = tk.Scrollbar(card)
            scrollbar.pack(side="right", fill="y")

            self.lst_history = tk.Listbox(card, bg="#1f3047", fg=COL_TEXT, font=FONT_SUB,
                            selectbackground=COL_ACCENT, selectforeground="#0b132b",
                            borderwidth=0, highlightthickness=0, yscrollcommand=scrollbar.set)
            self.lst_history.pack(padx=20, pady=20, fill="both", expand=True)
            scrollbar.config(command=self.lst_history.yview)

            # Bind sự kiện Double Click
            self.lst_history.bind('<Double-1>', self._show_history_detail)

            if not self.history_data:
                self.lst_history.insert("end", "(Chưa có lịch sử đấu)")
            else:
                for h in self.history_data:
                    # h chứa: P1, P2, Winner, NgayGioKetThuc, SoLuotBan_NC1...
                    t = str(h.get('NgayGioKetThuc'))
                    p1 = h.get('P1')
                    p2 = h.get('P2')
                    winner = h.get('Winner')
                    line = f"🕒 {t} | ⚔️ {p1} vs {p2} | 🏆 Thắng: {winner}"
                    self.lst_history.insert("end", line)

            tk.Button(self.main_frame, text="🔍 Xem chi tiết", bg=COL_BTN, fg=COL_BTN_TEXT,
                    relief="flat", command=lambda: self._show_history_detail(None)).pack(pady=10)

        except Exception as e:
            print("Lỗi vẽ History:", e)

    def _show_history_detail(self, event):
        """Hiển thị Popup thông số chi tiết của trận đấu (Chỉ hiện 1 cái)"""
        try:
            if not self.lst_history.curselection():
                return
            idx = self.lst_history.curselection()[0]
            data = self.history_data[idx]

            # === [LOGIC MỚI] ĐÓNG CỬA SỔ CŨ NẾU CÓ ===
            if self.detail_window is not None:
                try:
                    if self.detail_window.winfo_exists():
                        self.detail_window.destroy()
                except:
                    pass
            # =========================================

            # Tạo cửa sổ Popup mới
            top = tk.Toplevel(self)
            self.detail_window = top  # <--- Lưu lại tham chiếu vào biến
            
            top.title("Chi tiết trận đấu")
            top.geometry("400x450")
            top.configure(bg=COL_BG2)

            # --- Phần vẽ giao diện giữ nguyên như cũ ---
            tk.Label(top, text="📊 THỐNG KÊ TRẬN ĐẤU", bg=COL_BG2, fg=COL_ACCENT, font=FONT_H2).pack(pady=15)

            info_frame = tk.Frame(top, bg=COL_CARD, padx=20, pady=20)
            info_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

            def add_row(label, value, color=COL_TEXT):
                row = tk.Frame(info_frame, bg=COL_CARD)
                row.pack(fill="x", pady=2)
                tk.Label(row, text=label, bg=COL_CARD, fg=COL_MUTED, width=20, anchor="w").pack(side="left")
                tk.Label(row, text=value, bg=COL_CARD, fg=color, anchor="w", font=("Arial", 10, "bold")).pack(side="left")

            p1 = data.get('P1')
            p2 = data.get('P2')
            winner = data.get('Winner')
            
            add_row("Thời gian:", str(data.get('NgayGioKetThuc')))
            add_row("Người chơi 1:", p1)
            add_row("Người chơi 2:", p2)
            add_row("🏆 Người thắng:", winner, color="#ff9f1c")

            tk.Frame(info_frame, bg=COL_MUTED, height=1).pack(fill="x", pady=10)
            
            tk.Label(info_frame, text=f"Thống kê của {p1}:", bg=COL_CARD, fg=COL_ACCENT).pack(anchor="w", pady=(5,0))
            shots1 = data.get('SoLuotBan_NC1', 0)
            hits1 = data.get('SoLuotTrung_NC1', 0)
            acc1 = round((hits1/shots1 * 100), 1) if shots1 > 0 else 0
            add_row("   • Số phát bắn:", f"{shots1}")
            add_row("   • Độ chính xác:", f"{acc1}% ({hits1} trúng)")

            tk.Label(info_frame, text=f"Thống kê của {p2}:", bg=COL_CARD, fg=COL_ACCENT).pack(anchor="w", pady=(10,0))
            shots2 = data.get('SoLuotBan_NC2', 0)
            hits2 = data.get('SoLuotTrung_NC2', 0)
            acc2 = round((hits2/shots2 * 100), 1) if shots2 > 0 else 0
            add_row("   • Số phát bắn:", f"{shots2}")
            add_row("   • Độ chính xác:", f"{acc2}% ({hits2} trúng)")

            tk.Button(top, text="Đóng", bg=COL_BTN, fg=COL_BTN_TEXT, relief="flat", command=top.destroy).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xem chi tiết: {e}")