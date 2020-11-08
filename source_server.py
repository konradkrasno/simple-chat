import socket
import threading

from typing import *


class StopServerException(Exception):
    pass


class Server:

    def __init__(self, host: str, port: int, debug: bool = False):
        self.host = host
        self.port = port
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._debug = debug
        self._stop_server: bool = False
        self.clients: Dict[str, socket.socket] = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._s.close()

    def bind(self) -> None:
        self._s.bind((self.host, self.port))

    def listen(self) -> None:
        self._s.listen()
        print("Server is listening...")

    def echo(self) -> None:
        while True:
            conn, addr = self._s.accept()
            if self._stop_server:
                break
            print(f"Got a connection from {addr!r}")
            thread = threading.Thread(target=self.handle, args=(conn,))
            thread.start()

    def handle(self, conn: socket.socket) -> None:
        nick = self.get_nick(conn)
        while not self._stop_server:
            try:
                self.receive_and_send(conn, nick)
            except (OSError, EOFError) as e:
                print("An error occurred:", e)
                break
            except ConnectionResetError:
                conn.close()
            except StopServerException:
                break

    def get_nick(self, conn: socket.socket) -> str:
        while True:
            conn.send(b"Give your nickname: ")
            nick = self.save_nick(conn)
            if nick:
                conn.sendall(f"hello {nick}".encode('utf-8'))
                return nick

    def save_nick(self, conn: socket.socket) -> str:
        nick = conn.recv(1024).decode()
        if nick not in self.clients:
            self.clients[nick] = conn
            return nick
        return ""

    def receive_and_send(self, conn: socket.socket, nick: str, ) -> None:
        recipient, message = self.receive_and_process_message(conn, nick)
        if not message:
            raise StopServerException
        self.relay(nick, recipient, message)

    def receive_and_process_message(self, conn: socket.socket, nick: str) -> Union[Tuple[str, bytes], bool]:
        message = conn.recv(1024).decode()
        receiver, message = self.process_message(message, nick)
        try:
            message = self.message_manager[message](conn, nick)
        except KeyError:
            message = self.add_nick_to_message(message, nick)
        return receiver, message

    @staticmethod
    def process_message(message: str, sender: str) -> Tuple[str, str]:
        if message.startswith("@"):
            try:
                nick, message = message.split(" ", 1)
            except ValueError:
                return sender, f"Can't send message to receiver. Try again."
            return nick[1:], message
        else:
            return "", message

    @property
    def message_manager(self) -> Dict[str, callable]:
        manager = {
            f"/quit": self.close_connection,
            f"/stop_server": self.shut_down_server,
        }
        return manager

    def close_connection(self, conn: socket.socket, nick: str) -> bytes:
        self.clients.pop(nick)
        conn.close()
        return f"{nick} left chat".encode('utf-8')

    def shut_down_server(self, conn: socket.socket, nick: str) -> bool:
        if self._debug:
            self._stop_server = True
            self._close_all_conn()
            return False
        return True

    def _close_all_conn(self) -> None:
        for conn in self.clients.values():
            conn.close()

    @staticmethod
    def add_nick_to_message(message: str, nick: str) -> bytes:
        return f"{nick}: {message}".encode('utf-8')

    def relay(self, sender: str, recipient: str, message: bytes) -> None:
        if recipient:
            try:
                self.clients[recipient].sendall(message)
                self.clients[sender].sendall(message)
            except KeyError:
                self.clients[sender].sendall(f"No such user: {recipient}".encode('utf-8'))
        else:
            for client in self.clients.values():
                client.sendall(message)
