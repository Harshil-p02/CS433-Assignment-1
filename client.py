import socket


class Client:

    def __init__(self, server, port, username):
        self.server = server
        self.port = int(port)
        self.username = username
        self.header = 64
        self.format = 'utf-8'

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.server, self.port))
        print("> Successfully connected with server!")

        self.send_msg(self.username)

        while True:
            print("> ", end="")
            cmd = input()
            if cmd == "!q":
                self.client.close()
                break
            self.send_msg(cmd)
            msg = self.recv_msg()
            if msg is None:
                break

            print(msg)

    def send_msg(self, msg):
        # what if msg length is greater than header (msg > 64 bytes)
        # break msg into multiple pieces

        msg = self.encrypt_msg(msg, "transpose")
        msg_len = len(msg)
        send_msg_len = str(msg_len).encode(self.format)
        send_msg_len += b" " * (self.header - len(send_msg_len))
        self.client.send(send_msg_len)
        self.client.send(msg.encode(self.format))

    def recv_msg(self):
        msg_len = self.client.recv(self.header).decode(self.format)
        if not msg_len:
            return None
        msg = self.client.recv(int(msg_len)).decode(self.format)
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


ip = "10.0.2.15"
port = 5555
c = Client(ip, port, "test_user")