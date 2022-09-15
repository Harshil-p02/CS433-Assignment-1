import socket
import subprocess
import os
import codecs


class Server:

    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.format = 'utf-8'
        self.header = 64
        self.encryption = "None"
        self.offset = 2
        self.word_size = 4

        self.users = {}
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind((self.ip, self.port))

        # while True:
        self.start()

    def start(self):
        self.soc.listen()
        conn, addr = self.soc.accept()

        username = self.recv_msg(self.encryption, conn)
        while True:
            msg = self.recv_msg(self.encryption, conn)
            if msg is None:
                break

            print(f"message received from client {conn} -> {msg}")

            if msg == "cwd":
                proc = os.getcwd()
                self.send_msg(proc, self.encryption, conn)

            elif msg == "ls":
                proc = subprocess.run(["ls", "-l"], capture_output=True, text=True)
                if proc.returncode:
                    exit(1)
                self.send_msg(proc.stdout, self.encryption, conn)

            elif msg[:2] == "cd":
                cmd = msg.split()
                try:
                    os.chdir(cmd[1])
                except:
                    pass
                self.send_msg(os.getcwd(), self.encryption, conn)

            elif msg[:3] == "dwd":
                _, file = msg.split()
                mode = self.encryption
                if mode == "caesar" and not self.is_utf8(file):
                    mode = "None"
                self.send_msg(mode, self.encryption, conn)
                self.send_msg("BEGIN_DWD", mode, conn)
                with open(file, "rb") as f:
                    data = f.read(4096)
                    while data:
                        self.send_msg(data, mode, conn, encode=False)
                        data = f.read(4096)
                self.send_msg("END_DWD", mode, conn)

                self.send_msg(f"Download of {file} completed", self.encryption, conn)

            elif msg[:3] == "upd":
                _, file = msg.split()
                mode = self.recv_msg(self.encryption, conn)
                if self.recv_msg(mode, conn) == "BEGIN_UPD":
                    with open(file, "wb") as f:
                        while True:
                            data = self.recv_msg(mode, conn, decode=False)
                            if data != bytes("END_UPD", self.format):
                                f.write(data)
                            else:
                                break

                self.send_msg(f"Upload of {file} completed", self.encryption, conn)

            else:
                self.send_msg("Error - Incorrect command", self.encryption, conn)


    def send_msg(self, msg, mode, soc, encode=True):
        msg = self.encrypt_msg(msg, mode)
        msg_len = len(msg)
        send_msg_len = str(msg_len).encode(self.format)
        send_msg_len += b" " * (self.header - len(send_msg_len))
        soc.send(send_msg_len)
        if encode:
            soc.send(msg.encode(self.format))
        else:
            soc.send(msg)

    def recv_msg(self, mode, soc, decode=True):
        msg_len = soc.recv(self.header).decode(self.format)
        if not msg_len:
            return None
        if decode:
            msg = soc.recv(int(msg_len)).decode(self.format)
        else:
            msg = soc.recv(int(msg_len))
        msg = self.decrypt_msg(msg, mode)

        return msg

    def encrypt_msg(self, msg, mode, offset=2):
        if mode == "None":
            return msg

        encrypted_msg = ""
        if mode == "caesar":
            for i in msg:
                encrypted_msg += chr(ord(i) + offset)

        if mode == "transpose":
            encrypted_msg = msg[::-1]

        return encrypted_msg

    def decrypt_msg(self, msg, mode, offset=2):
        if mode == "None":
            return msg

        decrypted_msg = ""
        if mode == "caesar":
            for i in msg:
                decrypted_msg += chr(ord(i) - offset)

        if mode == "transpose":
            decrypted_msg = msg[::-1]

        return decrypted_msg

    def is_utf8(self, file):
        try:
            codecs.open(file, encoding="utf-8", errors="strict").readlines()
            return True
        except:
            return False


ip = "192.168.56.1"
port = 5555
s = Server(ip, port)