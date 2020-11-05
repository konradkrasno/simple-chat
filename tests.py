import pytest
import socket
import threading
import time

from typing import *
from chat_socket import Client
from server import start_server, HOST, PORT


@pytest.fixture
def server() -> None:
    thread = threading.Thread(target=start_server, args=(HOST, PORT, True,))
    thread.start()
    time.sleep(0.00001)


def test_server(server: pytest.fixture) -> None:
    users: List[str] = ["Freddie", "Jim", "Mick"]
    connections: Dict[str, socket.socket] = {}
    client = Client(HOST, PORT)
    for user in users:
        conn = client.set_connection()
        connections[user] = conn

    # greeting
    for user, conn in connections.items():
        assert conn.recv(1024) == b"Connected to the server.\nGive your nick name: "
        conn.send(f"{user}".encode('utf-8'))
        assert conn.recv(1024) == f"hello {user}".encode('utf-8')

    # conversation
    for user, conn in connections.items():
        conn.send(b"what's up?")
        for c in connections.values():
            assert c.recv(1024) == f"{user}: what's up?".encode('utf-8')

    # stop server
    client.stop_server(connections["Freddie"])
    client.set_connection()
