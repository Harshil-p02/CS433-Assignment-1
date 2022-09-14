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
        print("Successfully connected with server!")

        self.send_msg(self.username)
        self.send_msg("cwd")

    def send_msg(self, msg):
        # what if msg length is greater than header (msg > 64 bytes)
        # break msg into multiple pieces

        msg = self.encrypt_msg(msg, "caesar")
        msg_len = len(msg)
        send_msg_len = str(msg_len).encode(self.format)
        send_msg_len += b" " * (self.header - len(send_msg_len))
        self.client.send(send_msg_len)
        self.client.send(msg.encode(self.format))

    def recv_msg(self):
        msg_len = self.client.recv(self.header).decode(self.format)
        msg = self.client.recv(int(msg_len)).decode(self.format)
        msg = self.decrypt_msg(msg, "caesar")
        print(f"message received from server -> {msg}")

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
c = Client(ip, port, "test_user")