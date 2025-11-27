# db.py
import mysql.connector
from datetime import datetime
import hashlib

def get_connection():
    # ⚠️ LƯU Ý: Đảm bảo XAMPP đã BẬT và mật khẩu đúng
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",      # <--- Kiểm tra lại mật khẩu MySQL của bạn (thường là rỗng "" hoặc "123456")
        database="battleshipdb"
    )

# ===================== HASH PASSWORD =====================
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

# ===================== REGISTER USER =====================
def register_user(username, password):
    db = None  # ✅ Khởi tạo biến db trước
    cursor = None
    try:
        db = get_connection()
        cursor = db.cursor()

        # Kiểm tra tài khoản đã tồn tại chưa
        cursor.execute("SELECT * FROM taikhoan WHERE TenDangNhap = %s", (username,))
        if cursor.fetchone():
            return False, "Tài khoản đã tồn tại!"

        hashed_pw = hash_password(password)

        sql = """
        INSERT INTO taikhoan (TenDangNhap, MatKhau, SoTranThang, SoTranThua, NgayTao, TrangThai)
        VALUES (%s, %s, 0, 0, %s, 'Active')
        """
        cursor.execute(sql, (username, hashed_pw, datetime.now()))
        db.commit()

        return True, "Đăng ký thành công!"

    except Exception as e:
        print("Lỗi Register:", e) # In lỗi ra terminal để dễ sửa
        return False, f"Lỗi kết nối: {str(e)}"

    finally:
        if db and db.is_connected():
            if cursor: cursor.close()
            db.close()

# ===================== LOGIN USER =====================
def login_user(username, password):
    db = None # ✅ Khởi tạo biến db trước
    cursor = None
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        hashed_pw = hash_password(password)

        sql = """
        SELECT * FROM taikhoan 
        WHERE TenDangNhap = %s AND MatKhau = %s
        """
        cursor.execute(sql, (username, hashed_pw))
        user = cursor.fetchone()

        if user:
            if user.get('TrangThai') == 'Locked':
                return False, "Tài khoản của bạn đã bị khóa!"
            return True, user
        else:
            return False, "Sai tài khoản hoặc mật khẩu!"

    except Exception as e:
        print("Lỗi Login:", e)
        return False, f"Lỗi kết nối: {str(e)}"

    finally:
        if db and db.is_connected():
            if cursor: cursor.close()
            db.close()

# ===================== LOGIN ADMIN =====================
def login_admin(username, password):
    db = None
    cursor = None
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        hashed_pw = hash_password(password)

        # Kiểm tra bảng quanli
        sql = "SELECT * FROM quanli WHERE ten_dang_nhap = %s AND mat_khau = %s"
        cursor.execute(sql, (username, hashed_pw))
        admin = cursor.fetchone()

        if admin:
            return True, admin
        
        # Fallback: cho phép user 'admin' trong bảng taikhoan đăng nhập quyền admin (để test)
        if username == 'admin':
             sql_user = "SELECT * FROM taikhoan WHERE TenDangNhap = 'admin' AND MatKhau = %s"
             cursor.execute(sql_user, (hashed_pw,))
             user_admin = cursor.fetchone()
             if user_admin:
                 return True, user_admin

        return False, "Sai tài khoản quản trị!"

    except Exception as e:
        return False, str(e)

    finally:
        if db and db.is_connected():
            if cursor: cursor.close()
            db.close()

# ================= ADMIN: QUẢN LÝ NGƯỜI DÙNG =================
def get_all_users():
    db = None
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        sql = "SELECT TenDangNhap, SoTranThang, SoTranThua, TrangThai FROM taikhoan WHERE TenDangNhap != 'admin'"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        print("DB Error:", e)
        return []
    finally:
        if db and db.is_connected(): db.close()

def set_user_status(username, status):
    db = None
    try:
        db = get_connection()
        cursor = db.cursor()
        sql = "UPDATE taikhoan SET TrangThai = %s WHERE TenDangNhap = %s"
        cursor.execute(sql, (status, username))
        db.commit()
        return True
    except Exception as e:
        print("DB Error:", e)
        return False
    finally:
        if db and db.is_connected(): db.close()

def delete_user(username):
    db = None
    try:
        db = get_connection()
        cursor = db.cursor()
        sql = "DELETE FROM taikhoan WHERE TenDangNhap = %s"
        cursor.execute(sql, (username,))
        db.commit()
        return True
    except Exception as e:
        print("DB Error:", e)
        return False
    finally:
        if db and db.is_connected(): db.close()

# ================= ADMIN: LỊCH SỬ ĐẤU =================
# [File db.py]

# [File db.py]

def get_match_history():
    db = None
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        
        # SQL ĐÃ ĐƯỢC CHỈNH SỬA THEO ẢNH DATABASE
        sql = """
            SELECT 
                l.MaTranDau, 
                tk1.TenDangNhap as P1, 
                tk2.TenDangNhap as P2, 
                tk_win.TenDangNhap as Winner, 
                l.ThoiGianKetThuc as NgayGioKetThuc,
                l.SoLuotBan_NC1, 
                l.SoLuotTrung_NC1, 
                l.SoLuotBan_NC2, 
                l.SoLuotTrung_NC2
            FROM lich_su_tran_dau l
            JOIN taikhoan tk1 ON l.MaNguoiChoi1 = tk1.MaTaiKhoan
            JOIN taikhoan tk2 ON l.MaNguoiChoi2 = tk2.MaTaiKhoan
            LEFT JOIN taikhoan tk_win ON l.NguoiThang = tk_win.MaTaiKhoan
            ORDER BY l.ThoiGianKetThuc DESC
        """
        
        cursor.execute(sql)
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print("Lỗi lấy lịch sử (db.py):", e)
        return []
    finally:
        if db and db.is_connected():
            cursor.close()
            db.close()

# ================= USER: THÔNG TIN CÁ NHÂN =================

def get_user_profile(username):
    db = None
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        # Lấy thêm cột NgayCapNhat
        sql = "SELECT TenDangNhap, Email, SoTranThang, SoTranThua, NgayTao, NgayCapNhat FROM taikhoan WHERE TenDangNhap = %s"
        cursor.execute(sql, (username,))
        return cursor.fetchone()
    except Exception as e:
        print("Lỗi get_profile:", e)
        return None
    finally:
        if db and db.is_connected(): db.close()

# [Trong file db.py]

def update_user_profile(current_username, new_username, email, new_password=None):
    db = None
    try:
        db = get_connection()
        cursor = db.cursor()

        # 1. Nếu người dùng đổi tên, kiểm tra xem tên mới đã tồn tại chưa
        if new_username != current_username:
            cursor.execute("SELECT MaTaiKhoan FROM taikhoan WHERE TenDangNhap = %s", (new_username,))
            if cursor.fetchone():
                return False, "Tên đăng nhập này đã có người sử dụng!"

        # 2. Xây dựng câu lệnh SQL cập nhật
        # Chúng ta dùng current_username để tìm dòng cần sửa
        
        # Trường hợp đổi cả mật khẩu
        if new_password:
            hashed = hash_password(new_password)
            sql = """
                UPDATE taikhoan 
                SET TenDangNhap=%s, Email=%s, MatKhau=%s, NgayCapNhat=NOW() 
                WHERE TenDangNhap=%s
            """
            cursor.execute(sql, (new_username, email, hashed, current_username))
        
        # Trường hợp KHÔNG đổi mật khẩu
        else:
            sql = """
                UPDATE taikhoan 
                SET TenDangNhap=%s, Email=%s, NgayCapNhat=NOW() 
                WHERE TenDangNhap=%s
            """
            cursor.execute(sql, (new_username, email, current_username))
            
        db.commit()
        return True, "Cập nhật thành công!"

    except Exception as e:
        print("Lỗi update:", e)
        return False, f"Lỗi hệ thống: {str(e)}"
    finally:
        if db and db.is_connected(): db.close()


# ================= USER: LỊCH SỬ CÁ NHÂN =================
def get_my_history(username):
    """Lấy lịch sử đấu của riêng user này"""
    db = None
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        
        # Lấy ID của user trước
        cursor.execute("SELECT MaTaiKhoan FROM taikhoan WHERE TenDangNhap=%s", (username,))
        row = cursor.fetchone()
        if not row: return []
        uid = row['MaTaiKhoan']

        # Truy vấn lịch sử có tham gia của uid (là người 1 HOẶC người 2)
        sql = """
            SELECT 
                l.MaTranDau, 
                tk1.TenDangNhap as P1, 
                tk2.TenDangNhap as P2, 
                tk_win.TenDangNhap as Winner, 
                l.ThoiGianKetThuc as NgayGioKetThuc
            FROM lich_su_tran_dau l
            JOIN taikhoan tk1 ON l.MaNguoiChoi1 = tk1.MaTaiKhoan
            JOIN taikhoan tk2 ON l.MaNguoiChoi2 = tk2.MaTaiKhoan
            LEFT JOIN taikhoan tk_win ON l.NguoiThang = tk_win.MaTaiKhoan
            WHERE l.MaNguoiChoi1 = %s OR l.MaNguoiChoi2 = %s
            ORDER BY l.ThoiGianKetThuc DESC
        """
        cursor.execute(sql, (uid, uid))
        return cursor.fetchall()
    except Exception as e:
        print("Lỗi get_my_history:", e)
        return []
    finally:
        if db and db.is_connected(): db.close()