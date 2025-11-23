# server.py
import socket
import threading
import json
import random
from datetime import datetime
from db import get_connection

HOST = "0.0.0.0"
PORT = 5050

# clients: socket -> {"name": str, "room": room_id | None}
clients = {}

# rooms: room_id -> {
#   "players": [sock1, sock2?],
#   "owner": str,
#   "turn": sock | None,
#   "ready": {sock: bool},
#   "stage": "waiting" | "placing" | "playing" | "finished",
#   "boards": {
#       sock: {
#           "ships": [...],
#           "alive_cells": set((r, c), ...)
#       }
#   },
#   "shots": {
#       sock: set((r, c), ...)
#   },
#   "stats": {
#       sock: {"shots": int, "hits": int, "misses": int}
#   },
#   "start_time": datetime | None,
#   "replay_requests": set(sock, ...)
# }
rooms = {}

lock = threading.Lock()


# ===================== TIỆN ÍCH GỬI TIN =====================
def send(sock, data):
    """Gửi 1 gói JSON cho 1 client."""
    try:
        sock.sendall((json.dumps(data) + "\n").encode())
    except Exception:
        pass


def broadcast(room_id, data):
    """Gửi 1 gói JSON cho toàn bộ client trong phòng."""
    if room_id not in rooms:
        return
    for p in rooms[room_id]["players"]:
        send(p, data)


# ===== CẬP NHẬT DANH SÁCH PHÒNG CHO TẤT CẢ CLIENT (LOBBY) =====
def broadcast_rooms():
    room_list = []
    for rid, r in rooms.items():
        room_list.append({
            "id": rid,
            "players": len(r["players"]),
            "owner": r.get("owner", "Unknown")
        })

    for sock in list(clients.keys()):
        send(sock, {
            "type": "ROOM_LIST",
            "rooms": room_list
        })


# ===================== CẬP NHẬT TÊN REALTIME =====================
def update_names(room_id):
    """Gửi NAME_UPDATE để 2 bên thấy tên nhau realtime."""
    if room_id not in rooms:
        return
    players = rooms[room_id]["players"]
    names = [clients[p]["name"] for p in players]
    broadcast(room_id, {
        "type": "NAME_UPDATE",
        "players": names
    })


def send_room_state(sock):
    """Gửi trạng thái phòng hiện tại cho 1 client (BattleScreen mới mở)."""
    info = clients.get(sock)
    if not info:
        send(sock, {
            "type": "ROOM_STATE",
            "players": [],
            "ready": [],
            "stage": "none"
        })
        return

    room_id = info.get("room")
    if not room_id or room_id not in rooms:
        send(sock, {
            "type": "ROOM_STATE",
            "players": [],
            "ready": [],
            "stage": "none"
        })
        return

    r = rooms[room_id]
    players = r["players"]
    names = [clients[p]["name"] for p in players]

    ready_map = r.get("ready", {})
    ready_list = [bool(ready_map.get(p, False)) for p in players]
    stage = r.get("stage", "waiting")

    send(sock, {
        "type": "ROOM_STATE",
        "players": names,
        "ready": ready_list,
        "stage": stage
    })


# ===================== LƯU KẾT QUẢ VÀO CSDL =====================
def save_match_result(room_id, winner_sock, loser_sock):
    """
    Lưu lịch sử trận đấu vào bảng lich_su_tran_dau
    + cập nhật SoTranThang / SoTranThua trong bảng taikhoan.
    """
    try:
        if room_id not in rooms:
            return

        r = rooms[room_id]
        players = r.get("players", [])
        if len(players) != 2:
            return

        p1, p2 = players
        stats = r.get("stats", {})
        s1 = stats.get(p1, {"shots": 0, "hits": 0, "misses": 0})
        s2 = stats.get(p2, {"shots": 0, "hits": 0, "misses": 0})

        db = get_connection()
        cursor = db.cursor()

        name1 = clients[p1]["name"]
        name2 = clients[p2]["name"]

        # Lấy MaTaiKhoan theo TenDangNhap
        cursor.execute(
            "SELECT MaTaiKhoan FROM taikhoan WHERE TenDangNhap=%s", (name1,)
        )
        row = cursor.fetchone()
        if not row:
            return
        id1 = row[0]

        cursor.execute(
            "SELECT MaTaiKhoan FROM taikhoan WHERE TenDangNhap=%s", (name2,)
        )
        row = cursor.fetchone()
        if not row:
            return
        id2 = row[0]

        winner_name = clients[winner_sock]["name"]
        if winner_sock == p1:
            winner_id = id1
        else:
            winner_id = id2

        start_time = r.get("start_time") or datetime.now()
        end_time = datetime.now()

        # Thêm bản ghi lịch sử trận đấu
        sql = """
            INSERT INTO lich_su_tran_dau
            (MaNguoiChoi1, MaNguoiChoi2,
             ThoiGianBatDau, ThoiGianKetThuc,
             SoLuotBan_NC1, SoLuotBan_NC2,
             SoLuotTrung_NC1, SoLuotTrung_NC2,
             NguoiThang)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        cursor.execute(sql, (
            id1, id2,
            start_time, end_time,
            s1["shots"], s2["shots"],
            s1["hits"], s2["hits"],
            winner_id
        ))

        # Cập nhật số trận thắng / thua
        cursor.execute(
            "UPDATE taikhoan SET SoTranThang = SoTranThang + 1 WHERE MaTaiKhoan=%s",
            (winner_id,)
        )
        loser_id = id1 if winner_id == id2 else id2
        cursor.execute(
            "UPDATE taikhoan SET SoTranThua = SoTranThua + 1 WHERE MaTaiKhoan=%s",
            (loser_id,)
        )

        db.commit()

    except Exception as e:
        print("❗ Lỗi lưu kết quả trận đấu:", e)
    finally:
        try:
            if db.is_connected():
                cursor.close()
                db.close()
        except Exception:
            pass


# ===================== LUỒNG CLIENT =====================
def handle_client(sock):
    """Vòng lặp lắng nghe cho từng client."""
    username = f"User{random.randint(1000, 9999)}"
    clients[sock] = {"name": username, "room": None}

    send(sock, {"type": "WELCOME", "username": username})

    buf = ""
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break

            buf += data.decode()

            while "\n" in buf:
                raw, buf = buf.split("\n", 1)
                if not raw.strip():
                    continue
                try:
                    msg = json.loads(raw)
                    process(sock, msg)
                except Exception as e:
                    print("JSON error:", e)

    except Exception:
        pass
    finally:
        leave_room(sock)
        if sock in clients:
            del clients[sock]
        # broadcast_rooms() không bắt buộc ở đây vì leave_room đã gọi
        sock.close()


# ===================== RỜI PHÒNG =====================
def leave_room(sock):
    info = clients.get(sock)
    if not info:
        return

    room_id = info.get("room")
    if not room_id or room_id not in rooms:
        clients[sock]["room"] = None
        return

    with lock:
        r = rooms[room_id]

        # Xóa người chơi khỏi phòng
        if sock in r["players"]:
            r["players"].remove(sock)

        # Reset cho client
        clients[sock]["room"] = None

        # ========= NẾU PHÒNG TRỐNG → XÓA =========
        if not r["players"]:
            del rooms[room_id]

            print(f"🧹 Phòng {room_id} đã bị xóa")
            print("ROOMS HIỆN TẠI:", {k: len(v['players']) for k, v in rooms.items()})

            # Cập nhật lobby
            broadcast_rooms()
            return

        # ========= NẾU CÒN 1 NGƯỜI =========
        r["stage"] = "waiting"
        r["ready"] = {}
        r["boards"] = {}
        r["shots"] = {}
        r["stats"] = {}
        r["turn"] = None
        r["replay_requests"] = set()
        r["start_time"] = None

        remain = r["players"][0]

        send(remain, {
            "type": "CHAT",
            "msg": "⚠ Đối thủ đã rời phòng."
        })

        update_names(room_id)

        print("ROOMS SAU KHI RỜI:", {k: len(v['players']) for k, v in rooms.items()})

        # Cập nhật lobby
        broadcast_rooms()


# ===================== XỬ LÝ GÓI TIN =====================
def process(sock, msg):
    t = msg.get("type")

    # ---------- SET_NAME ----------
    if t == "SET_NAME":
        name = msg.get("name", "")
        if name:
            clients[sock]["name"] = name
            room_id = clients[sock].get("room")
            if room_id:
                update_names(room_id)

    # ---------- GET_ROOMS ----------
    elif t == "GET_ROOMS":
        send(sock, {
            "type": "ROOM_LIST",
            "rooms": [
                {
                    "id": rid,
                    "players": len(r["players"]),
                    "owner": r.get("owner", "Unknown")
                }
                for rid, r in rooms.items()
            ]
        })

    # ---------- CREATE_ROOM ----------
    elif t == "CREATE_ROOM":
        rid = f"R{random.randint(1000, 9999)}"
        owner = msg.get("owner", clients[sock]["name"])

        with lock:
            rooms[rid] = {
                "players": [sock],
                "owner": owner,
                "turn": None,
                "ready": {},
                "stage": "waiting",
                "boards": {},
                "shots": {},
                "stats": {},
                "start_time": None,
                "replay_requests": set()
            }

        clients[sock]["room"] = rid

        send(sock, {
            "type": "JOINED_ROOM",
            "room": rid,
            "owner": owner
        })

        # cập nhật lobby sau khi tạo phòng
        broadcast_rooms()

    # ---------- JOIN_ROOM ----------
    elif t == "JOIN_ROOM":
        rid = msg.get("room")
        if rid not in rooms:
            send(sock, {"type": "ERROR", "msg": "Phòng không tồn tại!"})
            return

        r = rooms[rid]
        if len(r["players"]) >= 2:
            send(sock, {"type": "ERROR", "msg": "Phòng đã đầy!"})
            return

        r["players"].append(sock)
        clients[sock]["room"] = rid

        send(sock, {"type": "JOINED_ROOM", "room": rid})

        # đủ 2 người -> gửi START + READY_STATE
        if len(r["players"]) == 2:
            p1, p2 = r["players"]
            name1 = clients[p1]["name"]
            name2 = clients[p2]["name"]

            r["ready"] = {p1: False, p2: False}
            r["stage"] = "waiting"
            r["boards"] = {}
            r["shots"] = {}
            r["stats"] = {}
            r["start_time"] = None
            r["replay_requests"] = set()

            broadcast(rid, {
                "type": "START",
                "players": [name1, name2],
                "ready": [False, False]
            })

            update_names(rid)

        # cập nhật lobby sau khi có người join
        broadcast_rooms()

    # ---------- LEAVE_ROOM (tự rời phòng nhưng vẫn online) ----------
    elif t == "LEAVE_ROOM":
        leave_room(sock)

    # ---------- CHAT ----------
    elif t == "CHAT":
        room_id = clients[sock].get("room")
        if room_id:
            broadcast(room_id, {
                "type": "CHAT",
                "msg": f"{clients[sock]['name']}: {msg.get('msg', '')}"
            })

    # ---------- READY ----------
    elif t == "READY":
        room_id = clients[sock].get("room")
        if not room_id or room_id not in rooms:
            return

        r = rooms[room_id]
        if "ready" not in r:
            r["ready"] = {p: False for p in r["players"]}

        r["ready"][sock] = True

        players = r["players"]
        ready_map = r["ready"]
        player_names = [clients[p]["name"] for p in players]
        ready_list = [bool(ready_map.get(p, False)) for p in players]

        broadcast(room_id, {
            "type": "READY_STATE",
            "players": player_names,
            "ready": ready_list
        })

        # Nếu cả 2 đã sẵn sàng và đang ở stage "waiting" -> sang giai đoạn đặt tàu
        if len(players) == 2 and all(ready_list) and r.get("stage") == "waiting":
            r["stage"] = "placing"
            r["boards"] = {}
            r["shots"] = {}
            r["stats"] = {}
            r["start_time"] = None

            broadcast(room_id, {
                "type": "PLACE_PHASE",
                "ships": [5, 4, 3, 2]
            })

    # ---------- GET_ROOM_STATE (Battle mới mở) ----------
    elif t == "GET_ROOM_STATE":
        send_room_state(sock)

    # ---------- PLACE_DONE (gửi bố trí tàu) ----------
    elif t == "PLACE_DONE":
        room_id = clients[sock].get("room")
        if not room_id or room_id not in rooms:
            return

        r = rooms[room_id]
        if r.get("stage") != "placing":
            return

        ships = msg.get("ships", [])
        ship_list = []
        alive_cells = set()

        try:
            for sh in ships:
                length = int(sh.get("len"))
                rr = int(sh.get("r"))
                cc = int(sh.get("c"))
                direction = sh.get("dir", "H")

                cells = set()
                for k in range(length):
                    rcell = rr + (k if direction == "V" else 0)
                    ccell = cc + (k if direction == "H" else 0)

                    # kiểm tra trong biên 10x10
                    if not (0 <= rcell < 10 and 0 <= ccell < 10):
                        raise ValueError("out_of_board")

                    if (rcell, ccell) in alive_cells:
                        raise ValueError("overlap")

                    cells.add((rcell, ccell))

                ship_list.append({
                    "length": length,
                    "r": rr,
                    "c": cc,
                    "dir": direction,
                    "cells": cells
                })
                alive_cells |= cells

            # lưu cho người chơi này
            boards = r.setdefault("boards", {})
            boards[sock] = {
                "ships": ship_list,
                "alive_cells": alive_cells
            }

        except Exception:
            send(sock, {"type": "ERROR", "msg": "Bố trí tàu không hợp lệ."})
            return

        # Nếu cả 2 người chơi đều đã gửi bố trí tàu
        if len(r["boards"]) == 2:
            r["stage"] = "playing"
            p1, p2 = r["players"]
            r["turn"] = p1
            r["shots"] = {p1: set(), p2: set()}
            r["stats"] = {
                p1: {"shots": 0, "hits": 0, "misses": 0},
                p2: {"shots": 0, "hits": 0, "misses": 0}
            }
            r["start_time"] = datetime.now()

            broadcast(room_id, {"type": "GAME_START"})
            send(p1, {"type": "TURN", "your_turn": True})
            send(p2, {"type": "TURN", "your_turn": False})

    # ---------- SHOOT ----------
    elif t == "SHOOT":
        room_id = clients[sock].get("room")
        if not room_id or room_id not in rooms:
            return

        r = rooms[room_id]
        if r.get("stage") != "playing":
            send(sock, {"type": "ERROR", "msg": "Trận đấu chưa bắt đầu."})
            return

        if r.get("turn") != sock:
            send(sock, {"type": "ERROR", "msg": "Không phải lượt bạn."})
            return

        row = msg.get("r")
        col = msg.get("c")

        players = r["players"]
        if len(players) < 2:
            return

        enemy_sock = players[1] if players[0] == sock else players[0]

        boards = r.get("boards", {})
        enemy_board = boards.get(enemy_sock)
        if not enemy_board:
            return

        enemy_cells = enemy_board["alive_cells"]

        # Kiểm tra trúng / trượt
        hit = (row, col) in enemy_cells
        if hit:
            enemy_cells.remove((row, col))

        # Cập nhật thống kê
        stats = r.setdefault("stats", {}).setdefault(
            sock, {"shots": 0, "hits": 0, "misses": 0}
        )
        stats["shots"] += 1
        if hit:
            stats["hits"] += 1
        else:
            stats["misses"] += 1

        # Thông báo cho cả phòng
        broadcast(room_id, {
            "type": "SHOT_RESULT",
            "by": clients[sock]["name"],
            "target": clients[enemy_sock]["name"],
            "r": row,
            "c": col,
            "hit": hit
        })

        # Kiểm tra thắng (toàn bộ ô tàu đã bị bắn hết)
        if not enemy_cells:
            # Lưu kết quả vào CSDL
            save_match_result(room_id, winner_sock=sock, loser_sock=enemy_sock)

            broadcast(room_id, {
                "type": "GAME_OVER",
                "winner": clients[sock]["name"]
            })
            r["stage"] = "finished"
            return

        # Điều khiển lượt
        if hit:
            # bắn trúng -> ở lại lượt
            send(sock, {"type": "TURN", "your_turn": True})
            send(enemy_sock, {"type": "TURN", "your_turn": False})
        else:
            # trượt -> đổi lượt
            r["turn"] = enemy_sock
            send(enemy_sock, {"type": "TURN", "your_turn": True})
            send(sock, {"type": "TURN", "your_turn": False})

    # ---------- YÊU CẦU CHƠI LẠI ----------
    elif t == "PLAY_AGAIN":
        room_id = clients[sock].get("room")
        if not room_id or room_id not in rooms:
            return

        r = rooms[room_id]
        if r.get("stage") != "finished":
            send(sock, {"type": "ERROR", "msg": "Trận đấu chưa kết thúc."})
            return

        players = r["players"]
        if len(players) < 2:
            send(sock, {"type": "ERROR", "msg": "Không còn đối thủ trong phòng."})
            return

        enemy_sock = players[1] if players[0] == sock else players[0]

        # Ghi nhận người yêu cầu chơi lại
        rr = r.setdefault("replay_requests", set())
        rr.add(sock)

        # Gửi lời mời đến đối thủ
        send(enemy_sock, {
            "type": "REMATCH_OFFER",
            "from": clients[sock]["name"]
        })

    # ---------- PHẢN HỒI CHƠI LẠI ----------
    elif t == "PLAY_AGAIN_RESPONSE":
        room_id = clients[sock].get("room")
        if not room_id or room_id not in rooms:
            return

        r = rooms[room_id]
        accept = bool(msg.get("accept"))
        players = r["players"]
        if len(players) < 2:
            return

        enemy_sock = players[1] if players[0] == sock else players[0]

        if not accept:
            # Từ chối -> báo cho đối thủ, người này rời phòng
            send(enemy_sock, {
                "type": "REMATCH_DENIED",
                "by": clients[sock]["name"]
            })
            leave_room(sock)
            return

        # Đồng ý -> nếu cả 2 đã đồng ý thì reset phòng và báo REMATCH_READY
        rr = r.setdefault("replay_requests", set())
        rr.add(sock)

        if len(rr) == 2:
            # Reset trạng thái phòng để chơi ván mới
            r["stage"] = "waiting"
            r["ready"] = {players[0]: False, players[1]: False}
            r["boards"] = {}
            r["shots"] = {}
            r["stats"] = {}
            r["start_time"] = None
            r["replay_requests"] = set()

            broadcast(room_id, {
                "type": "REMATCH_READY",
                "room": room_id,
                "players": [clients[players[0]]["name"],
                            clients[players[1]]["name"]]
            })

    # ---------- MẶC ĐỊNH ----------
    else:
        send(sock, {"type": "ERROR", "msg": "Loại message không hỗ trợ."})


# ===================== CHẠY SERVER =====================
def start():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()
    print(f"SERVER RUNNING ON {HOST}:{PORT}")

    while True:
        client, addr = s.accept()
        threading.Thread(target=handle_client, args=(client,),
                         daemon=True).start()


if __name__ == "__main__":
    start()
