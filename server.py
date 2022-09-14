import socket
import subprocess


class Server:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.format = 'utf-8'
        self.header = 64

        self.users = {}
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind((self.ip, self.port))

        # while True:
        self.start()

    def start(self):
        self.soc.listen()
        conn, addr = self.soc.accept()

        while True:
            msg_len = conn.recv(self.header).decode(self.format)
            if not msg_len:
                break
            msg = conn.recv(int(msg_len)).decode(self.format)

            print(f"message received from client {conn} -> {msg}")

            if msg == "cwd":
                proc = subprocess.run("pwd", capture_output=True)
                if proc.returncode:
                    exit(1)
                self.send_msg(proc.stdout.decode(), conn)

            elif msg == "ls":
                proc = subprocess.run("ls", capture_output=True)
                if proc.returncode:
                    exit(1)
                self.send_msg(proc.stdout.decode(), conn)

            elif msg[:2] == "cd":
                cmd = msg.split()
                proc = subprocess.run(cmd, capture_output=True)
                if proc.returncode:
                    exit(1)
                self.send_msg(proc.stdout.decode(), conn)

    def send_msg(self, msg, soc):
        msg = self.encrypt_msg(msg, "caesar")
        msg_len = len(msg)
        send_msg_len = str(msg_len).encode(self.format)
        send_msg_len += b" " * (self.header - len(send_msg_len))
        soc.send(send_msg_len)
        soc.send(msg.encode(self.format))

    def recv_msg(self, soc):
        msg_len = soc.recv(self.header).decode(self.format)
        msg = soc.recv(int(msg_len)).decode(self.format)
        msg = self.decrypt_msg(msg, "caesar")

        return msg

    def encrypt_msg(self, msg, mode=None, offset=2):
        if mode is None:
            return msg

        if mode == "caesar":
            for i in range(len(msg)):
                msg[i] = chr(ord(msg[i]) + offset)

        if mode == "transpose":
            msg = msg[::-1]

        return msg

    def decrypt_msg(self, msg, mode=None, offset=2):
        if mode is None:
            return msg

        if mode == "caesar":
            for i in range(len(msg)):
                msg[i] = msg[i] - offset

        if mode == "transpose":
            msg = msg[::-1]

        return msg


ip =
port =
s = Server(ip, port)