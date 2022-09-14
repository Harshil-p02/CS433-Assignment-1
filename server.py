import socket
import subprocess
import os


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
            msg = self.recv_msg(conn)
            if msg is None:
                break

            print(f"message received from client {conn} -> {msg}")

            if msg == "cwd":
                proc = os.getcwd()
                self.send_msg(proc, conn)

            elif msg == "ls":
                proc = subprocess.run(["ls", "-l"], capture_output=True, text=True)
                if proc.returncode:
                    exit(1)
                self.send_msg(proc.stdout, conn)

            elif msg[:2] == "cd":
                cmd = msg.split()
                try:
                    os.chdir(cmd[1])
                except:
                    pass
                self.send_msg(os.getcwd(), conn)

            elif msg[:3] == "dwd":
                _, file = msg.split()
                self.send_msg("BEGIN_DWD", conn)
                with open(file, "r") as f:
                    data = f.read(4096)
                    while data:
                        self.send_msg(data, conn)
                        data = f.read(4096)
                self.send_msg("END_DWD", conn)
                self.send_msg(f"Download of {file} completed", conn)

            elif msg[:3] == "upd":
                _, file = msg.split()
                if self.recv_msg(conn) == "BEGIN_UPD":
                    with open(file, "w") as f:
                        while True:
                            data = self.recv_msg(conn)
                            if data == "END_UPD":
                                break
                            f.write(data)
                self.send_msg(f"Upload of {file} completed", conn)


    def send_msg(self, msg, soc):
        msg = self.encrypt_msg(msg, "transpose")
        msg_len = len(msg)
        send_msg_len = str(msg_len).encode(self.format)
        send_msg_len += b" " * (self.header - len(send_msg_len))
        soc.send(send_msg_len)
        soc.send(msg.encode(self.format))

    def recv_msg(self, soc):
        msg_len = soc.recv(self.header).decode(self.format)
        if not msg_len:
            return None
        msg = soc.recv(int(msg_len)).decode(self.format)
        msg = self.decrypt_msg(msg, "transpose")

        return msg

    def encrypt_msg(self, msg, mode=None, offset=2):
        if mode is None:
            return msg

        encrypted_msg = ""
        if mode == "caesar":
            for i in msg:
                encrypted_msg += chr(ord(i) + offset)

        if mode == "transpose":
            encrypted_msg = msg[::-1]

        return encrypted_msg

    def decrypt_msg(self, msg, mode=None, offset=2):
        if mode is None:
            return msg

        decrypted_msg = ""
        if mode == "caesar":
            for i in msg:
                decrypted_msg += chr(ord(i) - offset)

        if mode == "transpose":
            decrypted_msg = msg[::-1]

        return decrypted_msg


ip = "192.168.56.1"
port = 5555
s = Server(ip, port)