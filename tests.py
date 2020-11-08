import pytest
import socket
import threading
import time

from typing import *
from source_server import Server
from source_client import Client
from server import start_server

HOST = '127.0.0.1'
PORT = 12345


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
        assert conn.recv(1024) == b"Give your nickname: "
        conn.send(f"{user}".encode('utf-8'))
        assert conn.recv(1024) == f"hello {user}".encode('utf-8')

    # conversation
    for user, conn in connections.items():
        conn.send(b"what's up?")
        for c in connections.values():
            assert c.recv(1024) == f"{user}: what's up?".encode('utf-8')

    for sender, conn in connections.items():
        for recipient, c in connections.items():
            conn.send(f"@{recipient} hello {recipient}".encode('utf-8'))
            assert conn.recv(2024) == f"{sender}: hello {recipient}".encode('utf-8')
            assert c.recv(1024) == f"{sender}: hello {recipient}".encode('utf-8')

    # stop server
    client.stop_server(connections["Freddie"])
    client.set_connection()


def test_process_message_when_valid():
    server = Server(HOST, PORT)
    nick, message = server.process_message(f"@Jim how are you?", "Freddy")
    assert nick == f"Jim"
    assert message == f"how are you?"


def test_process_message_when_invalid():
    server = Server(HOST, PORT)
    nick, message = server.process_message(f"@Jim", "Freddy")
    assert nick == f"Freddy"
    assert message == f"Can't send message to receiver. Wrong syntax."


def test_process_message_when_no_user():
    server = Server(HOST, PORT)
    nick, message = server.process_message(f"hello everyone", "Freddy")
    assert nick == f""
    assert message == f"hello everyone"
