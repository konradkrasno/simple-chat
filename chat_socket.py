import socket
import threading

from typing import *


class Server:

    def __init__(self, host: str, port: int, debug: bool = False):
        self.host = host
        self.port = port
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._debug = debug
        self.stop_server: bool = False
        self.clients: Dict[str, socket.socket] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._s.close()

    def bind(self) -> None:
        self._s.bind((self.host, self.port))
        print(f"Socket binded to {self.port}")

    def listen(self) -> None:
        self._s.listen()
        print("Socket is listening...")

    def echo(self) -> None:
        while True:
            conn, addr = self._s.accept()
            if self.stop_server:
                break
            print(f"Got a connection from {addr!r}")
            thread = threading.Thread(target=self.handle, args=(conn,))
            thread.start()

    def handle(self, conn: socket.socket) -> None:
        nick = self.get_nick(conn)
        while not self.stop_server:
            try:
                self.receive_and_send(nick, conn)
            except OSError:
                pass
            except ConnectionAbortedError:
                self.clients.pop(nick)
                conn.close()
                break

    def get_nick(self, conn: socket.socket) -> str:
        conn.send(b"Connected to the server.\nGive your nick name: ")
        nick = self.save_nick(conn)
        conn.send(f"hello {nick}".encode('utf-8'))
        return nick

    def save_nick(self, conn: socket.socket) -> str:
        nick = conn.recv(1024).decode()
        self.clients[nick] = conn
        return nick

    def receive_and_send(self, nick: str, conn: socket.socket) -> None:
        message = self.receive_and_process(conn, nick)
        if not message:
            raise ConnectionAbortedError
        self.relay(message)

    def receive_and_process(self, conn: socket.socket, nick: str) -> Union[bytes, bool]:
        message = conn.recv(1024).decode()
        if self._debug and message == f"stop_server":
            self.stop_server = True
            self._close_all_conn()
            return False
        elif message == f"quit":
            self.clients.pop(nick)
            conn.close()
            message = f"{nick} left chat".encode('utf-8')
        else:
            message = self.add_nick_to_message(nick, message)
        return message

    def relay(self, message: bytes) -> None:
        for client in self.clients.values():
            client.send(message)

    def _close_all_conn(self) -> None:
        for conn in self.clients.values():
            conn.close()

    @staticmethod
    def add_nick_to_message(nick: str, message: str) -> bytes:
        return f"{nick}: {message}".encode('utf-8')


class Client:

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    def set_connection(self) -> socket.socket:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        return s

    def echo(self, conn: socket.socket) -> None:
        receive_thread = threading.Thread(target=self.receive, args=(conn,))
        receive_thread.start()
        write_thread = threading.Thread(target=self.relay, args=(conn,))
        write_thread.start()

    @staticmethod
    def receive(conn: socket.socket) -> None:
        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                if data:
                    print(data)
                else:
                    if conn:
                        conn.close()
                    break
            except OSError:
                conn.close()
                break

    @staticmethod
    def relay(conn: socket.socket, test_message: str = '') -> None:
        while True:
            try:
                if test_message:
                    message = test_message
                else:
                    message = f"{input()}"
                if not message:
                    message = f" "
                conn.send(message.encode('utf-8'))
            except OSError:
                conn.close()
                break

    @staticmethod
    def stop_server(conn: socket.socket) -> None:
        conn.send(b"stop_server")
