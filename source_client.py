import socket
import threading

from typing import *


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
            except (OSError, EOFError) as e:
                print("An error occurred:", e)
                print("Closing connection.")
                conn.close()
                break
            else:
                if data:
                    print(data)
                else:
                    conn.close()
                    break

    @staticmethod
    def relay(conn: socket.socket, test_message: str = '') -> None:
        while True:
            if test_message:
                message = test_message
            else:
                try:
                    message = f"{input()}"
                except KeyboardInterrupt:
                    conn.send(b"/quit")
                    conn.close()
                    break
            try:
                conn.sendall(message.encode('utf-8'))
            except (OSError, EOFError) as e:
                print("An error occurred:", e)
                print("Closing connection.")
                conn.close()
                break

    @staticmethod
    def stop_server(conn: socket.socket) -> None:
        conn.send(b"/stop_server")
