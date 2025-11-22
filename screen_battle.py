import tkinter as tk
from base_screen import BaseScreen
from widgets import Board
from theme import *


class BattleScreen(BaseScreen):
    def __init__(self, master, username, back_lobby, show_result, room_id):
        super().__init__(master)

        self.master = master
        self.room_id = room_id
        self.username = username
        self.turn = False
        self.enemy_name = None
        self.phase = "waiting"
        self.players = []
        self.ready = [False, False]

        self.show_result = show_result

        self.total_shots = 0
        self.total_hits = 0
        self.total_misses = 0

        tk.Label(self.bg, text="🚢 BATTLE",
                 bg=COL_BG2, fg=COL_ACCENT,
                 font=FONT_H1).place(relx=0.5, rely=0.07, anchor="center")

        info = tk.Frame(self.bg, bg=COL_BG2)
        info.place(relx=0.5, rely=0.16, anchor="center")

        self.lbl_me = tk.Label(
            info,
            text=f"Bạn: {self.username} [Đang chờ đối thủ...]",
            bg=COL_BG2,
            fg=COL_TEXT,
            font=FONT_SUB
        )
        self.lbl_me.grid(row=0, column=0, padx=8)

        self.lbl_enemy = tk.Label(
            info,
            text="Đối thủ: (đang chờ...)",
            bg=COL_BG2,
            fg=COL_MUTED,
            font=FONT_SUB
        )
        self.lbl_enemy.grid(row=0, column=1, padx=8)

        self.ready_btn = tk.Button(
            info, text="✅ Sẵn sàng",
            bg=COL_ACCENT, fg="#0b132b",
            relief="flat",
            command=self._send_ready
        )
        self.ready_btn.grid(row=0, column=2, padx=8)

        self.start_btn = tk.Button(
            info, text="🚀 Bắt đầu",
            bg=COL_BTN, fg=COL_BTN_TEXT,
            relief="flat",
            state="disabled",
            command=self._click_start
        )
        self.start_btn.grid(row=0, column=3, padx=8)

        main = tk.Frame(self.bg, bg=COL_BG2)
        main.place(relx=0.5, rely=0.55, anchor="center")
        self.main = main

        self.my_board = Board(main, title="Bàn của bạn", show_ships=True)
        self.my_board.grid(row=0, column=0, padx=12)

        self.enemy_board = Board(
            main,
            title="Bàn đối thủ",
            show_ships=False,
            on_click=self._shoot
        )
        self.enemy_board.grid(row=0, column=1, padx=12)

        # Ẩn bàn địch cho tới khi bắt đầu bắn
        self.enemy_board.grid_remove()

        chat = tk.Frame(main, bg=COL_CARD)
        chat.grid(row=0, column=2, padx=12)

        tk.Label(chat, text="💬 Chat", bg=COL_CARD, fg=COL_TEXT,
                 font=FONT_H2).pack(anchor="w", padx=8, pady=4)

        self.chat_box = tk.Text(
            chat,
            width=30,
            height=20,
            bg="#1f3047",
            fg=COL_TEXT,
            relief="flat"
        )
        self.chat_box.pack(padx=4, pady=4)

        entry = tk.Frame(chat, bg=COL_CARD)
        entry.pack(fill="x")

        self.chat_entry = tk.Entry(
            entry,
            bg="#314863",
            fg=COL_TEXT
        )
        self.chat_entry.pack(side="left", fill="x", expand=True)

        tk.Button(
            entry,
            text="Gửi",
            bg=COL_ACCENT,
            fg="#0b132b",
            relief="flat",
            command=self._send_chat
        ).pack(side="left", padx=4)

        tk.Button(
            self.bg,
            text="← Về sảnh",
            bg=COL_BTN,
            fg=COL_BTN_TEXT,
            relief="flat",
            command=back_lobby
        ).place(
            relx=0.5,
            rely=0.92,
            anchor="center",
            width=160,
            height=36
        )

        # ====== Đăng ký nhận sự kiện từ server ======
        c = master.client
        c.on("CHAT", self._on_chat)
        c.on("TURN", self._on_turn)
        c.on("SHOT_RESULT", self._on_shot)
        c.on("START", self._start_game)
        c.on("READY_STATE", self._on_ready_state)
        c.on("PLACE_PHASE", self._on_place_phase)
        c.on("GAME_START", self._on_game_start)
        c.on("GAME_OVER", self._on_game_over)
        c.on("ERROR", self._on_error)
        c.on("NAME_UPDATE", self._on_name_update)
        c.on("ROOM_STATE", self._on_room_state)   # trạng thái phòng hiện tại
        c.on("SHIP_SUNK", self._on_ship_sunk)     # 🔥 tàu bị hạ

        self.chat_box.insert("end", "⏳ Đang chờ người chơi khác...\n")
        self.chat_box.see("end")

        # Vừa vào Battle thì xin server gửi trạng thái phòng hiện tại
        self.master.client.send({"type": "GET_ROOM_STATE"})

    # ========================= ROOM STATE (vừa vào phòng) =========================
    def _on_room_state(self, msg):
        """Cập nhật tên + trạng thái ngay khi mở màn Battle."""
        players = msg.get("players", [])
        ready = msg.get("ready", [])
        stage = msg.get("stage", "waiting")

        self.phase = stage
        self.players = players

        if not players:
            # chưa có ai (trường hợp hiếm)
            return

        if len(players) == 1:
            # Chỉ có mình trong phòng
            if self.username == players[0]:
                self.lbl_me.config(
                    text=f"Bạn: {players[0]} [Đang chờ đối thủ...]"
                )
                self.lbl_enemy.config(text="Đối thủ: (đang chờ...)")
            else:
                # lý thuyết không xảy ra, nhưng cứ xử lý cho chắc
                self.lbl_me.config(
                    text=f"Bạn: {self.username} [Đang chờ đối thủ...]"
                )
                self.lbl_enemy.config(
                    text=f"Đối thủ: {players[0]} [Chưa sẵn sàng]"
                )
            return

        # Có 2 người trong phòng
        if self.username == players[0]:
            me_idx = 0
            enemy_idx = 1
        else:
            me_idx = 1
            enemy_idx = 0

        me = players[me_idx]
        enemy = players[enemy_idx]
        self.enemy_name = enemy

        r_me = ready[me_idx] if me_idx < len(ready) else False
        r_enemy = ready[enemy_idx] if enemy_idx < len(ready) else False

        self.lbl_me.config(
            text=f"Bạn: {me} [{'Sẵn sàng' if r_me else 'Chưa sẵn sàng'}]"
        )
        self.lbl_enemy.config(
            text=f"Đối thủ: {enemy} [{'Sẵn sàng' if r_enemy else 'Chưa sẵn sàng'}]"
        )

    # ========================= NAME UPDATE (join/leave realtime) =========================
    def _on_name_update(self, msg):
        names = msg.get("players", [])

        if len(names) == 1:
            self.lbl_me.config(text=f"Bạn: {names[0]} [Đang chờ đối thủ...]")
            self.lbl_enemy.config(text="Đối thủ: (đang chờ...)")

        if len(names) == 2:
            if self.username == names[0]:
                me = names[0]
                enemy = names[1]
            else:
                me = names[1]
                enemy = names[0]

            self.enemy_name = enemy

            self.lbl_me.config(text=f"Bạn: {me} [Chưa sẵn sàng]")
            self.lbl_enemy.config(text=f"Đối thủ: {enemy} [Chưa sẵn sàng]")

    # ========================= GAME STATES =========================
    def _start_game(self, msg):
        players = msg.get("players", [])
        ready = msg.get("ready", [])

        self.chat_box.delete("1.0", "end")

        self.players = players

        if len(players) != 2:
            return

        if self.username == players[0]:
            me = players[0]
            enemy = players[1]
            idx_me = 0
        else:
            me = players[1]
            enemy = players[0]
            idx_me = 1

        self.enemy_name = enemy

        r_me = ready[idx_me] if idx_me < len(ready) else False
        r_enemy = ready[1 - idx_me] if len(ready) == 2 else False

        self.lbl_me.config(
            text=f"Bạn: {me} [{'Sẵn sàng' if r_me else 'Chưa sẵn sàng'}]"
        )
        self.lbl_enemy.config(
            text=f"Đối thủ: {enemy} [{'Sẵn sàng' if r_enemy else 'Chưa sẵn sàng'}]"
        )

        self.chat_box.insert("end", f"🎮 Bạn: {me}\n")
        self.chat_box.insert("end", f"🎮 Đối thủ: {enemy}\n")
        self.chat_box.see("end")

    def _on_ready_state(self, msg):
        players = msg["players"]
        ready = msg["ready"]

        if self.username not in players or len(players) != 2:
            return

        idx_me = players.index(self.username)
        idx_enemy = 1 - idx_me

        self.lbl_me.config(
            text=f"Bạn: {players[idx_me]} [{'Sẵn sàng' if ready[idx_me] else 'Chưa sẵn sàng'}]"
        )
        self.lbl_enemy.config(
            text=f"Đối thủ: {players[idx_enemy]} [{'Sẵn sàng' if ready[idx_enemy] else 'Chưa sẵn sàng'}]"
        )

        if ready[idx_me]:
            self.ready_btn.config(state="disabled")

    def _on_place_phase(self, msg):
        self.phase = "placing"

        self.enemy_board.grid_remove()
        self.my_board.start_placement([5, 4, 3, 2])

        self.start_btn.config(state="normal")

        self.chat_box.insert("end", "🛠 Giai đoạn đặt tàu...\n")
        self.chat_box.see("end")

    def _on_game_start(self, msg):
        self.phase = "playing"

        self.enemy_board.grid(row=0, column=1, padx=12)

        self.chat_box.insert("end", "🎯 Trận đấu bắt đầu!\n")
        self.chat_box.see("end")

    def _on_game_over(self, msg):
        winner = msg.get("winner", "???")

        self.chat_box.insert("end", f"🏁 Người thắng: {winner}\n")
        self.chat_box.see("end")

        self.after(1500, lambda: self.show_result(
            winner,
            self.total_shots,
            self.total_hits,
            self.total_misses
        ))

    # ========================= CHAT =========================
    def _on_chat(self, msg):
        self.chat_box.insert("end", msg["msg"] + "\n")
        self.chat_box.see("end")

    def _send_chat(self):
        content = self.chat_entry.get().strip()
        if content:
            self.master.client.send({
                "type": "CHAT",
                "msg": content
            })
            self.chat_entry.delete(0, "end")

    # ========================= READY / START =========================
    def _send_ready(self):
        self.master.client.send({"type": "READY"})
        self.ready_btn.config(state="disabled")

    def _click_start(self):
        if self.phase != "placing":
            return

        if not self.my_board.all_ships_placed():
            self.chat_box.insert("end", "⚠ Chưa đặt hết tàu!\n")
            self.chat_box.see("end")
            return

        self.master.client.send({
            "type": "PLACE_DONE",
            "ships": self.my_board.get_ships()
        })

        self.start_btn.config(state="disabled")

    # ========================= TURN =========================
    def _on_turn(self, msg):
        self.turn = msg["your_turn"]

        if self.turn:
            self.chat_box.insert("end", "👉 Tới lượt bạn!\n")
        else:
            self.chat_box.insert("end", f"⏳ Chờ {self.enemy_name}...\n")

        self.chat_box.see("end")

    # ========================= SHOOT =========================
    def _shoot(self, r, c):
        if self.phase != "playing":
            self.chat_box.insert("end", "⚠ Chưa tới giai đoạn bắn.\n")
        elif not self.turn:
            self.chat_box.insert("end", "⚠ Không phải lượt bạn!\n")
        else:
            self.master.client.send({
                "type": "SHOOT",
                "r": r,
                "c": c
            })
        self.chat_box.see("end")

    def _on_shot(self, msg):
        r, c = msg["r"], msg["c"]
        hit = msg["hit"]
        by = msg["by"]
        target = msg.get("target")

        # Phát bắn của mình → vẽ lên bàn địch
        if by == self.username:
            self.enemy_board.mark(r, c, hit)
            self.total_shots += 1
            if hit:
                self.total_hits += 1
            else:
                self.total_misses += 1

        # Phát bắn nhắm vào mình → vẽ lên bàn mình
        elif target == self.username:
            self.my_board.mark(r, c, hit)

        self.chat_box.insert(
            "end",
            f"{by} bắn ({r},{c}) → {'TRÚNG' if hit else 'TRƯỢT'}\n"
        )
        self.chat_box.see("end")

    # ========================= ERROR =========================
    def _on_error(self, msg):
        self.chat_box.insert("end", f"⚠ {msg.get('msg', '')}\n")
        self.chat_box.see("end")

    # ========================= SHIP SUNK =========================
    def _on_ship_sunk(self, msg):
        """Thông báo khi 1 tàu bị phá hủy hoàn toàn."""
        by = msg.get("by")
        owner = msg.get("owner")
        length = msg.get("length")

        if by == self.username:
            # Mình bắn chìm tàu của đối thủ
            self.chat_box.insert(
                "end",
                f"🔥 Bạn đã phá hủy tàu dài {length} ô của {owner}!\n"
            )
        elif owner == self.username:
            # Tàu của mình bị phá
            self.chat_box.insert(
                "end",
                f"☠ Một tàu dài {length} ô của bạn đã bị phá hủy!\n"
            )
        else:
            # TH khác (lý thuyết không có, nhưng để cho chắc)
            self.chat_box.insert(
                "end",
                f"💥 {by} đã phá hủy tàu dài {length} ô của {owner}\n"
            )

        self.chat_box.see("end")
