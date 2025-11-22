import tkinter as tk
from screen_login import LoginScreen
from screen_register import RegisterScreen
from screen_lobby import LobbyScreen
from screen_battle import BattleScreen
from screen_result import ResultScreen
from screen_admin import AdminScreen
from client import Client
import tkinter.messagebox as messagebox


class App(tk.Tk):
    def __init__(self, host="127.0.0.1", port=5050):
        super().__init__()
        self.title("Battleship — Modern UI")
        self.geometry("1200x780")

        self.client = Client()
        try:
            self.client.connect(host, port)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể kết nối server:\n{e}")
            self.destroy()
            return

        self.username = None
        self.current_room_id = None  # ⭐ lưu room hiện tại để chơi lại

        # Đăng ký các sự kiện từ server
        self.client.on("WELCOME", self._welcome)
        self.client.on("REMATCH_OFFER", self._on_rematch_offer)
        self.client.on("REMATCH_READY", self._on_rematch_ready)
        self.client.on("REMATCH_DENIED", self._on_rematch_denied)

        self._show_login()

    def _welcome(self, msg):
        self.username = msg["username"]

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()

    def _show_login(self):
        self._clear()
        LoginScreen(self, self._show_register, self._on_login)

    def _show_register(self):
        self._clear()
        RegisterScreen(self, self._show_login, self._on_register)

    def _on_register(self, user, pw):
        # Ở bản gốc của bạn có thể gọi hàm trong db.py để lưu.
        # Tạm thời chỉ báo thành công cho đơn giản.
        messagebox.showinfo("Đăng ký thành công",
                            f"Tài khoản '{user}' đã được tạo!")
        self._show_login()

    # ✅ GỬI TÊN TỪ DATABASE SANG SERVER
    def _on_login(self, username):
        self.username = username

        self.client.send({
            "type": "SET_NAME",
            "name": self.username
        })

        self._show_lobby()

    def _show_lobby(self):
        self._clear()
        LobbyScreen(self, self.username, self._show_battle,
                    self._show_login, self._show_admin)

    def _show_battle(self, room_id):
        self._clear()
        self.current_room_id = room_id   # ⭐ lưu lại để chơi lại
        BattleScreen(self, self.username, self._show_lobby,
                     self._show_result, room_id)

    def _show_result(self, winner, turns, hits, misses):
        self._clear()
        ResultScreen(
            self,
            winner, turns, hits, misses,
            back_lobby=self._back_to_lobby_from_result,
            play_again=self._request_rematch
        )

    # ====== CALLBACK CHO KẾT QUẢ ======
    def _back_to_lobby_from_result(self):
        """Người chơi chọn 'Quay về sảnh'."""
        try:
            self.client.send({"type": "LEAVE_ROOM"})
        except Exception:
            pass
        self.current_room_id = None
        self._show_lobby()

    def _request_rematch(self):
        """Người chơi bấm 'Chơi lại' – gửi yêu cầu rematch."""
        try:
            self.client.send({"type": "PLAY_AGAIN"})
        except Exception as e:
            messagebox.showerror("Lỗi",
                                 f"Không gửi được yêu cầu chơi lại:\n{e}")
            return

        messagebox.showinfo(
            "Chơi lại",
            "Đã gửi yêu cầu chơi lại.\nChờ đối thủ xác nhận..."
        )

    # ====== HANDLER REMATCH TỪ SERVER ======
    def _on_rematch_offer(self, msg):
        from_name = msg.get("from", "Đối thủ")
        ans = messagebox.askyesno(
            "Chơi lại?",
            f"{from_name} muốn chơi lại với bạn.\nBạn có đồng ý không?"
        )
        self.client.send({
            "type": "PLAY_AGAIN_RESPONSE",
            "accept": bool(ans)
        })

    def _on_rematch_ready(self, msg):
        """Cả hai đã đồng ý chơi lại – vào trận mới."""
        room = msg.get("room")
        if room:
            self.current_room_id = room
        if not self.current_room_id:
            # phòng bị mất -> quay về sảnh
            messagebox.showinfo("Chơi lại", "Phòng không còn tồn tại.")
            self._show_lobby()
            return

        messagebox.showinfo("Chơi lại", "Cả hai đã đồng ý. Bắt đầu ván mới!")
        self._show_battle(self.current_room_id)

    def _on_rematch_denied(self, msg):
        by = msg.get("by", "Đối thủ")
        messagebox.showinfo("Chơi lại",
                            f"{by} không muốn chơi lại.\n"
                            "Phòng hiện chỉ còn mình bạn.")
        # Người chơi này vẫn ở trong phòng; có thể quay lại sảnh tuỳ ý.

    def _show_admin(self):
        self._clear()
        AdminScreen(self, self._show_lobby)


if __name__ == "__main__":
    app = App(host="127.0.0.1", port=5050)  # đổi IP tại đây nếu cần
    app.mainloop()
