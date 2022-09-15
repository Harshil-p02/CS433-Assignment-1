import socket
import codecs
import time


class Client:

    def __init__(self, server, port, username):
        self.server = server
        self.port = int(port)
        self.username = username
        self.header = 64
        self.format = 'utf-8'
        self.encryption = "None"
        self.offset = 2
        self.word_size = 4

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server, self.port))
        print("> Successfully connected with server!")

        self.send_msg(self.username, self.encryption)

        while True:
            print("> ", end="")
            cmd = input()
            cmd = cmd.strip()
            if cmd == "!q":
                print("Exiting...")
                self.client.close()
                break
            elif cmd[:3] == "dwd":
                _, file = cmd.split()
                self.send_msg(cmd, self.encryption)
                mode = self.recv_msg(self.encryption)
                if self.recv_msg(mode) == "BEGIN_DWD":
                    with open(file, "wb") as f:
                        while True:
                            msg = self.recv_msg(mode, decode=False)
                            if msg != bytes("END_DWD", self.format):
                                f.write(msg)
                            else:
                                break
                print(self.recv_msg(self.encryption))

            elif cmd[:3] == "upd":
                _, file = cmd.split()
                self.send_msg(cmd, self.encryption)
                time.sleep(1)
                mode = self.encryption
                if mode == "caesar" and not self.is_utf8(file):
                    mode = "None"

                self.send_msg(mode, self.encryption)
                time.sleep(1)
                self.send_msg("BEGIN_UPD", mode)
                time.sleep(1)
                with open(file, "rb") as f:
                    data = f.read(4096)
                    while data:
                        self.send_msg(data, mode, encode=False)
                        data = f.read(4096)
                self.send_msg("END_UPD", mode)
                print(self.recv_msg(self.encryption))

            else:
                self.send_msg(cmd, self.encryption)
                msg = self.recv_msg(self.encryption)
                if msg is None:
                    break

                print(msg)

    def send_msg(self, msg, mode, encode=True):
        # what if msg length is greater than header (msg > 64 bytes)
        # break msg into multiple pieces

        msg = self.encrypt_msg(msg, mode)
        msg_len = len(msg)
        send_msg_len = str(msg_len).encode(self.format)
        send_msg_len += b" " * (self.header - len(send_msg_len))
        self.client.send(send_msg_len)
        if encode:
            self.client.send(msg.encode(self.format))
        else:
            self.client.send(msg)

    def recv_msg(self, mode, decode=True):
        msg_len = self.client.recv(self.header).decode(self.format)
        if not msg_len:
            return None
        if decode:
            msg = self.client.recv(int(msg_len)).decode(self.format)
        else:
            msg = self.client.recv(int(msg_len))
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
c = Client(ip, port, "test_user")