import socket
import threading
import json


class Client:
    def __init__(self):
        self.sock = socket.socket()
        self.handlers = {}
        self.username = None

    def connect(self, host, port):
        self.sock.connect((host, port))
        threading.Thread(target=self._listen, daemon=True).start()

    def on(self, event, func):
        self.handlers[event] = func

    def send(self, data):
        self.sock.sendall((json.dumps(data) + "\n").encode())

    def set_name(self, username):
        """Gửi tên thật (từ CSDL) lên server"""
        self.username = username
        self.send({
            "type": "SET_NAME",
            "name": username
        })

    def _listen(self):
        buf = ""

        while True:
            try:
                d = self.sock.recv(4096)
                if not d:
                    break

                buf += d.decode()

                while "\n" in buf:
                    raw, buf = buf.split("\n", 1)
                    msg = json.loads(raw)

                    t = msg["type"]

                    if t in self.handlers:
                        handler = self.handlers[t]

                        # Đưa về main-thread của Tkinter
                        handler.__self__.after(0, handler, msg)

            except:
                break
