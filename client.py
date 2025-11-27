import socket
import threading
import json
import tkinter as tk

class Client:
    def __init__(self):
        self.sock = socket.socket()
        self.handlers = {}
        self.username = None
        self.running = True

    def connect(self, host, port):
        try:
            self.sock.connect((host, port))
            threading.Thread(target=self._listen, daemon=True).start()
            return True
        except:
            return False

    def on(self, event, func):
        self.handlers[event] = func

    def send(self, data):
        try:
            self.sock.sendall((json.dumps(data) + "\n").encode())
        except:
            pass

    def set_name(self, username):
        self.username = username
        self.send({
            "type": "SET_NAME",
            "name": username
        })

    def _listen(self):
        buf = ""
        while self.running:
            try:
                d = self.sock.recv(4096)
                if not d:
                    break

                buf += d.decode()

                while "\n" in buf:
                    raw, buf = buf.split("\n", 1)
                    if not raw.strip(): continue
                    
                    try:
                        msg = json.loads(raw)
                        t = msg["type"]
                        
                        if t in self.handlers:
                            handler = self.handlers[t]
                            # Kiểm tra xem widget còn tồn tại không trước khi gọi
                            # handler.__self__ chính là cái màn hình (Lobby, Admin...)
                            if hasattr(handler, "__self__"):
                                widget = handler.__self__
                                try:
                                    # Kiểm tra widget còn sống không (tránh lỗi TclError)
                                    if widget.winfo_exists(): 
                                        widget.after(0, handler, msg)
                                except:
                                    pass # Widget đã chết, bỏ qua tin nhắn này
                    except json.JSONDecodeError:
                        pass
                    except Exception as e:
                        print(f"Error processing message: {e}")

            except ConnectionResetError:
                break
            except Exception as e:
                print(f"Socket error: {e}")
                break