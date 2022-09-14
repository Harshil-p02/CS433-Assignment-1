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

        msg_len = len(msg)
        send_msg_len = str(msg_len).encode(self.format)
        send_msg_len += b" " * (self.header - len(send_msg_len))
        self.client.send(send_msg_len)
        self.client.send(msg.encode(self.format))

    def recv_msg(self):
        msg_len = self.client.recv(self.header).decode(self.format)
        msg = self.client.recv(int(msg_len)).decode(self.format)
        print(f"message received from server -> {msg}")

    def encrypt_msg(self):
        pass

    def decrypt_msg(self):
        pass


ip =
port =
c = Client(ip, port, "test_user")