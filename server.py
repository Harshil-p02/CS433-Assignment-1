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
            # msg = self.recv_msg(conn)
            msg_len = conn.recv(self.header).decode(self.format)
            if not msg_len:
                break
            msg = conn.recv(int(msg_len)).decode(self.format)

            if not msg:
                break
            print(f"message received from client {conn} -> {msg}")
            # msg = conn.recv(self.header).decode(self.format)
            if msg == "cwd":
                proc = subprocess.run(msg, capture_output=True)
                if proc.returncode:
                    exit(1)
                print(proc.stdout)

    def send_msg(self, msg, soc):
        msg_len = len(msg)
        send_msg_len = str(msg_len).encode(self.format)
        send_msg_len += b" " * (self.header - len(send_msg_len))
        soc.send(send_msg_len)
        soc.send(msg.encode(self.format))

    def recv_msg(self, soc):
        msg_len = soc.recv(self.header).decode(self.format)
        # print(msg_len)
        # exit(1)
        msg = soc.recv(int(msg_len)).decode(self.format)
        return msg


ip =
port =
s = Server(ip, port)