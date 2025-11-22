# db.py
import mysql.connector
from datetime import datetime
import hashlib

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="battleshipdb"
    )


# ===================== HASH PASSWORD =====================
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


# ===================== REGISTER USER =====================
def register_user(username, password):
    try:
        db = get_connection()
        cursor = db.cursor()

        # Kiểm tra tài khoản đã tồn tại chưa
        cursor.execute("SELECT * FROM taikhoan WHERE TenDangNhap = %s", (username,))
        if cursor.fetchone():
            return False, "Tài khoản đã tồn tại!"

        hashed_pw = hash_password(password)

        sql = """
        INSERT INTO taikhoan (TenDangNhap, MatKhau, SoTranThang, SoTranThua, NgayTao)
        VALUES (%s, %s, 0, 0, %s)
        """
        cursor.execute(sql, (username, hashed_pw, datetime.now()))
        db.commit()

        return True, "Đăng ký thành công!"

    except Exception as e:
        return False, str(e)

    finally:
        if db.is_connected():
            cursor.close()
            db.close()


# ===================== LOGIN USER =====================
def login_user(username, password):
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
            return True, user
        else:
            return False, "Sai tài khoản hoặc mật khẩu!"

    except Exception as e:
        return False, str(e)

    finally:
        if db.is_connected():
            cursor.close()
            db.close()


# ===================== LOGIN ADMIN =====================
def login_admin(username, password):
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        hashed_pw = hash_password(password)

        sql = """
        SELECT * FROM quanli 
        WHERE ten_dang_nhap = %s AND mat_khau = %s
        """
        cursor.execute(sql, (username, hashed_pw))
        admin = cursor.fetchone()

        if admin:
            return True, admin
        else:
            return False, "Sai tài khoản quản trị!"

    except Exception as e:
        return False, str(e)

    finally:
        if db.is_connected():
            cursor.close()
            db.close()
