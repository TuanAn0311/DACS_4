import tkinter as tk
from theme import *


class Board(tk.Frame):
    def __init__(self, master, title="", show_ships=False, on_click=None):
        super().__init__(master, bg=COL_BG2)
        self.on_click = on_click

        tk.Label(self, text=title, bg=COL_BG2, fg=COL_TEXT, font=FONT_H2).pack()
        self.canvas = tk.Canvas(self, width=GRID_N * CELL + 2, height=GRID_N * CELL + 2,
                                bg="#10263f", highlightthickness=0)
        self.canvas.pack(pady=6)

        # Ma trận trạng thái để đánh dấu trúng/trượt
        self.state = [[0] * GRID_N for _ in range(GRID_N)]

        # Trạng thái đặt tàu
        self.mode = "normal"        # 'normal' / 'placing'
        # mỗi ship: {'length', 'orientation', 'placed', 'cells', 'tag', 'button'}
        self.ship_defs = []
        self.selected_ship = None

        self.info = tk.Label(self, text="", bg=COL_BG2, fg=COL_MUTED, font=FONT_SUB)
        self.info.pack()

        # Dock hiển thị các tàu để chọn
        self.dock_frame = tk.Frame(self, bg=COL_BG2)
        self.dock_frame.pack(pady=4)

        self._draw_grid()

        # Bắt sự kiện click trên bàn
        self.canvas.bind("<Button-1>", self._on_canvas_click)

    # ----------------- VẼ Ô LƯỚI -----------------
    def _draw_grid(self):
        for i in range(GRID_N):
            for j in range(GRID_N):
                x0, y0 = j * CELL, i * CELL
                x1, y1 = x0 + CELL, y0 + CELL
                self.canvas.create_rectangle(
                    x0, y0, x1, y1,
                    outline="#1f3a56",
                    fill="#0e2236"
                )

    # ----------------- VẼ MỘT TÀU -----------------
    def _draw_ship(self, tag, r1, c1, r2, c2):
        x0, y0 = c1 * CELL, r1 * CELL
        x1, y1 = (c2 + 1) * CELL, (r2 + 1) * CELL
        self.canvas.create_rectangle(
            x0 + 4, y0 + 8, x1 - 4, y1 - 8,
            fill="#9fb3c8",
            outline="",
            tags=tag
        )

        if r1 == r2:
            # Ngang
            self.canvas.create_polygon(
                x1 - 4, (y0 + y1) // 2,
                x1 + 10, y0 + 8,
                x1 + 10, y1 - 8,
                fill="#bcd0e0",
                outline="",
                tags=tag
            )
        else:
            # Dọc
            self.canvas.create_polygon(
                (x0 + x1) // 2, y0 - 10,
                x0 + 8, y0 + 4,
                x1 - 8, y0 + 4,
                fill="#bcd0e0",
                outline="",
                tags=tag
            )

    # ----------------- BẮT ĐẦU CHẾ ĐỘ ĐẶT TÀU -----------------
    def start_placement(self, ship_lengths):
        """
        Bắt đầu chế độ đặt tàu.
        Ví dụ: ship_lengths = [5, 4, 3, 2]
        """
        self.mode = "placing"
        self.ship_defs = []
        self.selected_ship = None

        # Xoá dock cũ (nếu có)
        for w in self.dock_frame.winfo_children():
            w.destroy()

        # Tạo danh sách tàu trong dock
        for idx, length in enumerate(ship_lengths):
            tag = f"ship{idx}"
            btn = tk.Button(
                self.dock_frame,
                text=f"Tàu {length} ô",
                bg=COL_BG2,
                fg=COL_TEXT,
                relief="flat",
                font=FONT_SUB,
                command=lambda i=idx: self._select_ship(i)
            )
            btn.pack(side="left", padx=4)

            self.ship_defs.append({
                "length": length,
                "orientation": "H",   # 'H' hoặc 'V'
                "placed": False,
                "cells": [],
                "tag": tag,
                "button": btn
            })

        if self.ship_defs:
            self._select_ship(0)
        else:
            self.info.config(text="Không có tàu để đặt.")

        # Cho phép nhận phím R để xoay
        self.canvas.focus_set()
        self.canvas.bind("<Key-r>", self._on_rotate_key)

    def _select_ship(self, idx):
        """Chọn 1 tàu trong dock để đặt hoặc di chuyển."""
        if idx < 0 or idx >= len(self.ship_defs):
            return
        self.selected_ship = idx

        # Đổi màu nút để biết đang chọn tàu nào
        for i, sh in enumerate(self.ship_defs):
            if i == idx:
                sh["button"].config(bg=COL_ACCENT, fg="#0b132b")
            else:
                sh["button"].config(bg=COL_BG2, fg=COL_TEXT)

        sh = self.ship_defs[idx]
        huong = "ngang" if sh["orientation"] == "H" else "dọc"
        self.info.config(
            text=f"Đang chọn tàu {sh['length']} ô – hướng {huong} (nhấn R để xoay)."
        )

    def _on_rotate_key(self, event):
        """Nhấn phím R để xoay tàu đang chọn."""
        if self.mode != "placing" or self.selected_ship is None:
            return
        sh = self.ship_defs[self.selected_ship]
        sh["orientation"] = "V" if sh["orientation"] == "H" else "H"
        huong = "ngang" if sh["orientation"] == "H" else "dọc"
        self.info.config(
            text=f"Đang chọn tàu {sh['length']} ô – hướng {huong} (nhấn R để xoay)."
        )

    def _on_canvas_click(self, e):
        c = e.x // CELL
        r = e.y // CELL
        if not (0 <= r < GRID_N and 0 <= c < GRID_N):
            return

        if self.mode == "placing":
            self._place_ship_at(r, c)
        else:
            # Chế độ đánh nhau – click để bắn
            if self.on_click:
                self.on_click(r, c)

    def _place_ship_at(self, r, c):
        """Đặt / di chuyển tàu đang chọn vào vị trí (r, c) trên bàn."""
        if self.mode != "placing" or self.selected_ship is None:
            return

        sh = self.ship_defs[self.selected_ship]
        length = sh["length"]
        orientation = sh["orientation"]

        # Tính các ô tàu sẽ chiếm
        cells = []
        for k in range(length):
            rr = r + (k if orientation == "V" else 0)
            cc = c + (k if orientation == "H" else 0)

            if not (0 <= rr < GRID_N and 0 <= cc < GRID_N):
                self.info.config(text="❌ Tàu vượt khỏi bàn. Hãy chọn vị trí khác.")
                return

            cells.append((rr, cc))

        # Gom tất cả ô của các tàu khác để kiểm tra trùng
        other_cells = set()
        for i, other in enumerate(self.ship_defs):
            if i == self.selected_ship:
                continue
            for cell in other["cells"]:
                other_cells.add(cell)

        for cell in cells:
            if cell in other_cells:
                self.info.config(text="❌ Tàu bị chồng lên tàu khác. Hãy chọn vị trí khác.")
                return

        # Xoá hình vẽ tàu cũ (nếu đã vẽ)
        self.canvas.delete(sh["tag"])

        r1 = cells[0][0]
        c1 = cells[0][1]
        r2 = cells[-1][0]
        c2 = cells[-1][1]

        # Vẽ lại tàu tại vị trí mới
        self._draw_ship(sh["tag"], r1, c1, r2, c2)

        sh["cells"] = cells
        sh["placed"] = True
        sh["button"].config(text=f"Tàu {length} ô ✅")

        self.info.config(
            text="✅ Đã đặt tàu. Bạn có thể chọn tàu khác hoặc click lại để đổi vị trí."
        )

    def all_ships_placed(self):
        """Kiểm tra đã đặt đủ tất cả tàu chưa."""
        return len(self.ship_defs) > 0 and all(sh["placed"] for sh in self.ship_defs)

    def get_ships(self):
        """Trả về danh sách tàu để gửi lên server."""
        ships = []
        for sh in self.ship_defs:
            if not sh["placed"] or not sh["cells"]:
                continue
            cells = sh["cells"]
            r0, c0 = cells[0]
            ships.append({
                "r": r0,
                "c": c0,
                "len": sh["length"],
                "dir": sh["orientation"]
            })
        return ships

    # ----------------- ĐÁNH DẤU TRÚNG / TRƯỢT -----------------
    def mark(self, r, c, hit):
        if not (0 <= r < GRID_N and 0 <= c < GRID_N):
            return
        if self.state[r][c] != 0:
            return

        self.state[r][c] = 1 if hit else 2
        x = c * CELL + CELL // 2
        y = r * CELL + CELL // 2
        color = "#ffd166" if hit else "#89c2d9"

        # Hiệu ứng vòng tròn
        for rad in range(6, CELL // 2, 6):
            self.canvas.create_oval(
                x - rad, y - rad, x + rad, y + rad,
                outline=color, width=2
            )
        if hit:
            self.canvas.create_text(x, y, text="💥", font=("Segoe UI", 14))
        else:
            self.canvas.create_oval(
                x - 6, y - 6, x + 6, y + 6,
                outline="#6aa2c0", width=2
            )
