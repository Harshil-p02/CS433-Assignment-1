import socket
import codecs
import os


class Client:

    def __init__(self, server, port, username):
        self.server = server
        self.port = int(port)
        self.username = username
        self.header = 64
        self.format = 'utf-8'
        self.encryption = ""
        self.offset = 2
        self.word_size = 4

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server, self.port))
        print(">> Successfully connected with server!")

        self.send_msg(self.username, self.encryption)
        print("Select encryption from 0-2")
        print("\t 0 - plain text")
        print("\t 1 - caesar cipher")
        print("\t 2 - transpose")
        while True:
            enc = input()
            if enc == '0':
                self.encryption = "None"
                break
            elif enc == '1':
                self.encryption = "caesar"
                break
            elif enc == '2':
                self.encryption = "transpose"
                break
            else:
                print("Enter valid value")
        self.send_msg(self.encryption, "None")
        print(f"Encrypting messages using {self.encryption}")

        print("type ? for help")

        while True:
            print(">> ", end="")
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
                status = self.recv_msg(self.encryption)
                print(status)
                if status == "OK":
                    if self.recv_msg(mode) == "BEGIN_DWD":
                        with open(file, "w") as f:
                            while True:
                                msg = self.recv_msg(mode)
                                if msg != "END_DWD":
                                    f.write(msg)
                                else:
                                    break
                    print(self.recv_msg(self.encryption))

            elif cmd[:3] == "upd":
                _, file = cmd.split()
                self.send_msg(cmd, self.encryption)
                mode = self.encryption
                if mode == "caesar" and not self.is_utf8(file):
                    mode = "None"

                self.send_msg(mode, self.encryption)
                if not os.path.isfile(file):
                    print("FILE NOT PRESENT")
                    self.send_msg("NOK", self.encryption)
                else:
                    self.send_msg("OK", self.encryption)
                    self.send_msg("BEGIN_UPD", mode)
                    with open(file, "r") as f:
                        data = f.read(4096)
                        while data:
                            self.send_msg(data, mode)
                            data = f.read(4096)
                    self.send_msg("END_UPD", mode)
                    print(self.recv_msg(self.encryption))

            elif cmd[:2] == "cd":
                self.send_msg(cmd, self.encryption)
                status = self.recv_msg(self.encryption)
                msg = self.recv_msg(self.encryption)
                if status != "OK":
                    print("Error in changing directory")
                print(msg)

            else:
                self.send_msg(cmd, self.encryption)
                msg = self.recv_msg(self.encryption)
                if msg is None:
                    break

                print(msg)

    def send_msg(self, msg, mode):
        msg = self.encrypt_msg(msg, mode)
        msg_len = len(msg)
        send_msg_len = str(msg_len).encode(self.format)
        send_msg_len += b" " * (self.header - len(send_msg_len))
        self.client.send(send_msg_len)
        self.client.send(msg.encode(self.format))

    def recv_msg(self, mode):
        msg_len = self.client.recv(self.header).decode(self.format)
        if not msg_len:
            return None
        msg = self.client.recv(int(msg_len)).decode(self.format)
        msg = self.decrypt_msg(msg, mode)

        return msg

    def encrypt_msg(self, msg, mode):
        if mode == "None":
            return msg

        encrypted_msg = ""
        if mode == "caesar":
            for i in msg:
                encrypted_msg += chr(ord(i) + self.offset)

        if mode == "transpose":
            i = 0
            while i < len(msg):
                encrypted_msg += self.reverse(msg[i:min(i + self.word_size, len(msg))])
                i += self.word_size

        return encrypted_msg

    def decrypt_msg(self, msg, mode):
        if mode == "None":
            return msg

        decrypted_msg = ""
        if mode == "caesar":
            for i in msg:
                decrypted_msg += chr(ord(i) - self.offset)

        if mode == "transpose":
            i = 0
            while i < len(msg):
                decrypted_msg += self.reverse(msg[i:min(i + self.word_size, len(msg))])
                i += self.word_size

        return decrypted_msg

    def is_utf8(self, file):
        try:
            codecs.open(file, encoding="utf-8", errors="strict").readlines()
            return True
        except:
            return False

    def reverse(self, x):
        return x[::-1]


ip = "10.0.2.15"
port = 5555
c = Client(ip, port, "test_user")