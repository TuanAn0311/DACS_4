# server.py
import socket
import threading
import json
import random
from datetime import datetime
from db import get_connection, get_all_users, set_user_status, delete_user, get_match_history, get_user_profile, update_user_profile, get_my_history
HOST = "0.0.0.0"
PORT = 5050

# clients: socket -> {"name": str, "room": room_id | None}
clients = {}

# rooms: room_id -> { ... }
rooms = {}

lock = threading.Lock()


# ===================== TIỆN ÍCH GỬI TIN =====================
def send(sock, data):
    """Gửi 1 gói JSON cho 1 client."""
    try:
        # Xử lý datetime để không bị lỗi JSON serialize
        def json_serial(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError ("Type %s not serializable" % type(obj))

        sock.sendall((json.dumps(data, default=json_serial) + "\n").encode())
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
    """Gửi trạng thái phòng hiện tại cho 1 client."""
    info = clients.get(sock)
    if not info:
        send(sock, {"type": "ROOM_STATE", "players": [], "ready": [], "stage": "none"})
        return

    room_id = info.get("room")
    if not room_id or room_id not in rooms:
        send(sock, {"type": "ROOM_STATE", "players": [], "ready": [], "stage": "none"})
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
    try:
        if room_id not in rooms: return
        r = rooms[room_id]
        p1, p2 = r.get("players", [])[:2]
        
        stats = r.get("stats", {})
        s1 = stats.get(p1, {"shots": 0, "hits": 0, "misses": 0})
        s2 = stats.get(p2, {"shots": 0, "hits": 0, "misses": 0})

        db = get_connection()
        cursor = db.cursor()

        name1 = clients[p1]["name"]
        name2 = clients[p2]["name"]

        # 1. Lấy MaTaiKhoan (theo cấu trúc bảng taikhoan)
        cursor.execute("SELECT MaTaiKhoan FROM taikhoan WHERE TenDangNhap=%s", (name1,))
        row1 = cursor.fetchone()
        cursor.execute("SELECT MaTaiKhoan FROM taikhoan WHERE TenDangNhap=%s", (name2,))
        row2 = cursor.fetchone()

        if row1 and row2:
            id1, id2 = row1[0], row2[0]
            winner_id = id1 if winner_sock == p1 else id2
            loser_id = id2 if winner_sock == p1 else id1
            
            start_time = r.get("start_time") or datetime.now()
            end_time = datetime.now()

            # 2. Insert vào bảng lich_su_tran_dau (Đúng tên cột)
            sql = """
                INSERT INTO lich_su_tran_dau 
                (MaNguoiChoi1, MaNguoiChoi2, ThoiGianBatDau, ThoiGianKetThuc, 
                 SoLuotBan_NC1, SoLuotBan_NC2, SoLuotTrung_NC1, SoLuotTrung_NC2, NguoiThang)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            # Lưu ý: s1 tương ứng người chơi 1, s2 tương ứng người chơi 2
            cursor.execute(sql, (
                id1, id2, start_time, end_time, 
                s1["shots"], s2["shots"], s1["hits"], s2["hits"], winner_id
            ))

            # 3. Update bảng taikhoan (Đúng tên cột MaTaiKhoan)
            cursor.execute("UPDATE taikhoan SET SoTranThang = SoTranThang + 1 WHERE MaTaiKhoan=%s", (winner_id,))
            cursor.execute("UPDATE taikhoan SET SoTranThua = SoTranThua + 1 WHERE MaTaiKhoan=%s", (loser_id,))
            
            db.commit()
            print(f"✅ Đã lưu kết quả trận đấu: {name1} vs {name2}")

    except Exception as e:
        print("❗ Lỗi lưu kết quả (server.py):", e)
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

# ===================== LUỒNG CLIENT =====================
def handle_client(sock):
    username = f"User{random.randint(1000, 9999)}"
    clients[sock] = {"name": username, "room": None}
    send(sock, {"type": "WELCOME", "username": username})

    buf = ""
    try:
        while True:
            data = sock.recv(4096)
            if not data: break
            buf += data.decode()
            while "\n" in buf:
                raw, buf = buf.split("\n", 1)
                if not raw.strip(): continue
                try:
                    msg = json.loads(raw)
                    process(sock, msg)
                except Exception as e:
                    print("JSON error:", e)
    except:
        pass
    finally:
        leave_room(sock)
        if sock in clients: del clients[sock]
        sock.close()


# ===================== RỜI PHÒNG =====================
def leave_room(sock):
    info = clients.get(sock)
    if not info: return
    room_id = info.get("room")
    if not room_id or room_id not in rooms: return

    with lock:
        r = rooms[room_id]
        if sock in r["players"]:
            r["players"].remove(sock)
        clients[sock]["room"] = None

        # Nếu phòng trống -> Xóa
        if not r["players"]:
            del rooms[room_id]
            print(f"🧹 Phòng {room_id} đã bị xóa")
            broadcast_rooms()
            return

        # Nếu còn người -> Reset về waiting
        r.update({
            "stage": "waiting", "ready": {}, "boards": {}, 
            "shots": {}, "stats": {}, "turn": None, 
            "start_time": None, "replay_requests": set()
        })
        
        remain = r["players"][0]
        send(remain, {"type": "CHAT", "msg": "⚠ Đối thủ đã rời phòng."})
        update_names(room_id)
        broadcast_rooms()


# ===================== XỬ LÝ GÓI TIN =====================
def process(sock, msg):
    t = msg.get("type")

    # ==================== ADMIN LOGIC ====================
    if t == "ADMIN_GET_USERS":
        users = get_all_users()
        send(sock, {"type": "ADMIN_USER_LIST", "users": users})

    elif t == "ADMIN_LOCK_USER":
        target = msg.get("username")
        status = msg.get("status") # 'Active' or 'Locked'
        ok = set_user_status(target, status)
        if ok:
            users = get_all_users()
            send(sock, {"type": "ADMIN_USER_LIST", "users": users})
            send(sock, {"type": "ADMIN_ACTION_OK", "msg": f"Đã cập nhật trạng thái {target}"})
        else:
            send(sock, {"type": "ADMIN_ACTION_FAIL", "msg": "Lỗi Database!"})

    elif t == "ADMIN_DELETE_USER":
        target = msg.get("username")
        ok = delete_user(target)
        if ok:
            users = get_all_users()
            send(sock, {"type": "ADMIN_USER_LIST", "users": users})
            send(sock, {"type": "ADMIN_ACTION_OK", "msg": f"Đã xóa {target}"})
        else:
            send(sock, {"type": "ADMIN_ACTION_FAIL", "msg": "Lỗi Database!"})

    elif t == "ADMIN_GET_ROOMS":
        # Lấy từ memory (RAM) vì đây là trạng thái realtime
        room_data = []
        for rid, r in rooms.items():
            status = "Đang chơi" if r.get("stage") == "playing" else "Đang chờ"
            p_names = [clients[p]["name"] for p in r["players"]]
            room_data.append({
                "id": rid,
                "players": p_names,
                "status": status
            })
        send(sock, {"type": "ADMIN_ROOM_LIST", "rooms": room_data})

    elif t == "ADMIN_KILL_ROOM":
        target_rid = msg.get("room_id")
        if target_rid in rooms:
            r = rooms[target_rid]
            # Đuổi hết người chơi ra
            for p in list(r["players"]): # copy list để safe remove
                clients[p]["room"] = None
                send(p, {"type": "ERROR", "msg": "⛔ Phòng đã bị Admin giải tán!"})
                # Gửi gói tin để client tự quay về lobby nếu cần thiết
                # (Ở đây ta chỉ xóa logical, client game sẽ tự xử lý khi nhận ERROR hoặc ngắt kết nối)
            
            del rooms[target_rid]
            broadcast_rooms() # Cập nhật lobby cho mọi người
            
            # Refresh list cho Admin
            process(sock, {"type": "ADMIN_GET_ROOMS"})
            send(sock, {"type": "ADMIN_ACTION_OK", "msg": f"Đã hủy phòng {target_rid}"})

    elif t == "ADMIN_GET_HISTORY":
        hist = get_match_history()
        # Convert datetime to string handled in send() function
        send(sock, {"type": "ADMIN_HISTORY_LIST", "history": hist})


    # ==================== GAME LOGIC ====================
    elif t == "SET_NAME":
        name = msg.get("name", "")
        if name:
            clients[sock]["name"] = name
            if clients[sock].get("room"): update_names(clients[sock]["room"])

    elif t == "GET_ROOMS":
        broadcast_rooms() # Gửi riêng cho người yêu cầu thì đúng hơn nhưng broadcast cũng ok

    elif t == "CREATE_ROOM":
        rid = f"R{random.randint(1000, 9999)}"
        owner = msg.get("owner", clients[sock]["name"])
        with lock:
            rooms[rid] = {
                "players": [sock], "owner": owner, "turn": None, "ready": {},
                "stage": "waiting", "boards": {}, "shots": {}, "stats": {},
                "start_time": None, "replay_requests": set()
            }
        clients[sock]["room"] = rid
        send(sock, {"type": "JOINED_ROOM", "room": rid, "owner": owner})
        broadcast_rooms()

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
        
        if len(r["players"]) == 2:
            broadcast(rid, {"type": "START", "players": [clients[p]["name"] for p in r["players"]], "ready": [False, False]})
            update_names(rid)
        
        broadcast_rooms()

    elif t == "LEAVE_ROOM":
        leave_room(sock)

    elif t == "CHAT":
        rid = clients[sock].get("room")
        if rid: broadcast(rid, {"type": "CHAT", "msg": f"{clients[sock]['name']}: {msg.get('msg')}"})

    elif t == "READY":
        rid = clients[sock].get("room")
        if rid and rid in rooms:
            r = rooms[rid]
            r["ready"][sock] = True
            broadcast(rid, {
                "type": "READY_STATE", 
                "players": [clients[p]["name"] for p in r["players"]],
                "ready": [r["ready"].get(p, False) for p in r["players"]]
            })
            # Nếu cả 2 ready
            if len(r["players"]) == 2 and all(r["ready"].values()) and r["stage"] == "waiting":
                r["stage"] = "placing"
                broadcast(rid, {"type": "PLACE_PHASE", "ships": [5, 4, 3, 2]})

    elif t == "GET_ROOM_STATE":
        send_room_state(sock)

    elif t == "PLACE_DONE":
        rid = clients[sock].get("room")
        if not rid or rooms[rid]["stage"] != "placing": return
        r = rooms[rid]
        
        # Xử lý ships (giống logic cũ)
        ships = msg.get("ships", [])
        alive_cells = set()
        try:
            for sh in ships:
                length, rr, cc, d = int(sh["len"]), int(sh["r"]), int(sh["c"]), sh.get("dir", "H")
                cells = set()
                for k in range(length):
                    rc, colc = rr + (k if d=="V" else 0), cc + (k if d=="H" else 0)
                    if not (0<=rc<10 and 0<=colc<10): raise ValueError
                    if (rc, colc) in alive_cells: raise ValueError
                    cells.add((rc, colc))
                alive_cells |= cells
            
            r["boards"][sock] = {"alive_cells": alive_cells}
        except:
            send(sock, {"type": "ERROR", "msg": "Bố trí lỗi!"})
            return

        if len(r["boards"]) == 2:
            r["stage"] = "playing"
            p1, p2 = r["players"]
            r["turn"] = p1
            r["stats"] = {p1: {"shots":0,"hits":0,"misses":0}, p2: {"shots":0,"hits":0,"misses":0}}
            r["start_time"] = datetime.now()
            broadcast(rid, {"type": "GAME_START"})
            send(p1, {"type": "TURN", "your_turn": True})
            send(p2, {"type": "TURN", "your_turn": False})

    elif t == "SHOOT":
        rid = clients[sock].get("room")
        if not rid or rooms[rid]["stage"] != "playing": return
        r = rooms[rid]
        if r["turn"] != sock: 
            send(sock, {"type": "ERROR", "msg": "Chưa đến lượt!"})
            return

        row, col = msg.get("r"), msg.get("c")
        players = r["players"]
        enemy = players[1] if players[0] == sock else players[0]
        
        enemy_cells = r["boards"][enemy]["alive_cells"]
        hit = (row, col) in enemy_cells
        if hit: enemy_cells.remove((row, col))

        # Stats
        st = r["stats"][sock]
        st["shots"] += 1
        if hit: st["hits"] += 1
        else: st["misses"] += 1

        broadcast(rid, {"type": "SHOT_RESULT", "by": clients[sock]["name"], "target": clients[enemy]["name"], "r": row, "c": col, "hit": hit})

        if not enemy_cells: # Thắng
            save_match_result(rid, sock, enemy)
            broadcast(rid, {"type": "GAME_OVER", "winner": clients[sock]["name"]})
            r["stage"] = "finished"
        else:
            if not hit: 
                r["turn"] = enemy
                send(enemy, {"type": "TURN", "your_turn": True})
                send(sock, {"type": "TURN", "your_turn": False})
            else:
                send(sock, {"type": "TURN", "your_turn": True})

    elif t == "PLAY_AGAIN":
        rid = clients[sock].get("room")
        if rid and rooms[rid]["stage"] == "finished":
            r = rooms[rid]
            r["replay_requests"].add(sock)
            players = r["players"]
            enemy = players[1] if players[0] == sock else players[0]
            send(enemy, {"type": "REMATCH_OFFER", "from": clients[sock]["name"]})

    elif t == "PLAY_AGAIN_RESPONSE":
        rid = clients[sock].get("room")
        if rid:
            accept = msg.get("accept")
            if not accept:
                leave_room(sock)
            else:
                r = rooms[rid]
                r["replay_requests"].add(sock)
                if len(r["replay_requests"]) == 2:
                    # Reset Game
                    r.update({"stage": "waiting", "ready": {}, "boards": {}, "stats": {}, "replay_requests": set()})
                    p1, p2 = r["players"]
                    r["ready"] = {p1: False, p2: False}
                    broadcast(rid, {"type": "REMATCH_READY", "players": [clients[p1]["name"], clients[p2]["name"]]})
    
    # ==================== USER PROFILE & HISTORY ====================

    elif t == "GET_PROFILE":
        username = clients[sock]["name"]
        data = get_user_profile(username)
        if data:
            # Chuyển đổi ngày tháng thành chuỗi để không lỗi JSON
            if data.get('NgayTao'): 
                data['NgayTao'] = str(data['NgayTao'])
            
            if data.get('NgayCapNhat'): 
                data['NgayCapNhat'] = str(data['NgayCapNhat'])
            else:
                data['NgayCapNhat'] = "Chưa cập nhật"

            send(sock, {"type": "PROFILE_DATA", "data": data})

    # [Trong file server.py -> hàm process]

    elif t == "UPDATE_PROFILE":
        old_name = clients[sock]["name"]
        new_name = msg.get("new_username")
        email = msg.get("email")
        pw = msg.get("password")
        
        # Gọi hàm DB mới
        ok, message = update_user_profile(old_name, new_name, email, pw)
        
        if ok:
            # Cập nhật lại tên trong bộ nhớ RAM của Server
            clients[sock]["name"] = new_name
            # Nếu đang ở trong phòng, cần cập nhật tên cho đối thủ thấy (Optional)
            rid = clients[sock].get("room")
            if rid: update_names(rid)
            
            send(sock, {"type": "PROFILE_UPDATE_OK", "msg": message})
        else:
            send(sock, {"type": "ERROR", "msg": message})

    elif t == "DELETE_SELF":
        username = clients[sock]["name"]
        ok = delete_user(username) # Hàm này đã có sẵn ở bài trước
        if ok:
            send(sock, {"type": "DELETE_OK", "msg": "Tài khoản đã bị xóa. Tạm biệt!"})
        else:
            send(sock, {"type": "ERROR", "msg": "Lỗi khi xóa tài khoản!"})

    elif t == "GET_MY_HISTORY":
        username = clients[sock]["name"]
        hist = get_my_history(username)
        # Datetime sẽ được json_serial xử lý ở hàm send
        send(sock, {"type": "MY_HISTORY_DATA", "history": hist})


# ===================== CHẠY SERVER =====================
def start():
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen()
    print(f"✅ SERVER ĐANG CHẠY TẠI {HOST}:{PORT}")

    while True:
        client, addr = s.accept()
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

if __name__ == "__main__":
    start()