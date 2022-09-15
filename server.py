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
        self.encryption = ""
        self.offset = 2
        self.word_size = 4

        self.users = {}
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind((self.ip, self.port))

        self.start()

    def start(self):
        self.soc.listen()
        conn, addr = self.soc.accept()

        username = self.recv_msg(self.encryption, conn)
        self.encryption = self.recv_msg("None", conn)
        print(f"using {self.encryption}")
        while True:
            msg = self.recv_msg(self.encryption, conn)
            if msg is None:
                break

            print(f"message received from client {conn} -> {msg}")

            if msg == "?":
                out = """
cwd \t\t-\t prints current working directory
ls \t\t-\t list all files and folders in the current directory
cd <dir> \t-\t change directory
dwd <file> \t-\t download <file> from server
upd <file> \t-\t upload <file> to server
!q \t\t-\t exit
? \t\t-\t shows this message
                """
                self.send_msg(out, self.encryption, conn)
            elif msg == "cwd":
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
                    self.send_msg("OK", self.encryption, conn)
                except:
                    self.send_msg("NOK", self.encryption, conn)
                self.send_msg(os.getcwd(), self.encryption, conn)

            elif msg[:3] == "dwd":
                _, file = msg.split()
                mode = self.encryption
                if mode == "caesar" and not self.is_utf8(file):
                    mode = "None"
                self.send_msg(mode, self.encryption, conn)
                if not os.path.isfile(file):
                    self.send_msg("NOK", self.encryption, conn)
                else:
                    self.send_msg("OK", self.encryption, conn)
                    self.send_msg("BEGIN_DWD", mode, conn)
                    with open(file, "r") as f:
                        data = f.read(4096)
                        while data:
                            self.send_msg(data, mode, conn)
                            data = f.read(4096)
                    self.send_msg("END_DWD", mode, conn)

                    self.send_msg(f"Download of {file} completed", self.encryption, conn)

            elif msg[:3] == "upd":
                _, file = msg.split()
                file = file.split("/")[-1]
                mode = self.recv_msg(self.encryption, conn)
                status = self.recv_msg(self.encryption, conn)
                if status == "OK":
                    if self.recv_msg(mode, conn) == "BEGIN_UPD":
                        with open(file, "w") as f:
                            print("file created")
                            while True:
                                data = self.recv_msg(mode, conn)
                                if data != "END_UPD":
                                    f.write(data)
                                else:
                                    break
                    self.send_msg(f"Upload of {file} completed", self.encryption, conn)

            else:
                self.send_msg("Error - Incorrect command", self.encryption, conn)

    def send_msg(self, msg, mode, soc):
        msg = self.encrypt_msg(msg, mode)
        msg_len = len(msg)
        send_msg_len = str(msg_len).encode(self.format)
        send_msg_len += b" " * (self.header - len(send_msg_len))
        soc.send(send_msg_len)
        soc.send(msg.encode(self.format))

    def recv_msg(self, mode, soc):
        msg_len = soc.recv(self.header).decode(self.format)
        if not msg_len:
            return None
        msg = soc.recv(int(msg_len)).decode(self.format)
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
s = Server(ip, port)