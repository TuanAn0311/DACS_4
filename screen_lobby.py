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
        self.logout_func = logout

        # --- HEADER ---
        tk.Label(self.bg, text=f"⚓ Sảnh — Xin chào, {username}",
                 bg=COL_BG2, fg=COL_ACCENT, font=FONT_H1).place(relx=0.5, rely=0.08, anchor="center")

        # --- KHUNG CHỨA DANH SÁCH PHÒNG ---
        self.area = tk.Frame(self.bg, bg=COL_BG2)
        self.area.place(relx=0.5, rely=0.55, anchor="center")

        # --- CÁC NÚT CHỨC NĂNG (Gom nhóm cho gọn) ---
        btn_frame = tk.Frame(self.bg, bg=COL_BG2)
        btn_frame.place(relx=0.5, rely=0.18, anchor="center")

        tk.Button(btn_frame, text="Tạo phòng", bg=COL_ACCENT, fg="#0b132b", relief="flat",
                  width=15, command=self._create_room).pack(side="left", padx=5)

        tk.Button(btn_frame, text="🔄 Làm mới", bg=COL_BTN, fg=COL_BTN_TEXT, relief="flat",
                  width=12, command=self.refresh_rooms).pack(side="left", padx=5)

        tk.Button(btn_frame, text="👤 Cá nhân", bg="#4cc9f0", fg="#0b132b", relief="flat",
                  width=12, command=self._req_profile).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="📜 Lịch sử", bg="#4cc9f0", fg="#0b132b", relief="flat",
                  width=12, command=self._req_history).pack(side="left", padx=5)


        # --- FOOTER ---
        if getattr(self.master, "is_admin", False) == True:
            tk.Button(self.bg, text="Trang Admin", bg=COL_BTN, fg=COL_BTN_TEXT,
                      relief="flat", command=go_admin).place(relx=0.35, rely=0.92, anchor="center", width=140, height=36)

        tk.Button(self.bg, text="Đăng xuất", bg=COL_BTN, fg=COL_BTN_TEXT,
                  relief="flat", command=logout).place(relx=0.65, rely=0.92, anchor="center", width=140, height=36)

        # --- SOCKET LISTENERS ---
        c = master.client
        c.on("ROOM_LIST", self._on_rooms)
        c.on("JOINED_ROOM", self._joined_room)
        c.on("WELCOME", self._welcome)
        c.on("ERROR", self._show_error)
        
        # Listeners mới cho Profile & History
        c.on("PROFILE_DATA", self._show_profile_popup)
        c.on("PROFILE_UPDATE_OK", self._on_update_success)
        c.on("DELETE_OK", self._on_delete_ok)
        c.on("MY_HISTORY_DATA", self._show_history_popup)

        # Lấy danh sách phòng lần đầu
        c.send({"type": "GET_ROOMS"})
        self._auto_refresh()

    # ================= REALTIME =================
    def _auto_refresh(self):
        try:
            if self.winfo_exists():
                self.master.client.send({"type": "GET_ROOMS"})
                self.after(2000, self._auto_refresh) # 2 giây refresh 1 lần
        except: pass

    # ================= EVENTS CƠ BẢN =================
    def _welcome(self, msg): self.username = msg["username"]
    def refresh_rooms(self): self.master.client.send({"type": "GET_ROOMS"})
    def _create_room(self): self.master.client.send({"type": "CREATE_ROOM"})
    def _show_error(self, msg): messagebox.showwarning("Thông báo", msg["msg"])
    def _joined_room(self, msg): self.go_battle(msg["room"])
    def _join(self, room): self.master.client.send({"type": "JOIN_ROOM", "room": room})

    def _on_rooms(self, msg):
        try:
            if not self.winfo_exists() or not self.area.winfo_exists(): return
        except: return
        for w in self.area.winfo_children(): w.destroy()
        
        rooms = msg["rooms"]
        if not rooms:
            tk.Label(self.area, text="(Chưa có phòng)", bg=COL_BG2, fg=COL_MUTED).pack()
            return
        
        # Vẽ lưới phòng (3 cột)
        for i, r in enumerate(rooms):
            box = tk.Frame(self.area, width=230, height=140, bg=COL_CARD)
            box.grid(row=i//3, column=i%3, padx=16, pady=16)
            tk.Label(box, text=f"Phòng {r['id']}", fg=COL_TEXT, bg=COL_CARD, font=FONT_H2).pack(pady=(8, 2))
            tk.Label(box, text=f"👑 Chủ: {r['owner']}", fg=COL_MUTED, bg=COL_CARD).pack()
            tk.Label(box, text=f"👤 {r['players']}/2", fg=COL_MUTED, bg=COL_CARD).pack()
            
            state = "disabled" if r["players"] >= 2 else "normal"
            text = "Phòng đầy" if r["players"] >= 2 else "Tham gia"
            color = "gray" if r["players"] >= 2 else COL_ACCENT
            
            tk.Button(box, text=text, bg=color, fg="#0b132b", relief="flat", state=state,
                      command=lambda rid=r['id']: self._join(rid)).pack(pady=8)

    # ================= 1. XỬ LÝ THÔNG TIN CÁ NHÂN =================
    def _req_profile(self):
        self.master.client.send({"type": "GET_PROFILE"})

    # [Trong file screen_lobby.py -> thay thế hàm _show_profile_popup]

    # [Trong file screen_lobby.py]

    # [Trong file screen_lobby.py]

    def _show_profile_popup(self, msg):
        data = msg["data"]
        
        # --- CẤU HÌNH UI ---
        BG_POPUP = COL_BG2
        BG_SECTION = COL_CARD
        TXT_LABEL = COL_MUTED
        TXT_VAL = COL_TEXT
        ACCENT = COL_ACCENT

        top = tk.Toplevel(self)
        top.title("Hồ sơ người chơi")
        top.geometry("420x680") 
        top.configure(bg=BG_POPUP)

        tk.Label(top, text="HỒ SƠ NGƯỜI CHƠI", bg=BG_POPUP, fg=ACCENT, font=FONT_H1).pack(pady=(20, 10))

        # ==========================================================
        # PHẦN 1: CÀI ĐẶT TÀI KHOẢN
        # ==========================================================
        frame_edit = tk.Frame(top, bg=BG_SECTION, padx=20, pady=15)
        frame_edit.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_edit, text="THÔNG TIN TÀI KHOẢN", bg=BG_SECTION, fg=ACCENT, 
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 10))

        def add_input(label, value, is_pass=False):
            tk.Label(frame_edit, text=label, bg=BG_SECTION, fg=TXT_LABEL, 
                     font=("Arial", 9), anchor="w").pack(fill="x", pady=(5, 0))
            
            e = tk.Entry(frame_edit, bg=BG_SECTION, fg=TXT_VAL, 
                         font=("Arial", 11), relief="flat", insertbackground="white",
                         show="•" if is_pass else "")
            if value: e.insert(0, str(value))
            e.pack(fill="x", pady=(2, 0))
            
            tk.Frame(frame_edit, bg=TXT_LABEL, height=1).pack(fill="x", pady=(0, 5))
            return e

        # 1. Tên hiển thị
        ent_user = add_input("Tên hiển thị:", data['TenDangNhap'])
        
        # 2. Email
        ent_email = add_input("Email:", data.get('Email') or "")
        
        # 3. Mật khẩu (Có chức năng Ẩn/Hiện)
        ent_pw = add_input("Mật khẩu mới (Để trống nếu không đổi):", "", is_pass=True)

        # --- Checkbox Hiện mật khẩu ---
        def toggle_password():
            if var_show_pass.get():
                ent_pw.config(show="") # Hiển thị text thường
            else:
                ent_pw.config(show="•") # Hiển thị dấu chấm

        var_show_pass = tk.BooleanVar()
        chk = tk.Checkbutton(frame_edit, text="Hiện mật khẩu", variable=var_show_pass, 
                             command=toggle_password,
                             bg=BG_SECTION, fg=TXT_LABEL, selectcolor=BG_SECTION,
                             activebackground=BG_SECTION, activeforeground=TXT_VAL,
                             font=("Arial", 9), relief="flat", highlightthickness=0)
        chk.pack(anchor="w", pady=(0, 5))

        # ==========================================================
        # PHẦN 2: THỐNG KÊ (Giữ nguyên như cũ)
        # ==========================================================
        frame_stats = tk.Frame(top, bg=BG_SECTION, padx=20, pady=15)
        frame_stats.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_stats, text="THỐNG KÊ CHIẾN TÍCH", bg=BG_SECTION, fg=ACCENT, 
                 font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 15))

        stats_grid = tk.Frame(frame_stats, bg=BG_SECTION)
        stats_grid.pack(fill="x")

        f_win = tk.Frame(stats_grid, bg=BG_SECTION)
        f_win.pack(side="left", expand=True, fill="x")
        tk.Label(f_win, text="TRẬN THẮNG", bg=BG_SECTION, fg=TXT_LABEL, font=("Arial", 8)).pack()
        tk.Label(f_win, text=str(data['SoTranThang']), bg=BG_SECTION, fg="#00ff88", font=("Arial", 24, "bold")).pack()

        tk.Frame(stats_grid, bg=TXT_LABEL, width=1, height=40).pack(side="left", padx=10)

        f_lose = tk.Frame(stats_grid, bg=BG_SECTION)
        f_lose.pack(side="left", expand=True, fill="x")
        tk.Label(f_lose, text="TRẬN THUA", bg=BG_SECTION, fg=TXT_LABEL, font=("Arial", 8)).pack()
        tk.Label(f_lose, text=str(data['SoTranThua']), bg=BG_SECTION, fg="#ff595e", font=("Arial", 24, "bold")).pack()

        tk.Frame(frame_stats, bg=TXT_LABEL, height=1).pack(fill="x", pady=15)

        def add_info_row(lbl, val):
            row = tk.Frame(frame_stats, bg=BG_SECTION)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=lbl, bg=BG_SECTION, fg=TXT_LABEL, width=18, anchor="w").pack(side="left")
            tk.Label(row, text=val, bg=BG_SECTION, fg=TXT_VAL, anchor="w").pack(side="left")

        add_info_row("Ngày tham gia:", str(data['NgayTao']))
        add_info_row("Cập nhật lần cuối:", str(data.get('NgayCapNhat', 'N/A')))

        # ==========================================================
        # PHẦN 3: NÚT BẤM
        # ==========================================================
        btn_frame = tk.Frame(top, bg=BG_POPUP)
        btn_frame.pack(side="bottom", pady=20)

        tk.Button(btn_frame, text="💾 LƯU THAY ĐỔI", bg=ACCENT, fg="#0b132b", 
                  relief="flat", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2",
                  command=lambda: self._do_update(ent_user.get(), ent_email.get(), ent_pw.get())
                  ).pack(side="left", padx=10)

        tk.Button(btn_frame, text="❌ XÓA TÀI KHOẢN", bg="#ff595e", fg="white", 
                  relief="flat", font=("Arial", 10, "bold"), padx=15, pady=5, cursor="hand2",
                  command=lambda: self._req_delete(top)
                  ).pack(side="left", padx=10)

    def _do_update(self, new_user, email, pw):
        # Gửi thêm new_username lên server
        self.master.client.send({
            "type": "UPDATE_PROFILE",
            "new_username": new_user,
            "email": email,
            "password": pw
        })
        
    def _on_update_success(self, msg):
        # 1. Hiển thị thông báo thành công
        messagebox.showinfo("Thành công", msg["msg"])
        
        # 2. (Tùy chọn) Tự động tắt cửa sổ hồ sơ cũ và mở lại cái mới 
        # để cập nhật ngay lập tức "Ngày cập nhật" và "Tên hiển thị" mới
        
        # Tìm và đóng cửa sổ popup hiện tại (nếu đang mở)
        # Lưu ý: Cách này hoạt động tốt nếu bạn chỉ mở 1 popup hồ sơ tại 1 thời điểm
        for widget in self.winfo_children():
            if isinstance(widget, tk.Toplevel) and widget.title() == "Hồ sơ người chơi":
                widget.destroy()
        
        # Tải lại hồ sơ mới
        self._req_profile()

    def _req_delete(self, parent):
        if messagebox.askyesno("Cảnh báo nguy hiểm", "Bạn có chắc chắn muốn xóa tài khoản?\nHành động này KHÔNG THỂ hoàn tác!"):
            self.master.client.send({"type": "DELETE_SELF"})
            parent.destroy()

    def _on_delete_ok(self, msg):
        messagebox.showinfo("Thông báo", msg["msg"])
        self.logout_func() # Tự động đăng xuất

    # ================= 2. XỬ LÝ LỊCH SỬ CÁ NHÂN =================
    def _req_history(self):
        self.master.client.send({"type": "GET_MY_HISTORY"})

    def _show_history_popup(self, msg):
        hist = msg.get("history", [])
        
        top = tk.Toplevel(self)
        top.title(f"Lịch sử đấu của {self.username}")
        top.geometry("420x450")
        top.configure(bg=COL_BG2)

        tk.Label(top, text="📜 LỊCH SỬ ĐẤU", bg=COL_BG2, fg=COL_ACCENT, font=FONT_H2).pack(pady=10)

        card = tk.Frame(top, bg=COL_CARD)
        card.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(card)
        scrollbar.pack(side="right", fill="y")
        
        lst = tk.Listbox(card, bg="#1f3047", fg=COL_TEXT, font=FONT_SUB,
                         selectbackground=COL_ACCENT, selectforeground="#0b132b",
                         borderwidth=0, highlightthickness=0, yscrollcommand=scrollbar.set)
        lst.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=lst.yview)

        if not hist:
            lst.insert("end", "(Bạn chưa chơi trận nào)")
        else:
            for h in hist:
                # Format: [TG] Đối thủ: UserB -> Thắng/Thua
                time_str = str(h['NgayGioKetThuc'])
                
                # Xác định đối thủ
                if h['P1'] == self.username:
                    enemy = h['P2']
                else:
                    enemy = h['P1']
                
                result = "THẮNG" if h['Winner'] == self.username else "THUA"
                line = f"[{time_str}] vs {enemy} -> {result}"
                lst.insert("end", line)

        tk.Button(top, text="Đóng", bg=COL_BTN, fg=COL_BTN_TEXT, relief="flat", command=top.destroy).pack(pady=10)